import json
import os
from datetime import datetime

STORAGE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cotizaciones_db.json")

DEFAULT_PROPOSAL = {
    "quote_number": "COT-2026-001",
    "quote_date": datetime.today().strftime("%d/%m/%Y"),
    "quote_validity": "15 días calendario",
    "company_name": "BARCAM SOFTWARE LABS",
    "company_lead": "Desarrollo de Software & Soluciones Web / Móviles",
    "company_contact": "contacto@barcam.site | +57 300 123 4567 | Colombia",
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


def _load_db():
    if not os.path.exists(STORAGE_FILE):
        initial_data = {"COT-2026-001": DEFAULT_PROPOSAL}
        _save_db(initial_data)
        return initial_data
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"COT-2026-001": DEFAULT_PROPOSAL}


def _save_db(data):
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_quotation(quote_id: str):
    db = _load_db()
    # Búsqueda insensible a mayúsculas
    for q_id, q_data in db.items():
        if q_id.upper() == quote_id.upper():
            return q_data
    return None


def save_quotation(data: dict) -> str:
    db = _load_db()
    quote_id = data.get("quote_number", "").strip()
    if not quote_id:
        quote_id = f"COT-{datetime.today().strftime('%Y%m%d')}-{len(db)+1:02d}"
        data["quote_number"] = quote_id
    
    db[quote_id] = data
    _save_db(db)
    return quote_id


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
    db = _load_db()
    summary = []
    for q_id, q_data in db.items():
        summary.append({
            "id": q_id,
            "project_title": q_data.get("project_title", "Sin título"),
            "client_name": q_data.get("client_name", "Cliente"),
            "client_company": q_data.get("client_company", ""),
            "quote_date": q_data.get("quote_date", ""),
            "total": _selected_plan(q_data).get("price", 0)
        })
    return summary
