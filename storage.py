import json
import os
import secrets
import sqlite3
import threading
from datetime import datetime

STORAGE_FILE = os.environ.get(
    "STORAGE_FILE",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "cotizaciones_db.json")
)
DATABASE_FILE = os.environ.get(
    "DATABASE_FILE",
    os.path.join(os.path.dirname(STORAGE_FILE), "cotizaciones.db")
)

DEFAULT_PROPOSAL = {
    "quote_number": "COT-2026-001",
    "quote_date": datetime.today().strftime("%d/%m/%Y"),
    "quote_validity": "15 días calendario",
    "company_name": "BARCAM SOFTWARE LABS",
    "company_lead": "Desarrollo de Software & Soluciones Web / Móviles",
    "company_contact": "contacto@barcam.site | +57 300 123 4567 | Colombia",
    "company_whatsapp": "+57 300 123 4567",
    "client_name": "Carlos Rodríguez",
    "client_company": "Inversiones & Finanzas S.A.S",
    "client_contact": "carlos.rodriguez@inversiones.com | +57 310 987 6543",
    "project_title": "MyFinces — Control de Finanzas Personales",
    "project_category": "Ecosistema Web & Aplicación Móvil APK",
    "project_description": (
        "Desarrollo e implementación del ecosistema de software MyFinces para el control integral de finanzas personales. "
        "Permite registrar ingresos, egresos, gastos fijos periódicos, seguimiento a deudas activas y conciliación de metas de ahorro "
        "en un libro contable centralizado. La solución incluye la aplicación web responsive conectada a backend en la nube, "
        "el panel administrativo de gestión y la compilación de la aplicación móvil en formato APK optimizada."
    ),
    "modules": [
        {
            "name": "Portal Web MyFinces",
            "desc": "Interfaz web responsiva para registro, conciliación mensual de ingresos/gastos, balance en tiempo real y gráficos analíticos."
        },
        {
            "name": "Conexión Web & Backend Seguro",
            "desc": "APIs RESTful seguras que sincronizan la aplicación web y móvil con la base de datos central protegida."
        },
        {
            "name": "Panel Administrativo y Auditoría",
            "desc": "Administración de usuarios, monitoreo de sesiones, configuración de parámetros y control centralizado."
        },
        {
            "name": "Aplicación Móvil (Entrega APK)",
            "desc": "App móvil compilada en paquete instalador APK para Android con diseño rápido, modo offline y sincronización."
        },
        {
            "name": "Ingeniería, Despliegue y Soporte",
            "desc": "Ciclo completo de ingeniería, puesta en marcha en servidor y acompañamiento técnico post-entrega garantizado."
        }
    ],
    "plans": [
        {
            "num": "Opción 1",
            "name": "Plan Esencial / MVP",
            "price": 2500000,
            "support_hours": "8 horas",
            "features": "Web App básica conectada + Entrega APK + 8 horas de soporte técnico incluidas.",
            "is_recommended": False
        },
        {
            "num": "Opción 2",
            "name": "Plan Estándar Profesional",
            "price": 4000000,
            "support_hours": "15 horas",
            "features": "Web completa + Panel Admin + Conexión sincronizada + APK optimizada + 15 horas de soporte técnico incluidas.",
            "is_recommended": True
        },
        {
            "num": "Opción 3",
            "name": "Plan Avanzado & Escalable",
            "price": 5000000,
            "support_hours": "20 horas",
            "features": "Ecosistema completo Web + Admin + APK + Prioridad de entrega + 20 horas de soporte técnico incluidas.",
            "is_recommended": False
        }
    ],
    "selected_plan_index": 1,
    "show_extra_services": True,
    "show_pentest": True,
    "show_hourly_dev": True,
    "show_hourly_supp": True,
    "hourly_rate_dev": 75000,
    "hourly_rate_supp": 50000,
    "pentest_cost": "$ 800.000 COP",
    "pentest_desc": "Auditoría técnica OWASP, pruebas de penetración contra inyecciones y fugas de datos en APIs backend y aplicación web, con informe.",
    "include_pentest_in_total": False,
    "exclusions": [
        "Servidor / VPS / Hosting: El costo mensual o anual de la infraestructura en la nube corre por cuenta directa del cliente.",
        "Dominio y Certificados SSL: La adquisición, renovación y titularidad del dominio web es asumida por el cliente.",
        "Consumo de APIs de Inteligencia Artificial: Saldo o tokens facturados directamente por proveedores externos (OpenAI, Gemini, etc.).",
        "Licenciamiento de Terceros y Cuentas de Desarrollador: Membresías de tiendas (Google Play $25 USD / Apple $99 USD) o librerías pagas.",
        "Tiempos de Aprobación de Tiendas: Los tiempos de validación de Google o Apple escapan al control del equipo de desarrollo."
    ],
    "limitations": [
        "Entrega en formato APK: La app móvil se entrega como paquete instalador APK firmado. No incluye publicación en Google Play Store salvo contratación adicional.",
        "Instalación y Desconocimiento de APK: La distribución manual de la APK a usuarios finales del cliente es responsabilidad del cliente.",
        "Accesos al Servidor: La entrega a tiempo depende del suministro oportuno de accesos a servidores y credenciales por parte del cliente.",
        "Documentación Faltante: Requerimientos no contemplados en esta cotización se liquidarán bajo la bolsa de horas de desarrollo.",
        "Garantía Técnica: 30 días calendario de soporte y resolución de bugs sin costo tras la entrega formal."
    ],
    "tax_type": "Valor Neto (Persona Natural / No Responsable de IVA)",
    "tax_rate": 0.0,
    "rete_fuente_enabled": False,
    "rete_fuente_pct": 11.0,
    "rete_iva_enabled": False,
    "rete_iva_pct": 15.0,
    "rete_ica_enabled": False,
    "rete_ica_pm": 9.66,
    "adv_pct": 50,
    "mid_pct": 30,
    "fin_pct": 20
}


# ==========================================
# BASE DE DATOS SQLITE
# ==========================================
_lock = threading.Lock()
_initialized = False


def _connect():
    os.makedirs(os.path.dirname(DATABASE_FILE) or ".", exist_ok=True)
    conn = sqlite3.connect(DATABASE_FILE, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    return conn


def _now():
    return datetime.now().isoformat(timespec="seconds")


def init_db():
    """Crea la tabla y migra una sola vez las cotizaciones del JSON antiguo."""
    global _initialized
    if _initialized:
        return
    with _lock:
        if _initialized:
            return
        with _connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quotations (
                    id          TEXT PRIMARY KEY COLLATE NOCASE,
                    data        TEXT NOT NULL,
                    created_at  TEXT NOT NULL,
                    updated_at  TEXT NOT NULL
                )
            """)
            empty = conn.execute("SELECT COUNT(*) FROM quotations").fetchone()[0] == 0
            if empty:
                legacy = {}
                if os.path.exists(STORAGE_FILE):
                    try:
                        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                            legacy = json.load(f)
                    except Exception:
                        legacy = {}
                if not legacy:
                    legacy = {DEFAULT_PROPOSAL["quote_number"]: DEFAULT_PROPOSAL}
                now = _now()
                conn.executemany(
                    "INSERT OR IGNORE INTO quotations (id, data, created_at, updated_at) VALUES (?, ?, ?, ?)",
                    [(q_id, json.dumps(q, ensure_ascii=False), now, now) for q_id, q in legacy.items()]
                )
                if os.path.exists(STORAGE_FILE):
                    try:
                        os.replace(STORAGE_FILE, STORAGE_FILE + ".migrado")
                    except OSError:
                        pass
            _ensure_token_column(conn)
            conn.execute("CREATE TABLE IF NOT EXISTS app_state (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS quotation_tests (
                    token       TEXT PRIMARY KEY,
                    quote_id    TEXT NOT NULL,
                    data        TEXT NOT NULL,
                    created_at  TEXT NOT NULL
                )
            """)
        _initialized = True


def _app_state_set(conn, key: str, value: str):
    conn.execute("INSERT INTO app_state (key, value) VALUES (?, ?) "
                 "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, value))


def get_session_nonce() -> str:
    """Valor que acompaña a la firma de la cookie del panel.
    Al rotarlo, todas las cookies emitidas antes dejan de ser válidas."""
    init_db()
    with _lock, _connect() as conn:
        row = conn.execute("SELECT value FROM app_state WHERE key = 'session_nonce'").fetchone()
        if row and row["value"]:
            return row["value"]
        nonce = secrets.token_urlsafe(16)
        _app_state_set(conn, "session_nonce", nonce)
    return nonce


def rotate_session_nonce() -> str:
    """Invalida en el servidor todas las sesiones abiertas del panel."""
    init_db()
    nonce = secrets.token_urlsafe(16)
    with _lock, _connect() as conn:
        _app_state_set(conn, "session_nonce", nonce)
    return nonce


def new_access_token() -> str:
    """Código secreto e impredecible para el enlace del cliente (~128 bits)."""
    return secrets.token_urlsafe(16)


def _ensure_token_column(conn):
    """Agrega la columna access_token (si falta) y asigna un código a las cotizaciones que no lo tengan."""
    cols = [r["name"] for r in conn.execute("PRAGMA table_info(quotations)")]
    if "access_token" not in cols:
        conn.execute("ALTER TABLE quotations ADD COLUMN access_token TEXT")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_quotations_token ON quotations(access_token)")
    for (q_id,) in conn.execute("SELECT id FROM quotations WHERE access_token IS NULL OR access_token = ''").fetchall():
        conn.execute("UPDATE quotations SET access_token = ? WHERE id = ?", (new_access_token(), q_id))


def _row_to_data(row):
    data = json.loads(row["data"])
    # El número y el código de acceso vienen siempre del registro
    data["quote_number"] = row["id"]
    data["access_token"] = row["access_token"]
    return data


def _clean_for_storage(data: dict) -> str:
    stored = {k: v for k, v in data.items() if k != "access_token"}
    return json.dumps(stored, ensure_ascii=False)


def get_quotation_by_token(token: str):
    init_db()
    token = (token or "").strip()
    if len(token) < 16:
        return None
    with _connect() as conn:
        row = conn.execute("SELECT id, data, access_token FROM quotations WHERE access_token = ?", (token,)).fetchone()
    return _row_to_data(row) if row else None


# ==========================================
# COPIAS DE PRUEBA (no afectan la cotización real)
# ==========================================
TEST_PREFIX = "prueba_"
TEST_TTL_HOURS = 24


def is_test_token(token: str) -> bool:
    return str(token or "").startswith(TEST_PREFIX)


def create_test_copy(quote_id: str, data: dict) -> str:
    """Guarda una copia aislada de la cotización para pruebas del administrador.
    Cada cotización tiene una sola copia de prueba: la nueva reemplaza la anterior."""
    init_db()
    quote_id = str(quote_id or data.get("quote_number") or "BORRADOR").strip()
    token = TEST_PREFIX + secrets.token_urlsafe(16)
    data = dict(data)
    for key in ("client_requests", "client_selected_at", "client_confirmed_at"):
        data.pop(key, None)
    limit = datetime.fromtimestamp(datetime.now().timestamp() - TEST_TTL_HOURS * 3600).isoformat(timespec="seconds")
    with _lock, _connect() as conn:
        conn.execute("DELETE FROM quotation_tests WHERE quote_id = ? OR created_at < ?", (quote_id, limit))
        conn.execute("INSERT INTO quotation_tests (token, quote_id, data, created_at) VALUES (?, ?, ?, ?)",
                     (token, quote_id, _clean_for_storage(data), _now()))
    return token


def get_test_copy(token: str):
    init_db()
    with _connect() as conn:
        row = conn.execute("SELECT token, quote_id, data FROM quotation_tests WHERE token = ?",
                           (str(token or ""),)).fetchone()
    if not row:
        return None
    data = json.loads(row["data"])
    data["quote_number"] = row["quote_id"]
    data["access_token"] = row["token"]
    data["is_test"] = True
    return data


def update_test_copy(token: str, data: dict):
    """Las acciones simuladas del cliente solo modifican la copia de prueba."""
    init_db()
    with _lock, _connect() as conn:
        conn.execute("UPDATE quotation_tests SET data = ? WHERE token = ?",
                     (_clean_for_storage({k: v for k, v in data.items() if k != "is_test"}), token))


def delete_test_copies(quote_id: str):
    init_db()
    with _lock, _connect() as conn:
        conn.execute("DELETE FROM quotation_tests WHERE quote_id = ?", (str(quote_id or "").strip(),))


def regenerate_access_token(quote_id: str):
    """Invalida el enlace anterior del cliente y genera uno nuevo."""
    init_db()
    token = new_access_token()
    with _lock, _connect() as conn:
        cur = conn.execute("UPDATE quotations SET access_token = ?, updated_at = ? WHERE id = ?",
                           (token, _now(), quote_id.strip()))
        return token if cur.rowcount else None


def get_quotation(quote_id: str):
    init_db()
    with _connect() as conn:
        row = conn.execute("SELECT id, data, access_token FROM quotations WHERE id = ?", (quote_id.strip(),)).fetchone()
    return _row_to_data(row) if row else None


def save_quotation(data: dict) -> str:
    init_db()
    with _lock, _connect() as conn:
        quote_id = str(data.get("quote_number", "")).strip()
        if not quote_id:
            quote_id = _next_quote_number(conn)
            data["quote_number"] = quote_id
        now = _now()
        # El código de acceso se conserva al editar; solo se crea para cotizaciones nuevas
        conn.execute("""
            INSERT INTO quotations (id, data, created_at, updated_at, access_token) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at
        """, (quote_id, _clean_for_storage(data), now, now, new_access_token()))
    return quote_id


def _next_quote_number(conn) -> str:
    """Siguiente consecutivo del año: COT-2026-001, COT-2026-002, ..."""
    prefix = f"COT-{datetime.today().year}-"
    max_seq = 0
    for (q_id,) in conn.execute("SELECT id FROM quotations WHERE id LIKE ?", (prefix + "%",)):
        tail = q_id[len(prefix):]
        if tail.isdigit():
            max_seq = max(max_seq, int(tail))
    return f"{prefix}{max_seq + 1:03d}"


def next_quote_number() -> str:
    init_db()
    with _connect() as conn:
        return _next_quote_number(conn)


def quotation_exists(quote_id: str) -> bool:
    return get_quotation(quote_id) is not None


def delete_quotation(quote_id: str) -> bool:
    init_db()
    with _lock, _connect() as conn:
        cur = conn.execute("DELETE FROM quotations WHERE id = ?", (quote_id.strip(),))
        return cur.rowcount > 0


def rename_quotation(old_id: str, data: dict) -> str:
    """Guarda con un número nuevo y elimina el anterior en una sola operación."""
    init_db()
    new_id = str(data.get("quote_number", "")).strip()
    with _lock, _connect() as conn:
        row = conn.execute("SELECT created_at, access_token FROM quotations WHERE id = ?", (old_id.strip(),)).fetchone()
        created = row["created_at"] if row else _now()
        token = (row["access_token"] if row else None) or new_access_token()
        conn.execute("DELETE FROM quotations WHERE id = ?", (old_id.strip(),))
        conn.execute("INSERT INTO quotations (id, data, created_at, updated_at, access_token) VALUES (?, ?, ?, ?, ?)",
                     (new_id, _clean_for_storage(data), created, _now(), token))
    return new_id


def set_selected_plan(quote_id: str, plan_index: int):
    """Actualiza solo el plan elegido por el cliente, sin pisar otros cambios."""
    init_db()
    with _lock, _connect() as conn:
        row = conn.execute("SELECT data FROM quotations WHERE id = ?", (quote_id.strip(),)).fetchone()
        if not row:
            return None
        data = json.loads(row["data"])
        if data.get("client_confirmed_at"):
            return False  # Ya confirmado: el plan no se puede cambiar desde el enlace
        if not 0 <= plan_index < len(data.get("plans", [])):
            return False
        data["selected_plan_index"] = plan_index
        data["client_selected_at"] = _now()
        conn.execute("UPDATE quotations SET data = ? WHERE id = ?",
                     (_clean_for_storage(data), quote_id.strip()))
    return True


DEFAULT_WHATSAPP = os.environ.get("WHATSAPP_NUMBER", "")
DEFAULT_COUNTRY_CODE = os.environ.get("WHATSAPP_COUNTRY_CODE", "57")


def whatsapp_digits(raw) -> str:
    """Deja el numero listo para wa.me: solo digitos y con indicativo de pais.
    Acepta '+57 300 123 4567', '300 123 4567', '57 300...'. Devuelve '' si no sirve."""
    digits = "".join(ch for ch in str(raw or "") if ch.isdigit())
    if not digits:
        return ""
    if len(digits) == 10 and DEFAULT_COUNTRY_CODE:
        digits = DEFAULT_COUNTRY_CODE + digits
    return digits if 8 <= len(digits) <= 15 else ""


def quote_whatsapp(data: dict) -> str:
    """Numero de WhatsApp del emisor para esta cotizacion (o el global por defecto)."""
    return whatsapp_digits(data.get("company_whatsapp") or DEFAULT_WHATSAPP)


def add_client_request(quote_id: str, kind: str, plan_index, message: str):
    """Registra que el cliente acepto un plan o pidio cambios en la cotizacion."""
    init_db()
    entry = {
        "kind": "modificacion" if kind == "modificacion" else "aceptacion",
        "plan_index": plan_index if isinstance(plan_index, int) else None,
        "message": str(message or "").strip()[:2000],
        "created_at": _now(),
        "attended": False,
    }
    with _lock, _connect() as conn:
        row = conn.execute("SELECT data FROM quotations WHERE id = ?", (quote_id.strip(),)).fetchone()
        if not row:
            return None
        data = json.loads(row["data"])
        requests = data.get("client_requests")
        if not isinstance(requests, list):
            requests = []
        plan = None
        if isinstance(entry["plan_index"], int):
            plans = data.get("plans") or []
            if 0 <= entry["plan_index"] < len(plans):
                plan = plans[entry["plan_index"]]
        entry["plan_label"] = f'{plan.get("num", "")} — {plan.get("name", "")}'.strip(" —") if plan else ""
        if entry["kind"] == "aceptacion":
            if data.get("client_confirmed_at"):
                return {**entry, "already_confirmed": True}  # No se registra dos veces
            data["client_confirmed_at"] = entry["created_at"]
            if plan:
                data["selected_plan_index"] = entry["plan_index"]
                data["client_selected_at"] = data.get("client_selected_at") or entry["created_at"]
        requests.append(entry)
        data["client_requests"] = requests[-50:]
        conn.execute("UPDATE quotations SET data = ?, updated_at = ? WHERE id = ?",
                     (_clean_for_storage(data), _now(), quote_id.strip()))
    return entry


def mark_requests_attended(quote_id: str) -> bool:
    """El administrador marca como atendidas todas las solicitudes del cliente."""
    init_db()
    with _lock, _connect() as conn:
        row = conn.execute("SELECT data FROM quotations WHERE id = ?", (quote_id.strip(),)).fetchone()
        if not row:
            return False
        data = json.loads(row["data"])
        for req in data.get("client_requests") or []:
            req["attended"] = True
        conn.execute("UPDATE quotations SET data = ? WHERE id = ?",
                     (_clean_for_storage(data), quote_id.strip()))
    return True


def extra_services_flags(data: dict) -> dict:
    """Qué servicios complementarios se muestran. Las cotizaciones antiguas los muestran todos."""
    section = data.get("show_extra_services", True) is not False
    flags = {
        "pentest": section and data.get("show_pentest", True) is not False,
        "hourly_dev": section and data.get("show_hourly_dev", True) is not False,
        "hourly_supp": section and data.get("show_hourly_supp", True) is not False,
    }
    flags["any"] = flags["pentest"] or flags["hourly_dev"] or flags["hourly_supp"]
    return flags


def plan_items(features) -> list:
    """Convierte el alcance de un plan en lista de ítems.
    Acepta lista, texto con un ítem por línea o texto antiguo separado por ' + '."""
    if isinstance(features, list):
        items = features
    else:
        text = str(features or "")
        items = text.splitlines() if "\n" in text else text.split(" + ")
    return [i.strip(" \t-•✔") for i in items if i.strip(" \t-•✔")]


def compute_totals(data: dict, base_val: float) -> dict:
    """Subtotal -> IVA -> Total factura -> Retenciones -> Neto a pagar."""
    def f(key, default=0.0):
        try:
            return float(data.get(key, default) or 0)
        except (TypeError, ValueError):
            return 0.0

    tax_rate = f("tax_rate")
    iva = base_val * tax_rate / 100.0
    total = base_val + iva

    retentions = []
    if data.get("rete_fuente_enabled") and f("rete_fuente_pct") > 0:
        pct = f("rete_fuente_pct")
        retentions.append({"key": "fuente", "label": f"Retención en la Fuente ({pct:g}%)",
                           "desc": "Sobre el subtotal antes de IVA", "value": base_val * pct / 100.0})
    if data.get("rete_iva_enabled") and f("rete_iva_pct") > 0 and iva > 0:
        pct = f("rete_iva_pct")
        retentions.append({"key": "iva", "label": f"ReteIVA ({pct:g}% del IVA)",
                           "desc": "Sobre el valor del IVA", "value": iva * pct / 100.0})
    if data.get("rete_ica_enabled") and f("rete_ica_pm") > 0:
        pm = f("rete_ica_pm")
        retentions.append({"key": "ica", "label": f"ReteICA ({pm:g} por mil)",
                           "desc": "Sobre el subtotal antes de IVA", "value": base_val * pm / 1000.0})

    total_ret = sum(r["value"] for r in retentions)
    return {"base": base_val, "iva": iva, "total": total, "retentions": retentions,
            "total_retentions": total_ret, "neto": total - total_ret}


def _selected_plan(q_data: dict) -> dict:
    plans = q_data.get("plans") or [{}]
    idx = q_data.get("selected_plan_index", 0) or 0
    return plans[min(max(idx, 0), len(plans) - 1)]


def list_quotations():
    init_db()
    with _connect() as conn:
        rows = conn.execute("SELECT id, data, access_token, created_at FROM quotations ORDER BY updated_at DESC, rowid DESC").fetchall()
    summary = []
    for row in rows:
        q_data = json.loads(row["data"])
        summary.append({
            "id": row["id"],
            "access_token": row["access_token"],
            "project_title": q_data.get("project_title", "Sin título"),
            "client_name": q_data.get("client_name", "Cliente"),
            "client_company": q_data.get("client_company", ""),
            "quote_date": q_data.get("quote_date", ""),
            "created_at": row["created_at"],
            "client_selected_at": q_data.get("client_selected_at"),
            "client_confirmed_at": q_data.get("client_confirmed_at"),
            "pending_requests": sum(1 for r in (q_data.get("client_requests") or []) if not r.get("attended")),
            "selected_plan": (f'{_selected_plan(q_data).get("num", "")} — {_selected_plan(q_data).get("name", "")}'
                              if q_data.get("client_selected_at") else ""),
            "neto": compute_totals(q_data, float(_selected_plan(q_data).get("price", 0) or 0))["neto"],
        })
    return summary
