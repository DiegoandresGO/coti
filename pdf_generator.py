import os
import io
from xml.sax.saxutils import escape
import storage
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable
)
from reportlab.pdfgen import canvas

# ==========================================
# PALETA DE COLOR EJECUTIVA MYFINCES (Alta Estética)
# ==========================================
PRIMARY_BRAND     = colors.HexColor("#4F46E5")  # Indigo Eléctrico
PRIMARY_DARK      = colors.HexColor("#0B0F19")  # Midnight Dark Navy
SECONDARY_NAVY    = colors.HexColor("#1E293B")  # Slate 800
ACCENT_VIOLET     = colors.HexColor("#6366F1")  # Indigo 500
ACCENT_LIGHT      = colors.HexColor("#EEF2FF")  # Indigo 50 (Fondos de tarjeta suave)
ACCENT_BORDER     = colors.HexColor("#C7D2FE")  # Indigo 200 (Bordes destacados)

TEXT_TITLE        = colors.HexColor("#0B0F19")  # Título principal
TEXT_MAIN         = colors.HexColor("#1E293B")  # Slate 800 (Texto de lectura)
TEXT_MUTED        = colors.HexColor("#64748B")  # Slate 500 (Texto secundario)
BORDER_LIGHT      = colors.HexColor("#E2E8F0")  # Slate 200 (Bordes sutiles)
BG_CARD           = colors.HexColor("#F8FAFC")  # Slate 50 (Fondo sutil)

# Badges y estados
BG_EMERALD        = colors.HexColor("#F0FDF4")  # Emerald 50
BORDER_EMERALD    = colors.HexColor("#86EFAC")  # Emerald 300
COLOR_EMERALD     = colors.HexColor("#15803D")  # Emerald 700

BG_ROSE           = colors.HexColor("#FFF1F2")  # Rose 50
BORDER_ROSE       = colors.HexColor("#FECDD3")  # Rose 200
COLOR_ROSE        = colors.HexColor("#9F1239")  # Rose 800

BG_AMBER          = colors.HexColor("#FFFBEB")  # Amber 50
BORDER_AMBER      = colors.HexColor("#FDE68A")  # Amber 200
COLOR_AMBER       = colors.HexColor("#B45309")  # Amber 700


class NumberedCanvas(canvas.Canvas):
    """Canvas corporativo con barra superior ejecutiva, pie de página y paginación automática."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        self.saveState()
        
        # Barra superior decorativa con doble tono (Indigo + Slate)
        self.setFillColor(PRIMARY_BRAND)
        self.rect(36, 11 * inch - 18, 8.5 * inch - 72, 3.5, fill=True, stroke=False)
        
        # Pie de página elegante
        self.setFont("Helvetica", 8)
        self.setFillColor(TEXT_MUTED)
        
        # Línea divisoria del pie
        self.setStrokeColor(BORDER_LIGHT)
        self.setLineWidth(0.6)
        self.line(36, 38, 8.5 * inch - 36, 38)
        
        # Textos de pie de página
        self.drawString(36, 26, "Propuesta Técnico-Comercial Confidencial · myfinances.barcam.site")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(8.5 * inch - 36, 26, page_str)
        
        self.restoreState()


def format_currency(value):
    """Formateo formal de moneda colombiana COP."""
    try:
        val_float = float(value)
        return f"$ {val_float:,.0f} COP".replace(",", ".")
    except (ValueError, TypeError):
        return str(value)


def generate_quotation_pdf(data):
    """Genera la cotización ejecutiva con alta calidad estética y diseño profesional."""
    buffer = io.BytesIO()
    margin = 36 # 0.5 pulgada
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin + 12,
        bottomMargin=margin + 15
    )
    
    styles = getSampleStyleSheet()
    
    # Jerarquía tipográfica refinada
    doc_supertitle = ParagraphStyle(
        'DocSuper',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=PRIMARY_BRAND,
        spaceAfter=3
    )
    
    company_title_style = ParagraphStyle(
        'CompanyTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=PRIMARY_DARK,
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=TEXT_MUTED
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=PRIMARY_DARK,
        spaceBefore=10,
        spaceAfter=5
    )
    
    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=TEXT_MAIN
    )
    
    body_bold = ParagraphStyle(
        'BodyBoldCustom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    body_muted = ParagraphStyle(
        'BodyMuted',
        parent=body_style,
        textColor=TEXT_MUTED,
        fontSize=8,
        leading=10.5
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=TEXT_MAIN
    )
    
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell_style,
        fontName='Helvetica-Bold'
    )
    
    story = []
    
    # ==========================
    # 1. ENCABEZADO Y METADATOS
    # ==========================
    company_name = data.get("company_name", "BARCAM SOFTWARE LABS")
    company_lead = data.get("company_lead", "Desarrollo de Software & Soluciones Web / Móviles")
    company_contact = data.get("company_contact", "contacto@barcam.site | +57 300 000 0000 | Colombia")
    
    quote_number = data.get("quote_number", "COT-2026-001")
    quote_date = data.get("quote_date", datetime.today().strftime("%d/%m/%Y"))
    quote_validity = data.get("quote_validity", "15 días calendario")
    
    client_name = data.get("client_name", "Cliente")
    client_company = data.get("client_company", "Empresa Cliente")
    client_contact = data.get("client_contact", "cliente@empresa.com")
    
    left_header = [
        Paragraph("PROPUESTA COMERCIAL & TÉCNICA", doc_supertitle),
        Paragraph(company_name, company_title_style),
        Paragraph(company_lead, subtitle_style),
        Spacer(1, 2),
        Paragraph(company_contact, body_muted)
    ]
    
    right_meta_data = [
        [Paragraph("<b>Propuesta N°:</b>", body_style), Paragraph(f"<b>{quote_number}</b>", ParagraphStyle('QN', parent=body_style, textColor=PRIMARY_BRAND))],
        [Paragraph("<b>Fecha de Emisión:</b>", body_style), Paragraph(quote_date, body_style)],
        [Paragraph("<b>Vigencia:</b>", body_style), Paragraph(quote_validity, body_style)],
        [Paragraph("<b>Plataforma:</b>", body_style), Paragraph("myfinances.barcam.site", ParagraphStyle('PL', parent=body_muted, textColor=PRIMARY_BRAND))]
    ]
    meta_table = Table(right_meta_data, colWidths=[85, 110])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), ACCENT_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, ACCENT_BORDER),
        ('INNERGRID', (0,0), (-1,-1), 0.5, ACCENT_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
    ]))
    
    header_table = Table([[left_header, meta_table]], colWidths=[340, 200])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER_LIGHT, spaceAfter=8))
    
    # ==========================
    # 2. INFORMACIÓN DEL CLIENTE Y PROYECTO (Card con Acento)
    # ==========================
    client_info_table = Table([
        [
            Paragraph("<b>CLIENTE / RECEPTOR DE LA PROPUESTA:</b>", ParagraphStyle('CT', parent=body_muted, fontSize=7.5, fontName='Helvetica-Bold', textColor=PRIMARY_BRAND)),
            Paragraph("<b>PROYECTO & SOLUCIÓN A DESARROLLAR:</b>", ParagraphStyle('PT', parent=body_muted, fontSize=7.5, fontName='Helvetica-Bold', textColor=PRIMARY_BRAND))
        ],
        [
            Paragraph(f"<b>{client_name}</b><br/>{client_company}<br/><font color='#64748B'>{client_contact}</font>", body_style),
            Paragraph(f"<b>{data.get('project_title', 'MyFinces — Control de Finanzas Personales')}</b><br/><font color='#4F46E5'>{data.get('project_category', 'Ecosistema Web & Aplicación Móvil APK')}</font><br/><font color='#64748B'>Ingresos, egresos, gastos fijos, deudas y metas de ahorro</font>", body_style)
        ]
    ], colWidths=[270, 270])
    
    client_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
        ('LINEBEFORE', (0,0), (0,-1), 3, PRIMARY_BRAND),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 5.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5.5),
        ('LEFTPADDING', (0,0), (-1,-1), 9),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(client_info_table)
    story.append(Spacer(1, 8))
    
    # ==========================
    # 3. DESCRIPCIÓN DEL DESARROLLO (Callout Card)
    # ==========================
    story.append(Paragraph("<font color='#4F46E5'><b>01.</b></font> DESCRIPCIÓN Y OBJETIVO DEL DESARROLLO", section_title_style))
    desc_text = data.get("project_description", (
        "Desarrollo e implementación del ecosistema de software <b>MyFinces</b> para el control integral de finanzas personales. "
        "Permite registrar ingresos, egresos, gastos fijos periódicos, seguimiento a deudas activas y conciliación de metas de ahorro "
        "en un libro contable centralizado. La solución incluye la aplicación web responsive conectada a backend en la nube, "
        "el panel administrativo de gestión y la compilación de la aplicación móvil en formato APK optimizada."
    ))
    
    desc_card = Table([[Paragraph(desc_text, body_style)]], colWidths=[540])
    desc_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
        ('LINEBEFORE', (0,0), (0,-1), 3, PRIMARY_BRAND),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 9),
        ('RIGHTPADDING', (0,0), (-1,-1), 9),
    ]))
    story.append(desc_card)
    story.append(Spacer(1, 8))
    
    # ==========================
    # 4. MÓDULOS Y ALCANCE FUNCIONAL
    # ==========================
    story.append(Paragraph("<font color='#4F46E5'><b>02.</b></font> MÓDULOS DE ALCANCE FUNCIONAL", section_title_style))
    
    modules = data.get("modules", [
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
    ])
    
    mod_table_data = [[
        Paragraph("Módulo / Componente", table_header_style),
        Paragraph("Descripción del Alcance Técnico-Funcional", table_header_style)
    ]]
    for idx, m in enumerate(modules, start=1):
        mod_table_data.append([
            Paragraph(f"<font color='#4F46E5'><b>MOD-{idx:02d}</b></font><br/><b>{m['name']}</b>", table_cell_style),
            Paragraph(m['desc'], table_cell_style)
        ])
    
    mod_table = Table(mod_table_data, colWidths=[175, 365])
    mod_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_DARK),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD])
    ]))
    story.append(mod_table)
    story.append(Spacer(1, 9))
    
    # ==========================
    # 5. PLANES DE INVERSIÓN (TIERS)
    # ==========================
    story.append(Paragraph("<font color='#4F46E5'><b>03.</b></font> PLANES DE INVERSIÓN Y OPCIONES DE DESARROLLO", section_title_style))
    story.append(Paragraph(
        "Estructura en tres (3) niveles de inversión según profundidad del proyecto y bolsa de soporte técnico incluida en cada opción:",
        body_muted
    ))
    story.append(Spacer(1, 5))
    
    plans = data.get("plans", [
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
    ])
    
    plans_table_data = [[
        Paragraph("Nivel de Plan", table_header_style),
        Paragraph("Inversión Total (COP)", table_header_style),
        Paragraph("Soporte Incluido", table_header_style),
        Paragraph("Alcance y Entregables del Plan", table_header_style)
    ]]
    
    for p in plans:
        is_rec = p.get("is_recommended", False)
        badge_text = "<font color='#4F46E5'><b>★ RECOMENDADO</b></font><br/>" if is_rec else ""
        hours_val = p.get('support_hours', 'Incluido')
        if "incluidas" not in str(hours_val).lower() and "incluido" not in str(hours_val).lower():
            hours_val = f"{hours_val} incluidas"
            
        plans_table_data.append([
            Paragraph(f"{badge_text}<b>{p['num']}</b><br/><font color='#64748B'>{p['name']}</font>", table_cell_style),
            Paragraph(f"<b>{format_currency(p['price'])}</b>", ParagraphStyle('PVal', parent=table_cell_bold, textColor=PRIMARY_BRAND)),
            Paragraph(f"<b>{hours_val}</b><br/><font color='#64748B' size=7.5>Sin cobro mensual</font>", table_cell_style),
            Paragraph("<br/>".join(f"• {escape(i)}" for i in storage.plan_items(p.get('features'))), table_cell_style)
        ])
    
    plans_table = Table(plans_table_data, colWidths=[120, 120, 110, 190])
    plans_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_DARK),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 5.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_CARD])
    ]))
    story.append(plans_table)
    story.append(Spacer(1, 9))
    
    # ==========================
    # 6. SERVICIOS ADICIONALES Y TARIFAS
    # ==========================
    story.append(Paragraph("<font color='#4F46E5'><b>04.</b></font> SERVICIOS COMPLEMENTARIOS Y BOLSA DE HORAS", section_title_style))
    
    hourly_dev = data.get("hourly_rate_dev", 75000)
    hourly_supp = data.get("hourly_rate_supp", 50000)
    pentest_cost = data.get("pentest_cost", "$ 800.000 COP")
    pentest_desc = data.get("pentest_desc", (
        "Auditoría técnica OWASP, pruebas de penetración contra inyecciones y fugas de datos en APIs backend y aplicación web, con informe."
    ))
    
    extras_data = [
        [
            Paragraph("<b>Pruebas de Penetración y Vulnerabilidades</b>", table_cell_bold),
            Paragraph(pentest_desc, table_cell_style),
            Paragraph(f"<b>{pentest_cost if isinstance(pentest_cost, str) else format_currency(pentest_cost)}</b>", ParagraphStyle('ExC', parent=table_cell_style, textColor=PRIMARY_BRAND))
        ],
        [
            Paragraph("<b>Hora de Desarrollo Adicional</b>", table_cell_bold),
            Paragraph("Para nuevos requerimientos, funciones no previstas o cambios de diseño fuera del alcance pactado.", table_cell_style),
            Paragraph(f"<b>{format_currency(hourly_dev)} / hora</b>", table_cell_style)
        ],
        [
            Paragraph("<b>Hora de Soporte Técnico Extra</b>", table_cell_bold),
            Paragraph("Aplica exclusivamente una vez agotada la bolsa de soporte técnico incluida en el plan contratado.", table_cell_style),
            Paragraph(f"<b>{format_currency(hourly_supp)} / hora</b>", table_cell_style)
        ]
    ]
    
    extras_table = Table(extras_data, colWidths=[150, 270, 120])
    extras_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD)
    ]))
    story.append(extras_table)
    story.append(Spacer(1, 9))
    
    # ==========================
    # 7. COSTOS NO ASUMIDOS (EXCLUSIONES)
    # ==========================
    story.append(Paragraph("<font color='#4F46E5'><b>05.</b></font> COSTOS NO ASUMIDOS (EXCLUSIONES DE INFRAESTRUCTURA)", section_title_style))
    exclusions = data.get("exclusions", [
        "<b>Servidor / VPS / Hosting:</b> El costo de infraestructura en la nube corre por cuenta directa del cliente.",
        "<b>Dominio y Certificados SSL:</b> La titularidad y renovación del dominio web es responsabilidad del cliente.",
        "<b>Consumo de APIs de Inteligencia Artificial:</b> Tokens facturados directamente por proveedores externos (OpenAI, Gemini, etc.).",
        "<b>Licenciamiento de Terceros y Cuentas:</b> Membresías de tiendas (Google Play $25 USD / Apple $99 USD/año).",
        "<b>Tiempos de Aprobación de Tiendas:</b> Los tiempos de validación de Google o Apple escapan al control del equipo de desarrollo."
    ])
    excl_items = [[Paragraph(f"• {ex}", body_style)] for ex in exclusions]
    excl_table = Table(excl_items, colWidths=[540])
    excl_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_ROSE),
        ('BOX', (0,0), (-1,-1), 1, BORDER_ROSE),
        ('LINEBEFORE', (0,0), (0,-1), 3, COLOR_ROSE),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 9),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(excl_table)
    story.append(Spacer(1, 9))
    
    # ==========================
    # 8. LIMITANTES Y CONDICIONES TÉCNICAS
    # ==========================
    story.append(Paragraph("<font color='#4F46E5'><b>06.</b></font> LIMITANTES Y CONDICIONES TÉCNICAS", section_title_style))
    limitations = data.get("limitations", [
        "<b>Entrega en formato APK:</b> La app móvil se entrega como paquete instalador APK firmado listo para Android.",
        "<b>Instalación y Desconocimiento de APK:</b> La distribución interna o instalación en terminales de usuarios finales es gestionada por el cliente.",
        "<b>Accesos al Servidor:</b> La entrega a tiempo depende del suministro oportuno de accesos a servidores y credenciales por parte del cliente.",
        "<b>Documentación Faltante:</b> Requerimientos no contemplados en esta cotización se liquidarán bajo la bolsa de horas de desarrollo.",
        "<b>Garantía Técnica:</b> 30 días calendario de soporte y resolución de bugs sin costo tras la entrega formal."
    ])
    lim_items = [[Paragraph(f"• {lim}", body_style)] for lim in limitations]
    lim_table = Table(lim_items, colWidths=[540])
    lim_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_CARD),
        ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
        ('LINEBEFORE', (0,0), (0,-1), 3, SECONDARY_NAVY),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 9),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(lim_table)
    story.append(Spacer(1, 9))
    
    # ==========================
    # 10. FORMAS DE PAGO Y CONDICIONES COMERCIALES
    # ==========================
    selected_plan_idx = data.get("selected_plan_index", 1)
    sel_plan = plans[min(max(selected_plan_idx, 0), len(plans)-1)]
    
    tax_type = data.get("tax_type", "Valor Neto (Persona Natural / No Responsable de IVA)")
    tax_rate = data.get("tax_rate", 0.0)
    base_val = float(sel_plan.get("price", 4000000))
    totals = storage.compute_totals(data, base_val)
    tax_val = totals["iva"]
    total_val = totals["total"]
    retentions = totals["retentions"]
    
    adv_p = data.get("adv_pct", 50)
    mid_p = data.get("mid_pct", 30)
    fin_p = data.get("fin_pct", 20)
    
    payment_terms = data.get("payment_terms", [
        (f"{adv_p}% Anticipo", "Al momento de la firma y aprobación de la propuesta comercial.", base_val * (adv_p / 100.0)),
        (f"{mid_p}% Hito Intermedio", "Contra entrega de la versión Web funcional conectada al backend.", base_val * (mid_p / 100.0)),
        (f"{fin_p}% Entrega Final", "Contra entrega de la APK compilada, despliegue final y accesos.", base_val * (fin_p / 100.0))
    ])
    
    pay_rows = [
        [
            Paragraph("Hito de Pago", table_header_style),
            Paragraph("Condición de Cumplimiento", table_header_style),
            Paragraph("Valor (COP)", table_header_style)
        ]
    ]
    for term, cond, val in payment_terms:
        pay_rows.append([
            Paragraph(f"<b>{term}</b>", table_cell_bold),
            Paragraph(cond, table_cell_style),
            Paragraph(format_currency(val), table_cell_bold)
        ])
    
    pay_rows.append([
        Paragraph("<b>Subtotal Desarrollo:</b>", table_cell_bold),
        Paragraph(f"Plan seleccionado: <b>{sel_plan['num']} - {sel_plan['name']}</b>", table_cell_style),
        Paragraph(f"<b>{format_currency(base_val)}</b>", table_cell_bold)
    ])
    if tax_rate > 0:
        pay_rows.append([
            Paragraph(f"<b>IVA ({tax_rate}%):</b>", table_cell_style),
            Paragraph("", table_cell_style),
            Paragraph(f"{format_currency(tax_val)}", table_cell_style)
        ])
    pay_rows.append([
        Paragraph("<b>TOTAL FACTURA:</b>" if retentions else "<b>TOTAL A PAGAR:</b>", ParagraphStyle('TotL', parent=table_cell_bold, fontSize=9.5, textColor=PRIMARY_BRAND)),
        Paragraph(f"Régimen: {tax_type}", table_cell_style),
        Paragraph(f"<b>{format_currency(total_val)}</b>", ParagraphStyle('TotV', parent=table_cell_bold, fontSize=9.5, textColor=PRIMARY_BRAND))
    ])
    if retentions:
        ret_style = ParagraphStyle('RetV', parent=table_cell_style, textColor=colors.HexColor('#E11D48'))
        for r in retentions:
            pay_rows.append([
                Paragraph(f"<b>- {r['label']}</b>", table_cell_style),
                Paragraph(r["desc"], table_cell_style),
                Paragraph(f"- {format_currency(r['value'])}", ret_style)
            ])
        pay_rows.append([
            Paragraph("<b>NETO A PAGAR:</b>", ParagraphStyle('NetL', parent=table_cell_bold, fontSize=9.5, textColor=PRIMARY_BRAND)),
            Paragraph("Total factura menos retenciones", table_cell_style),
            Paragraph(f"<b>{format_currency(totals['neto'])}</b>", ParagraphStyle('NetV', parent=table_cell_bold, fontSize=9.5, textColor=PRIMARY_BRAND))
        ])
    
    pay_table = Table(pay_rows, colWidths=[120, 290, 130])
    pay_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_DARK),
        ('BOX', (0,0), (-1,-1), 1, BORDER_LIGHT),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_LIGHT),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
        ('LEFTPADDING', (0,0), (-1,-1), 7),
        ('RIGHTPADDING', (0,0), (-1,-1), 7),
        ('BACKGROUND', (0,-1), (-1,-1), ACCENT_LIGHT),
        ('LINEABOVE', (0,-1), (-1,-1), 1.5, PRIMARY_BRAND)
    ]))
    
    pay_section = [
        Paragraph("<font color='#4F46E5'><b>07.</b></font> FORMAS DE PAGO Y CONDICIONES COMERCIALES", section_title_style),
        Spacer(1, 4),
        pay_table
    ]
    story.append(KeepTogether(pay_section))
    
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()
