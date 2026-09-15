import streamlit as st
import base64
from datetime import datetime
import pdf_generator

st.set_page_config(
    page_title="MyFinces+ — Cotizador Oficial de Software",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS de alta estética inspirados en diseño moderno FinTech
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Contenedor Hero Ejecutivo con Efecto Glow */
    .myfinces-hero {
        background: linear-gradient(135deg, #0B0F19 0%, #111827 50%, #1E1B4B 100%);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 16px;
        padding: 26px 32px;
        margin-bottom: 24px;
        box-shadow: 0 12px 30px -8px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(255, 255, 255, 0.05) inset;
        position: relative;
        overflow: hidden;
    }
    
    .myfinces-hero::after {
        content: "";
        position: absolute;
        top: -60px;
        right: -60px;
        width: 220px;
        height: 220px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.35) 0%, rgba(11, 15, 25, 0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    
    .brand-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(79, 70, 229, 0.2);
        border: 1px solid rgba(99, 102, 241, 0.4);
        color: #C7D2FE;
        font-size: 10.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        padding: 4px 12px;
        border-radius: 20px;
        margin-bottom: 12px;
    }
    
    .hero-title {
        color: #F8FAFC !important;
        font-size: 22px !important;
        font-weight: 800 !important;
        margin: 4px 0 6px 0 !important;
        letter-spacing: -0.02em;
    }
    
    .hero-title span {
        background: linear-gradient(135deg, #818CF8 0%, #C7D2FE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        color: #94A3B8 !important;
        font-size: 13.5px !important;
        margin: 0 0 16px 0 !important;
        line-height: 1.5;
        max-width: 800px;
    }
    
    /* Barra de estado rápido (KPIs de Cabecera) */
    .hero-kpis {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        padding-top: 14px;
    }
    
    .hero-chip {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 12px;
        color: #E2E8F0;
    }
    
    .hero-chip strong {
        color: #818CF8;
    }
    
    /* Estilos de Pestañas Modernas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F1F5F9;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 18px;
        font-weight: 600;
        font-size: 13.5px;
        color: #64748B;
        border: none !important;
        background-color: transparent;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #4F46E5 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08) !important;
    }
    
    /* Tarjetas de Planes (Estilo Pricing Table) */
    .pricing-card {
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 22px 20px;
        background: #FFFFFF;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .pricing-card.recommended {
        border: 2px solid #4F46E5;
        background: #FAFAFE;
        box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.15);
    }
    
    .badge-ribbon {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%);
        color: white;
        font-size: 10.5px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 4px 10px;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 8px;
    }
    
    .support-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        color: #15803D;
        font-size: 12px;
        font-weight: 700;
        padding: 5px 10px;
        border-radius: 8px;
        margin-top: 6px;
    }
    
    /* Tarjetas de Métricas Ejecutivas */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: #E2E8F0;
    }
    
    .metric-card.accent-indigo::before {
        background: #4F46E5;
    }
    
    .metric-card.accent-emerald::before {
        background: #10B981;
    }
    
    .metric-title {
        font-size: 11px;
        color: #64748B;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    
    .metric-value {
        font-size: 22px;
        color: #0F172A;
        font-weight: 800;
        margin-top: 6px;
        letter-spacing: -0.02em;
    }
    
    /* Botones de Acción Primarios */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
        transition: all 0.2s ease !important;
    }
    
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4) !important;
    }
    
    /* Cuadro de llamada a la acción en Descarga */
    .download-hero-card {
        background: linear-gradient(135deg, #EEF2FF 0%, #FFFFFF 100%);
        border: 1px solid #C7D2FE;
        border-radius: 14px;
        padding: 22px 24px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Preset de datos basado en MyFinces
DEFAULT_MYFINCES_DATA = {
    "company_name": "BARCAM SOFTWARE LABS",
    "company_lead": "Desarrollo de Software & Soluciones Web / Móviles",
    "company_contact": "contacto@barcam.site | +57 300 123 4567 | Colombia",
    "bank_info": "Bancolombia Cuenta de Ahorros N° 123-456789-00 a nombre de Desarrollador / Empresa.",
    "quote_number": "COT-2026-001",
    "quote_date": datetime.today().strftime("%d/%m/%Y"),
    "quote_validity": "15 días calendario",
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
    "deliverables": [
        "Código fuente completo del aplicativo web y backend en repositorio Git privado.",
        "Archivo instalador APK de la aplicación móvil optimizado para Android.",
        "Despliegue operativo y parametrización en servidor VPS acordado.",
        "Documentación técnica de arquitectura, credenciales maestras y manual de usuario.",
        "Sesión de capacitación virtual (2 horas) para la administración del sistema."
    ],
    "tax_type": "Valor Neto (Persona Natural / No Responsable de IVA)",
    "tax_rate": 0.0,
    "adv_pct": 50,
    "mid_pct": 30,
    "fin_pct": 20
}

# Inicializar sesión
if "quote_data" not in st.session_state:
    st.session_state.quote_data = DEFAULT_MYFINCES_DATA.copy()

data = st.session_state.quote_data

# ==========================================
# BARRA LATERAL (CONFIGURACIÓN)
# ==========================================
with st.sidebar:
    st.markdown("### 🏢 Emisor & Marca")
    
    col_pre1, col_pre2 = st.columns(2)
    with col_pre1:
        if st.button("🔄 MyFinces", use_container_width=True, help="Recargar valores de MyFinces"):
            st.session_state.quote_data = DEFAULT_MYFINCES_DATA.copy()
            st.rerun()
    with col_pre2:
        if st.button("🧹 Limpiar", use_container_width=True, help="Limpiar campos"):
            st.session_state.quote_data = {
                "company_name": "", "company_lead": "", "company_contact": "", "bank_info": "",
                "quote_number": "COT-" + datetime.today().strftime("%Y%m%d"),
                "quote_date": datetime.today().strftime("%d/%m/%Y"), "quote_validity": "15 días",
                "client_name": "", "client_company": "", "client_contact": "",
                "project_title": "", "project_category": "Desarrollo de Software",
                "project_description": "",
                "modules": [{"name": "Módulo 1", "desc": "Descripción funcional"}],
                "plans": [
                    {"num": "Opción 1", "name": "Básico", "price": 0, "support_hours": "0 horas", "features": "", "is_recommended": False}
                ],
                "selected_plan_index": 0, "hourly_rate_dev": 75000, "hourly_rate_supp": 50000,
                "pentest_cost": "N/A", "pentest_desc": "", "include_pentest_in_total": False,
                "exclusions": [], "limitations": [], "deliverables": [],
                "tax_type": "Valor Neto", "tax_rate": 0.0, "adv_pct": 50, "mid_pct": 30, "fin_pct": 20
            }
            st.rerun()

    st.text_input("Empresa / Proveedor", value=data["company_name"], key="sb_comp_name")
    st.text_input("Especialidad / Plataforma", value=data["company_lead"], key="sb_comp_lead")
    st.text_input("Contacto (Email | Tel | País)", value=data["company_contact"], key="sb_comp_contact")
    st.text_area("Datos de Pago Bancario", value=data["bank_info"], key="sb_bank_info", height=65)
    
    st.markdown("---")
    st.markdown("### 👤 Datos del Cliente")
    st.text_input("Nombre del Cliente", value=data["client_name"], key="sb_cli_name")
    st.text_input("Empresa u Organización", value=data["client_company"], key="sb_cli_comp")
    st.text_input("Contacto del Cliente", value=data["client_contact"], key="sb_cli_contact")

    st.markdown("---")
    st.markdown("### 📅 Consecutivo y Fechas")
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.text_input("N° Cotización", value=data["quote_number"], key="sb_quote_num")
    with c_m2:
        st.text_input("Fecha", value=data["quote_date"], key="sb_quote_date")
    st.text_input("Vigencia de la Oferta", value=data["quote_validity"], key="sb_quote_val")

# Sincronizar sidebar
data["company_name"] = st.session_state.get("sb_comp_name", data.get("company_name", ""))
data["company_lead"] = st.session_state.get("sb_comp_lead", data.get("company_lead", ""))
data["company_contact"] = st.session_state.get("sb_comp_contact", data.get("company_contact", ""))
data["bank_info"] = st.session_state.get("sb_bank_info", data.get("bank_info", ""))
data["client_name"] = st.session_state.get("sb_cli_name", data.get("client_name", ""))
data["client_company"] = st.session_state.get("sb_cli_comp", data.get("client_company", ""))
data["client_contact"] = st.session_state.get("sb_cli_contact", data.get("client_contact", ""))
data["quote_number"] = st.session_state.get("sb_quote_num", data.get("quote_number", "COT-2026-001"))
data["quote_date"] = st.session_state.get("sb_quote_date", data.get("quote_date", datetime.today().strftime("%d/%m/%Y")))
data["quote_validity"] = st.session_state.get("sb_quote_val", data.get("quote_validity", "15 días calendario"))

# Plan seleccionado activo para KPIs
active_plan_idx = data.get("selected_plan_index", 1)
curr_plan = data["plans"][min(active_plan_idx, len(data["plans"]) - 1)]

# ==========================================
# HERO BANNER DE ALTA ESTÉTICA
# ==========================================
hero_html = (
    f'<div class="myfinces-hero">'
    f'<div class="brand-pill"><span>⚡ SISTEMA DE CONTROL FINANCIERO PERSONAL</span></div>'
    f'<div class="hero-title">CADA PESO <span>REGISTRADO.</span> CADA DECISIÓN INFORMADA.</div>'
    f'<div class="hero-subtitle">Generador de propuestas técnico-comerciales para el desarrollo de software (Web + Móvil APK + Panel de Administración).</div>'
    f'<div class="hero-kpis">'
    f'<div class="hero-chip">💼 Plan: <strong>{curr_plan["num"]} ({curr_plan["name"]})</strong></div>'
    f'<div class="hero-chip">💰 Total: <strong>{pdf_generator.format_currency(curr_plan["price"])}</strong></div>'
    f'<div class="hero-chip">⏱️ Soporte: <strong>{curr_plan["support_hours"]}</strong></div>'
    f'<div class="hero-chip">📑 N°: <strong>{data["quote_number"]}</strong></div>'
    f'</div>'
    f'</div>'
)
st.markdown(hero_html, unsafe_allow_html=True)

# Pestañas
tab_scope, tab_plans, tab_limits, tab_payment, tab_preview = st.tabs([
    "🎯 1. Alcance & Módulos",
    "💰 2. Planes & Precios",
    "📋 3. Exclusiones & Limitantes",
    "💳 4. Pagos & Facturación",
    "📄 5. Vista Previa & Descargar PDF"
])

# ==========================================
# TAB 1: ALCANCE & MÓDULOS
# ==========================================
with tab_scope:
    st.markdown("#### 🎯 Información General del Proyecto")
    c_p1, c_p2 = st.columns([2, 1])
    with c_p1:
        data["project_title"] = st.text_input("Título del Proyecto", value=data["project_title"])
    with c_p2:
        data["project_category"] = st.text_input("Categoría / Tipo de Solución", value=data["project_category"])
        
    data["project_description"] = st.text_area(
        "Descripción del Desarrollo a Realizar",
        value=data["project_description"],
        height=100
    )
    
    st.markdown("---")
    st.markdown("#### 📦 Módulos del Sistema (Alcance Funcional)")
    
    modules_to_remove = []
    for i, mod in enumerate(data["modules"]):
        with st.expander(f"📦 Módulo {i+1}: {mod['name']}", expanded=True):
            col_m1, col_m2, col_m3 = st.columns([3, 6, 1])
            with col_m1:
                mod["name"] = st.text_input(f"Nombre Módulo {i+1}", value=mod["name"], key=f"mod_name_{i}")
            with col_m2:
                mod["desc"] = st.text_input(f"Descripción Módulo {i+1}", value=mod["desc"], key=f"mod_desc_{i}")
            with col_m3:
                st.write("")
                st.write("")
                if st.button("🗑️", key=f"del_mod_{i}", help="Eliminar este módulo"):
                    modules_to_remove.append(i)
                    
    if modules_to_remove:
        for idx in sorted(modules_to_remove, reverse=True):
            data["modules"].pop(idx)
        st.rerun()
        
    if st.button("➕ Agregar Nuevo Módulo"):
        data["modules"].append({"name": "Nuevo Módulo", "desc": "Descripción funcional del componente"})
        st.rerun()

# ==========================================
# TAB 2: PLANES Y PRECIOS
# ==========================================
with tab_plans:
    st.markdown("#### 💰 Opciones de Inversión (Tiers de Desarrollo)")
    st.caption("Configura el valor y horas de soporte incluidas en cada nivel de desarrollo.")
    
    cols_plans = st.columns(len(data["plans"]))
    for i, (col, plan) in enumerate(zip(cols_plans, data["plans"])):
        with col:
            rec_class = "recommended" if plan.get("is_recommended", False) else ""
            badge_html = "<span class='badge-ribbon'>★ RECOMENDADO</span>" if plan.get("is_recommended", False) else ""
            
            card_html = (
                f"<div class='pricing-card {rec_class}'>"
                f"<div>"
                f"{badge_html}"
                f"<h3 style='margin: 0; font-size: 18px; font-weight: 800; color: #0F172A;'>{plan['num']}</h3>"
                f"<div style='color: #64748B; font-size: 13px; font-weight: 500; margin-bottom: 8px;'>{plan['name']}</div>"
                f"<div class='support-pill'>✨ {plan['support_hours']} incluidas</div>"
                f"</div>"
                f"</div>"
            )
            st.markdown(card_html, unsafe_allow_html=True)
            
            st.write("")
            plan["name"] = st.text_input(f"Nombre ({plan['num']})", value=plan["name"], key=f"p_name_{i}")
            plan["price"] = st.number_input(
                f"Valor Inversión COP ({plan['num']})",
                value=int(plan["price"]),
                step=100000,
                key=f"p_price_{i}"
            )
            plan["support_hours"] = st.text_input(
                f"Horas Soporte Incluidas ({plan['num']})",
                value=str(plan.get("support_hours", "8 horas")),
                key=f"p_hours_{i}",
                help="Horas de soporte técnico que vienen incluidas en el plan sin costo adicional."
            )
            plan["features"] = st.text_area(
                f"Alcance Resumido ({plan['num']})",
                value=plan["features"],
                height=75,
                key=f"p_feat_{i}"
            )
            plan["is_recommended"] = st.checkbox("Marcar como Recomendado", value=plan.get("is_recommended", False), key=f"p_rec_{i}")
            
    st.markdown("---")
    st.markdown("#### ⚡ Tarifas Adicionales & Servicios Complementarios")
    
    col_ext1, col_ext2, col_ext3 = st.columns(3)
    with col_ext1:
        data["hourly_rate_dev"] = st.number_input(
            "Hora de Desarrollo Adicional (COP)",
            value=int(data["hourly_rate_dev"]),
            step=5000
        )
    with col_ext2:
        data["hourly_rate_supp"] = st.number_input(
            "Hora de Soporte Extra (COP)",
            value=int(data["hourly_rate_supp"]),
            step=5000,
            help="Aplica cuando se agote la bolsa de horas incluida en el plan."
        )
    with col_ext3:
        data["pentest_cost"] = st.text_input(
            "Costo Pruebas de Penetración / OWASP",
            value=str(data["pentest_cost"])
        )
        
    data["pentest_desc"] = st.text_input(
        "Alcance de Pruebas de Penetración y Vulnerabilidades",
        value=data["pentest_desc"]
    )

# ==========================================
# TAB 3: EXCLUSIONES Y LIMITANTES
# ==========================================
with tab_limits:
    col_sec1, col_sec2 = st.columns(2)
    
    with col_sec1:
        st.markdown("#### 🚫 Costos No Asumidos (Exclusiones)")
        st.caption("Costos directos que deben ser provistos o pagados por el cliente.")
        excl_text = st.text_area(
            "Listado de Exclusiones (Una por línea)",
            value="\n".join(data["exclusions"]),
            height=230
        )
        data["exclusions"] = [line.strip() for line in excl_text.split("\n") if line.strip()]

    with col_sec2:
        st.markdown("#### ⚠️ Limitantes y Condiciones Técnicas")
        st.caption("Puntos clave de responsabilidad, entrega en APK y supuestos.")
        lim_text = st.text_area(
            "Listado de Limitantes (Una por línea)",
            value="\n".join(data["limitations"]),
            height=230
        )
        data["limitations"] = [line.strip() for line in lim_text.split("\n") if line.strip()]

    st.markdown("---")
    st.markdown("#### 📦 Entregables Oficiales del Proyecto")
    st.caption("Productos tangibles y accesos que recibirá el cliente al finalizar.")
    deliv_text = st.text_area(
        "Listado de Entregables (Uno por línea)",
        value="\n".join(data["deliverables"]),
        height=160
    )
    data["deliverables"] = [line.strip() for line in deliv_text.split("\n") if line.strip()]

# ==========================================
# TAB 4: PAGOS Y FACTURACIÓN
# ==========================================
with tab_payment:
    st.markdown("#### 💳 Esquema de Liquidación y Condiciones Comerciales")
    
    col_p1, col_p2 = st.columns([2, 2])
    with col_p1:
        plan_names = [f"{p['num']} - {p['name']} ({pdf_generator.format_currency(p['price'])})" for p in data["plans"]]
        sel_idx = st.selectbox(
            "Selecciona el Plan base a liquidar en esta cotización:",
            range(len(plan_names)),
            index=data.get("selected_plan_index", 1),
            format_func=lambda i: plan_names[i]
        )
        data["selected_plan_index"] = sel_idx
        active_plan = data["plans"][sel_idx]

    with col_p2:
        tax_options = [
            "Valor Neto (Persona Natural / No Responsable de IVA)",
            "IVA Régimen Común (19%)",
            "Personalizado / Exento"
        ]
        curr_tax_idx = 0 if "Neto" in data["tax_type"] else (1 if "19%" in data["tax_type"] else 2)
        sel_tax = st.selectbox("Régimen de Impuestos:", tax_options, index=curr_tax_idx)
        data["tax_type"] = sel_tax
        if "19%" in sel_tax:
            data["tax_rate"] = 19.0
        else:
            data["tax_rate"] = 0.0

    st.markdown("---")
    st.markdown("#### 📊 Hitos de Pago (% del Valor de Desarrollo)")
    
    c_h1, c_h2, c_h3, c_h4 = st.columns(4)
    with c_h1:
        data["adv_pct"] = st.number_input("% Anticipo", value=int(data.get("adv_pct", 50)), min_value=0, max_value=100)
    with c_h2:
        data["mid_pct"] = st.number_input("% Hito Web", value=int(data.get("mid_pct", 30)), min_value=0, max_value=100)
    with c_h3:
        data["fin_pct"] = st.number_input("% Entrega Final", value=int(data.get("fin_pct", 20)), min_value=0, max_value=100)
    with c_h4:
        total_pct = data["adv_pct"] + data["mid_pct"] + data["fin_pct"]
        st.metric("Total Porcentajes", f"{total_pct}%")
        if total_pct != 100:
            st.warning("⚠️ La suma debe ser 100%.")

    base_price = float(active_plan["price"])
    tax_amount = base_price * (data["tax_rate"] / 100.0)
    total_amount = base_price + tax_amount
    
    data["payment_terms"] = [
        (f"{data['adv_pct']}% Anticipo", "Al momento de la firma y aprobación de la propuesta comercial.", base_price * (data['adv_pct'] / 100.0)),
        (f"{data['mid_pct']}% Hito Intermedio", "Contra entrega de la versión Web funcional conectada al backend.", base_price * (data['mid_pct'] / 100.0)),
        (f"{data['fin_pct']}% Entrega Final", "Contra entrega de la APK compilada, despliegue final y accesos.", base_price * (data['fin_pct'] / 100.0))
    ]

    st.markdown("#### 💰 Resumen Financiero:")
    rf1, rf2, rf3, rf4 = st.columns(4)
    with rf1:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>Subtotal Desarrollo</div><div class='metric-value'>{pdf_generator.format_currency(base_price)}</div></div>", unsafe_allow_html=True)
    with rf2:
        st.markdown(f"<div class='metric-card'><div class='metric-title'>IVA ({data['tax_rate']}%)</div><div class='metric-value'>{pdf_generator.format_currency(tax_amount)}</div></div>", unsafe_allow_html=True)
    with rf3:
        st.markdown(f"<div class='metric-card accent-indigo'><div class='metric-title'>Total a Pagar</div><div class='metric-value' style='color:#4F46E5'>{pdf_generator.format_currency(total_amount)}</div></div>", unsafe_allow_html=True)
    with rf4:
        supp_disp = active_plan.get('support_hours', 'Incluido')
        st.markdown(f"<div class='metric-card accent-emerald'><div class='metric-title'>Soporte Incluido</div><div class='metric-value' style='color:#15803D'>{supp_disp}</div></div>", unsafe_allow_html=True)

# ==========================================
# TAB 5: VISTA PREVIA Y DESCARGAR PDF
# ==========================================
with tab_preview:
    pdf_bytes = pdf_generator.generate_quotation_pdf(data)
    file_client_clean = data['client_name'].replace(" ", "_") if data['client_name'] else "Cliente"
    file_name = f"Cotizacion_MyFinces_{data['quote_number']}_{file_client_clean}.pdf"
    
    dl_card_html = (
        '<div class="download-hero-card">'
        '<h3 style="margin: 0; color: #0F172A; font-size: 20px; font-weight: 800;">📄 Propuesta Lista para Descarga</h3>'
        f'<p style="margin: 4px 0 0 0; color: #64748B; font-size: 13.5px;">Documento PDF corporativo de alta resolución listo para enviar al cliente ({len(pdf_bytes):,} bytes).</p>'
        '</div>'
    )
    st.markdown(dl_card_html, unsafe_allow_html=True)
    
    col_d1, col_d2 = st.columns([1, 2])
    with col_d1:
        st.download_button(
            label="📥 Descargar Propuesta en PDF",
            data=pdf_bytes,
            file_name=file_name,
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )
    with col_d2:
        st.info(f"📁 Archivo: **{file_name}** | Generado automáticamente con diseño ejecutivo.")

    st.markdown("---")
    st.markdown("#### 👁️ Previsualización del Documento:")
    
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="950" type="application/pdf" style="border: 1px solid #CBD5E1; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
