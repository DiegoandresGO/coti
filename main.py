import os
import unicodedata
from urllib.parse import quote, unquote
import hmac
import hashlib
import time
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
templates.env.globals["extra_services_flags"] = storage.extra_services_flags
templates.env.globals["quote_whatsapp"] = storage.quote_whatsapp

# ==========================================
# CONFIGURACIÓN DE SEGURIDAD & AUTENTICACIÓN
# ==========================================
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
SECRET_KEY = os.environ.get("SECRET_KEY", "barcam_myfinces_secret_key_2026_xyz")
COOKIE_NAME = "admin_session_token"
# Minutos sin actividad antes de cerrar la sesión del administrador
try:
    SESSION_TIMEOUT_MINUTES = max(1, int(os.environ.get("SESSION_TIMEOUT_MINUTES", "30")))
except ValueError:
    SESSION_TIMEOUT_MINUTES = 30
SESSION_TIMEOUT_SECONDS = SESSION_TIMEOUT_MINUTES * 60


def _sign(payload: str) -> str:
    """La firma incluye un valor guardado en la base de datos que se rota al cerrar
    sesión; así, las cookies anteriores dejan de validarse en el servidor."""
    clave = f"{SECRET_KEY}:{storage.get_session_nonce()}".encode()
    return hmac.new(clave, payload.encode(), hashlib.sha256).hexdigest()


def create_session_token(username: str) -> str:
    """Token firmado con HMAC que incluye la hora de la última actividad."""
    payload = f"{username}:{int(time.time())}"
    return f"{payload}:{_sign(payload)}"


def verify_session_token(token: str) -> bool:
    """Valida firma, usuario y que no hayan pasado más de SESSION_TIMEOUT_MINUTES sin actividad."""
    if not token or token.count(":") < 2:
        return False
    try:
        payload, sig = token.rsplit(":", 1)
        username, last_seen = payload.rsplit(":", 1)
        if not hmac.compare_digest(sig, _sign(payload)) or username != ADMIN_USERNAME:
            return False
        elapsed = time.time() - int(last_seen)
        return -60 <= elapsed <= SESSION_TIMEOUT_SECONDS
    except Exception:
        return False


def _cookie_secure() -> bool:
    return os.environ.get("COOKIE_SECURE", "true").lower() != "false"


# Las páginas del panel no se guardan en caché: si no se envían estas cabeceras,
# el navegador (o un proxy) puede volver a mostrar el panel desde su caché
# después de cerrar la sesión.
NO_STORE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0, private",
    "Pragma": "no-cache",
    "Expires": "0",
    "Vary": "Cookie",
}


def no_store(response):
    response.headers.update(NO_STORE_HEADERS)
    return response


def set_session_cookie(response, username: str):
    response.set_cookie(
        key=COOKIE_NAME,
        value=create_session_token(username),
        max_age=SESSION_TIMEOUT_SECONDS,
        path="/",
        httponly=True,
        samesite="lax",
        secure=_cookie_secure(),
    )


def clear_session_cookie(response):
    """Borra la cookie con la misma ruta con la que se creó; sin el atributo
    Secure, para que el borrado también se aplique si el sitio se sirve por HTTP.
    Se envía Max-Age=0 junto con una fecha de expiración en el pasado, para que
    ningún navegador ni proxy pueda conservar la sesión anterior."""
    response.set_cookie(
        key=COOKIE_NAME,
        value="",
        max_age=0,
        expires="Thu, 01 Jan 1970 00:00:00 GMT",
        path="/",
        httponly=True,
        samesite="lax",
    )


# Aviso de "sesión cerrada por inactividad": viaja en una cookie corta para que
# la dirección del login no muestre parámetros
NOTICE_COOKIE = "login_notice"
NOTICE_COOKIE_SECONDS = 120


def _read_notice_cookie(request: Request):
    """Devuelve (motivo, next) de la cookie de aviso, o ('', '') si no hay."""
    raw = request.cookies.get(NOTICE_COOKIE) or ""
    if not raw.startswith("inactividad|"):
        return "", ""
    return "inactividad", unquote(raw.split("|", 1)[1])[:300]


def safe_next(url: str) -> str:
    """Solo permite redirigir a rutas internas (evita //sitio-externo.com)."""
    url = url or "/"
    return url if url.startswith("/") and not url.startswith("//") and "\\" not in url else "/"

def is_admin_authenticated(request: Request) -> bool:
    """Verifica si la petición proviene de un administrador autenticado."""
    token = request.cookies.get(COOKIE_NAME)
    return verify_session_token(token)


# ==========================================
# PÁGINAS DE ERROR AMIGABLES
# ==========================================
from starlette.exceptions import HTTPException as StarletteHTTPException


def _wants_html(request: Request) -> bool:
    """Navegadores reciben una página; la API y fetch() siguen recibiendo JSON."""
    if request.url.path.startswith("/api/") or request.method != "GET":
        return False
    return "text/html" in request.headers.get("accept", "")


@app.exception_handler(StarletteHTTPException)
async def friendly_http_error(request: Request, exc: StarletteHTTPException):
    if not _wants_html(request):
        return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=getattr(exc, "headers", None))

    path = request.url.path
    if exc.status_code == 404 and path.startswith("/c/"):
        ctx = {
            "icon": "🔒",
            "title": "No tienes acceso a esta propuesta",
            "message": "El enlace que usaste no es válido o ya no tiene permiso para ver esta cotización.",
            "tips": [
                "Verifica que copiaste el enlace completo, sin espacios ni caracteres de más.",
                "Solicita un nuevo enlace de acceso a quien te envió la propuesta.",
            ],
        }
    elif exc.status_code == 404:
        ctx = {
            "icon": "🧭",
            "title": "Página no encontrada",
            "message": "La dirección que intentas abrir no existe o fue movida.",
            "tips": ["Revisa que la dirección esté bien escrita."],
        }
    elif exc.status_code in (401, 403):
        ctx = {
            "icon": "🔒",
            "title": "Acceso restringido",
            "message": "No tienes permiso para ver esta página.",
            "tips": [],
        }
    else:
        ctx = {
            "icon": "⚠️",
            "title": "Algo salió mal",
            "message": "No pudimos completar tu solicitud. Intenta de nuevo en unos minutos.",
            "tips": [],
        }
    ctx["status_code"] = exc.status_code
    response = templates.TemplateResponse(request, "error.html", ctx, status_code=exc.status_code)
    response.headers.update({"X-Robots-Tag": "noindex, nofollow", "Cache-Control": "no-store"})
    return response


# ==========================================
# RUTAS DE AUTENTICACIÓN (LOGIN / LOGOUT)
# ==========================================

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, next: str = "/", motivo: str = ""):
    """Página de acceso para administradores."""
    # El aviso de inactividad llega por cookie; los parámetros en la dirección
    # se siguen aceptando por si queda algún enlace antiguo guardado
    cookie_motivo, cookie_next = _read_notice_cookie(request)
    motivo = motivo or cookie_motivo
    next = safe_next(next if next != "/" else (cookie_next or "/"))

    if is_admin_authenticated(request):
        return RedirectResponse(url=next, status_code=303)

    notice = None
    if motivo == "inactividad":
        notice = f"Tu sesión se cerró tras {SESSION_TIMEOUT_MINUTES} minutos de inactividad. Vuelve a ingresar."
    response = templates.TemplateResponse(request, "login.html", {
        "next_url": next,
        "error": None,
        "notice": notice
    })
    if cookie_motivo:
        response.delete_cookie(NOTICE_COOKIE, path="/", httponly=True, samesite="lax")
    return response


@app.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request):
    """Procesa las credenciales enviadas por el formulario de inicio de sesión."""
    form_data = await request.form()
    username = form_data.get("username", "").strip()
    password = form_data.get("password", "").strip()
    next_url = safe_next(form_data.get("next", "/"))

    if hmac.compare_digest(username, ADMIN_USERNAME) and hmac.compare_digest(password, ADMIN_PASSWORD):
        response = RedirectResponse(url=next_url, status_code=303)
        set_session_cookie(response, username)
        return response

    return templates.TemplateResponse(request, "login.html", {
        "next_url": next_url,
        "error": "Credenciales inválidas. Verifica tu usuario y contraseña de administrador."
    }, status_code=401)


@app.get("/logout")
async def logout(motivo: str = "", next: str = "/"):
    """Cierra la sesión administrativa y lleva al login con una dirección limpia."""
    # El token se invalida también en el servidor, no solo en el navegador
    storage.rotate_session_nonce()
    response = RedirectResponse(url="/login", status_code=303)
    clear_session_cookie(response)
    if motivo == "inactividad":
        # El aviso y el destino viajan en una cookie de corta duración, así la
        # barra de direcciones queda en /login, sin parámetros a la vista
        response.set_cookie(
            key=NOTICE_COOKIE,
            value=f"inactividad|{quote(safe_next(next), safe='')}",
            max_age=NOTICE_COOKIE_SECONDS,
            path="/",
            httponly=True,
            samesite="lax",
            secure=_cookie_secure(),
        )
    return no_store(response)


@app.post("/api/session/ping")
async def session_ping(request: Request):
    """El panel lo llama cuando hay actividad del usuario para mantener la sesión viva."""
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=401, detail="Sesión expirada")
    return {"status": "ok", "timeout_minutes": SESSION_TIMEOUT_MINUTES}


@app.middleware("http")
async def refresh_admin_session(request: Request, call_next):
    """Cada petición del administrador renueva el contador de inactividad (sesión deslizante).
    Además evita que el panel, el login o la API queden en caché: así, al cerrar
    la sesión, volver a la dirección no puede mostrar la página guardada."""
    response = await call_next(request)
    path = request.url.path
    if not path.startswith(("/static", "/c/")):
        no_store(response)
    if (path not in ("/logout", "/login") and not path.startswith(("/static", "/c/"))
            and response.status_code < 400 and is_admin_authenticated(request)
            and "set-cookie" not in response.headers):
        set_session_cookie(response, ADMIN_USERNAME)
    return response


# ==========================================
# RUTAS DE INTERFAZ WEB (ADMIN PROTEGIDO)
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, id: str = ""):
    """Panel de administración y creación de cotizaciones (SOLO ADMINS)."""
    if not is_admin_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)

    # Abrir la cotización pedida (?id=...) o la más reciente
    quotes = storage.list_quotations()
    initial_data = storage.get_quotation(id) if id else None
    if not initial_data:
        initial_data = storage.get_quotation(quotes[0]["id"]) if quotes else storage.DEFAULT_PROPOSAL
    
    return templates.TemplateResponse(request, "admin.html", {
        "session_timeout_minutes": SESSION_TIMEOUT_MINUTES,
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

PRIVATE_HEADERS = {
    "X-Robots-Tag": "noindex, nofollow",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "private, no-store",
}


def _quote_by_token_or_404(token: str) -> dict:
    data = storage.get_quotation_by_token(token)
    if not data:
        raise HTTPException(status_code=404, detail="Enlace no válido o cotización no disponible")
    return data


@app.get("/c/{token}", response_class=HTMLResponse)
async def client_view(request: Request, token: str):
    """
    Portal del cliente. Solo se accede con el código secreto del enlace;
    el número de cotización por sí solo no da acceso.
    """
    data = _quote_by_token_or_404(token)
    response = templates.TemplateResponse(request, "client_view.html", {"data": data})
    response.headers.update(PRIVATE_HEADERS)
    return response


@app.get("/cotizacion/{quote_id}")
async def legacy_client_view(request: Request, quote_id: str):
    """Enlace antiguo por número: solo el administrador es redirigido al enlace seguro."""
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=404, detail="Enlace no válido")
    data = storage.get_quotation(quote_id)
    if not data:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return RedirectResponse(url=f"/c/{data['access_token']}", status_code=303)


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
async def get_quote_data(request: Request, quote_id: str):
    """Datos en formato JSON de una cotización específica (requiere admin)."""
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=401, detail="No autorizado")
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
    # Conservar el registro de la elección del cliente (el panel no lo envía)
    if existing.get("client_selected_at") and existing.get("selected_plan_index") == sel:
        payload["client_selected_at"] = existing["client_selected_at"]
    else:
        payload.pop("client_selected_at", None)
    payload.pop("access_token", None)
    # Las solicitudes del cliente se conservan: el panel no las envía
    if existing.get("client_requests"):
        payload["client_requests"] = existing["client_requests"]

    if is_rename and storage.quotation_exists(original_id):
        quote_id = storage.rename_quotation(original_id, payload)
    else:
        quote_id = storage.save_quotation(payload)
    return {
        "status": "ok",
        "quote_id": quote_id,
        "access_token": storage.get_quotation(quote_id)["access_token"],
        "message": f"Cotización {quote_id} guardada correctamente"
    }


@app.post("/api/cotizaciones/{quote_id}/regenerar-enlace")
async def regenerate_link(request: Request, quote_id: str):
    """Invalida el enlace actual del cliente y crea uno nuevo (requiere admin)."""
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=401, detail="No autorizado")
    token = storage.regenerate_access_token(quote_id)
    if not token:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return {"status": "ok", "access_token": token}


@app.post("/c/{token}/select-plan")
async def select_plan(token: str, payload: dict):
    """El cliente (con enlace válido) elige su plan preferido."""
    data = _quote_by_token_or_404(token)
    try:
        plan_index = int(payload.get("plan_index", 0))
    except (TypeError, ValueError):
        plan_index = -1
    if storage.set_selected_plan(data["quote_number"], plan_index):
        return {"status": "ok", "selected_plan_index": plan_index}
    return {"status": "error", "message": "Índice de plan inválido"}


def _whatsapp_url(data: dict, plan_index, kind: str, message: str) -> str:
    """Enlace wa.me con un mensaje ya redactado para el asesor comercial."""
    number = storage.quote_whatsapp(data)
    if not number:
        return ""
    plans = data.get("plans") or []
    plan = plans[plan_index] if isinstance(plan_index, int) and 0 <= plan_index < len(plans) else None
    quien = data.get("client_name") or "un cliente"
    lineas = [
        f"Hola, soy {quien}."
    ]
    if kind == "modificacion":
        lineas.append(f"Quiero solicitar cambios en la cotización {data.get('quote_number', '')}"
                      f" ({data.get('project_title', '')}).")
    else:
        lineas.append(f"Quiero avanzar con la cotización {data.get('quote_number', '')}"
                      f" ({data.get('project_title', '')}).")
    if plan:
        precio = f"{float(plan.get('price', 0) or 0):,.0f}".replace(",", ".")
        etiqueta = "Plan de referencia" if kind == "modificacion" else "Plan elegido"
        lineas.append(f"{etiqueta}: {plan.get('num', '')} — {plan.get('name', '')} ($ {precio} COP).")
    if message:
        lineas.append(f"Detalle: {message}")
    return f"https://wa.me/{number}?text={quote(chr(10).join(lineas))}"


@app.post("/c/{token}/solicitud")
async def client_request(token: str, payload: dict):
    """El cliente confirma un plan o pide modificaciones; se registra y se arma el enlace de WhatsApp."""
    data = _quote_by_token_or_404(token)
    kind = "modificacion" if payload.get("kind") == "modificacion" else "aceptacion"
    try:
        plan_index = int(payload.get("plan_index"))
    except (TypeError, ValueError):
        plan_index = None
    plans = data.get("plans") or []
    if plan_index is None or not 0 <= plan_index < len(plans):
        plan_index = None
    message = str(payload.get("message") or "").strip()[:2000]
    if kind == "modificacion" and not message:
        raise HTTPException(status_code=400, detail="Describe los cambios que necesitas en la cotización.")

    if kind == "aceptacion" and plan_index is not None:
        storage.set_selected_plan(data["quote_number"], plan_index)
        data["selected_plan_index"] = plan_index
    storage.add_client_request(data["quote_number"], kind, plan_index, message)
    return {"status": "ok", "whatsapp_url": _whatsapp_url(data, plan_index, kind, message)}


@app.post("/api/cotizaciones/{quote_id}/solicitudes/atendidas")
async def mark_requests(request: Request, quote_id: str):
    """Marca como atendidas las solicitudes del cliente (requiere admin)."""
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=401, detail="No autorizado")
    if not storage.mark_requests_attended(quote_id):
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return {"status": "ok"}


def _pdf_response(data: dict, plan_index):
    quote_id = data["quote_number"]
    if plan_index is not None and 0 <= plan_index < len(data.get("plans", [])):
        data = data.copy()
        data["selected_plan_index"] = plan_index

    pdf_bytes = pdf_generator.generate_quotation_pdf(data)

    client_clean = data.get("client_name", "Cliente").replace(" ", "_")
    plan_label = storage._selected_plan(data).get("num", "Plan").replace(" ", "")
    filename = f"Cotizacion_{quote_id}_{plan_label}_{client_clean}.pdf"
    ascii_name = unicodedata.normalize("NFKD", filename).encode("ascii", "ignore").decode().replace('"', "")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            # Nombre ASCII para compatibilidad + nombre UTF-8 (tildes) para navegadores modernos
            "Content-Disposition": f"inline; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(filename)}",
            **PRIVATE_HEADERS,
        }
    )


@app.get("/c/{token}/pdf")
async def client_pdf(token: str, plan_index: int = None):
    """PDF para el cliente con enlace válido."""
    return _pdf_response(_quote_by_token_or_404(token), plan_index)


@app.get("/api/cotizaciones/{quote_id}/pdf")
async def download_quote_pdf(request: Request, quote_id: str, plan_index: int = None):
    """PDF por número de cotización (requiere admin)."""
    if not is_admin_authenticated(request):
        raise HTTPException(status_code=401, detail="No autorizado")
    data = storage.get_quotation(quote_id)
    if not data:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    return _pdf_response(data, plan_index)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
