import os
import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, Response, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import storage
import pdf_generator

app = FastAPI(
    title="Sistema de Cotizaciones de Software",
    description="Plataforma comercial para generación, gestión y visualización de propuestas de software con exportación a PDF",
    version="2.0.0"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# Montar estáticos y plantillas
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.filters["plan_items"] = storage.plan_items

# ==========================================
# CONFIGURACIÓN DE SEGURIDAD & AUTENTICACIÓN
# ==========================================
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
SECRET_KEY = os.environ.get("SECRET_KEY", "barcam_myfinces_secret_key_2026_xyz")
COOKIE_NAME = "admin_session_token"

def create_session_token(username: str) -> str:
    """Genera un token seguro firmado con HMAC."""
    sig = hmac.new(SECRET_KEY.encode(), username.encode(), hashlib.sha256).hexdigest()
    return f"{username}:{sig}"

def verify_session_token(token: str) -> bool:
    """Valida la autenticidad del token de sesión administrativa."""
    if not token or ":" not in token:
        return False
    try:
        username, sig = token.split(":", 1)
        expected_sig = hmac.new(SECRET_KEY.encode(), username.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected_sig) and username == ADMIN_USERNAME
    except Exception:
        return False

def is_admin_authenticated(request: Request) -> bool:
    """Verifica si la petición proviene de un administrador autenticado."""
    token = request.cookies.get(COOKIE_NAME)
    return verify_session_token(token)


# ==========================================
# RUTAS DE AUTENTICACIÓN (LOGIN / LOGOUT)
# ==========================================

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/"):
    """Página de acceso para administradores."""
    if is_admin_authenticated(request):
        return RedirectResponse(url=next if next.startswith("/") else "/", status_code=303)
    
    return templates.TemplateResponse(request, "login.html", {
        "next_url": next,
        "error": None
    })


@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request):
    """Procesa las credenciales enviadas por el formulario de inicio de sesión."""
    form_data = await request.form()
    username = form_data.get("username", "").strip()
    password = form_data.get("password", "").strip()
    next_url = form_data.get("next", "/")
    if not next_url.startswith("/"):
        next_url = "/"

    if hmac.compare_digest(username, ADMIN_USERNAME) and hmac.compare_digest(password, ADMIN_PASSWORD):
        token = create_session_token(username)
        response = RedirectResponse(url=next_url, status_code=303)
        response.set_cookie(
            key=COOKIE_NAME,
            value=token,
            max_age=86400 * 30,  # 30 días de vigencia
            httponly=True,
            samesite="lax"
        )
        return response

    return templates.TemplateResponse(request, "login.html", {
        "next_url": next_url,
        "error": "Credenciales inválidas. Verifica tu usuario y contraseña de administrador."
    }, status_code=401)


@app.get("/logout")
async def logout():
    """Cierra la sesión administrativa."""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response


# ==========================================
# RUTAS DE INTERFAZ WEB (ADMIN PROTEGIDO)
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, id: str = ""):
    """Panel de administración y creación de cotizaciones (SOLO ADMINS)."""
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/login?next=/", status_code=303)

    # Abrir la cotización pedida (?id=...) o la más reciente
    quotes = storage.list_quotations()
    initial_data = storage.get_quotation(id) if id else None
    if not initial_data:
        initial_data = storage.get_quotation(quotes[0]["id"]) if quotes else storage.DEFAULT_PROPOSAL
    
    return templates.TemplateResponse(request, "admin.html", {
        "initial_data": initial_data,
        "quotes_list": quotes,
        "admin_user": ADMIN_USERNAME
    })


@app.get("/admin", response_class=HTMLResponse)
async def admin_alias(request: Request):
    return RedirectResponse(url="/")


# ==========================================
# PORTAL DEL CLIENTE (100% PÚBLICO - SIN RESTRICCIÓN)
# ==========================================

@app.get("/cotizacion/{quote_id}", response_class=HTMLResponse)
async def client_view(request: Request, quote_id: str):
    """
    Portal web público para que el cliente visualice su propuesta interactiva.
    NO REQUIERE LOGIN NI CONTRASEÑA para permitir fácil acceso al cliente.
    """
    data = storage.get_quotation(quote_id)
    if not data:
        raise HTTPException(status_code=404, detail=f"Cotización {quote_id} no encontrada")
    
    return templates.TemplateResponse(request, "client_view.html", {
        "data": data
    })


# ==========================================
# RUTAS DE API REST & PDF
# ==========================================

@app.get("/api/preset")
async def get_preset():
    """Retorna los datos predeterminados de MyFinces."""
    return storage.DEFAULT_PROPOSAL


@app.get("/api/cotizaciones")
async def list_all_quotes(request: Request):
    """Listado de cotizaciones guardadas (requiere admin)."""
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=401, detail="No autorizado")
    return storage.list_quotations()


@app.get("/api/cotizaciones/nueva")
async def new_quote_template(request: Request):
    """Plantilla para una cotización nueva, con el siguiente número disponible (requiere admin)."""
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=401, detail="No autorizado")
    import copy
    from datetime import datetime
    data = copy.deepcopy(storage.DEFAULT_PROPOSAL)
    data.update({
        "quote_number": storage.next_quote_number(),
        "quote_date": datetime.today().strftime("%d/%m/%Y"),
        "client_name": "",
        "client_company": "",
        "client_contact": "",
    })
    data.pop("selected_plan_index", None)
    return data


@app.delete("/api/cotizaciones/{quote_id}")
async def delete_quote(request: Request, quote_id: str):
    """Elimina una cotización (requiere admin)."""
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=401, detail="No autorizado")
    if not storage.delete_quotation(quote_id):
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return {"status": "ok"}


@app.get("/api/cotizaciones/{quote_id}")
async def get_quote_data(quote_id: str):
    """Datos en formato JSON de una cotización específica."""
    data = storage.get_quotation(quote_id)
    if not data:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return data


@app.post("/api/cotizaciones")
async def save_quote(request: Request, payload: dict):
    """
    Crea o actualiza una propuesta comercial.
    PROTEGIDO: Solo los administradores pueden guardar o editar cotizaciones.
    """
    if not is_admin_authenticated(request):
        raise HTTPException(
            status_code=401,
            detail="Acceso restringido: Debes iniciar sesión como administrador para guardar o modificar cotizaciones."
        )

    plans = payload.get("plans") or []
    if not plans:
        raise HTTPException(status_code=400, detail="La cotización debe tener al menos 1 plan.")
    # original_id: número con el que se abrió la cotización en el panel ("" si es nueva)
    original_id = str(payload.pop("original_id", "") or "").strip()
    quote_number = str(payload.get("quote_number", "") or "").strip()
    payload["quote_number"] = quote_number
    is_rename = bool(original_id) and quote_number and quote_number.upper() != original_id.upper()

    # Evitar sobrescribir otra cotización por usar un número que ya existe
    if quote_number and storage.quotation_exists(quote_number) and (not original_id or is_rename):
        raise HTTPException(
            status_code=409,
            detail=f"Ya existe una cotización con el número {quote_number}. Usa otro número o ábrela desde el listado para editarla."
        )

    # El plan seleccionado lo elige el cliente en su vista; el admin no lo define.
    # Se conserva la elección previa del cliente; si no hay, se usa el plan recomendado (o el primero).
    existing = storage.get_quotation(original_id or quote_number or "") or {}
    sel = existing.get("selected_plan_index")
    if not isinstance(sel, int) or not 0 <= sel < len(plans):
        sel = next((i for i, p in enumerate(plans) if p.get("is_recommended")), 0)
    payload["selected_plan_index"] = sel

    if is_rename and storage.quotation_exists(original_id):
        quote_id = storage.rename_quotation(original_id, payload)
    else:
        quote_id = storage.save_quotation(payload)
    return {
        "status": "ok",
        "quote_id": quote_id,
        "message": f"Cotización {quote_id} guardada correctamente"
    }


@app.post("/api/cotizaciones/{quote_id}/select-plan")
async def select_plan(quote_id: str, payload: dict):
    """
    PÚBLICO: Permite al cliente seleccionar su plan preferido sin requerir login.
    """
    try:
        plan_index = int(payload.get("plan_index", 0))
    except (TypeError, ValueError):
        plan_index = -1
    result = storage.set_selected_plan(quote_id, plan_index)
    if result is None:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    if result:
        return {"status": "ok", "selected_plan_index": plan_index}
    return {"status": "error", "message": "Índice de plan inválido"}


@app.get("/api/cotizaciones/{quote_id}/pdf")
async def download_quote_pdf(quote_id: str, plan_index: int = None):
    """
    PÚBLICO: Genera y descarga el PDF corporativo de alta calidad para el cliente.
    NO REQUIERE LOGIN NI CONTRASEÑA.
    """
    data = storage.get_quotation(quote_id)
    if not data:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    
    # Si se especificó un plan_index en la URL, actualizar la liquidación del PDF
    if plan_index is not None and 0 <= plan_index < len(data.get("plans", [])):
        data = data.copy()
        data["selected_plan_index"] = plan_index
    
    pdf_bytes = pdf_generator.generate_quotation_pdf(data)
    
    client_clean = data.get("client_name", "Cliente").replace(" ", "_")
    plan_label = storage._selected_plan(data).get("num", "Plan").replace(" ", "")
    filename = f"Cotizacion_{quote_id}_{plan_label}_{client_clean}.pdf"
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"'
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
