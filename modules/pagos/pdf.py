from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from core.utils import MESES

def generar_comprobante(cuota) -> BytesIO:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            rightMargin=2.5*cm, leftMargin=2.5*cm,
                            topMargin=2.5*cm, bottomMargin=2.5*cm)
    styles = getSampleStyleSheet()

    s_title = ParagraphStyle("s_title", parent=styles["Heading1"],
                              fontSize=18, alignment=TA_CENTER, spaceAfter=4)
    s_sub = ParagraphStyle("s_sub", parent=styles["Normal"],
                            fontSize=10, alignment=TA_CENTER, spaceAfter=2,
                            textColor=colors.HexColor("#6b7280"))
    s_label = ParagraphStyle("s_label", parent=styles["Heading3"],
                              fontSize=11, alignment=TA_CENTER, spaceAfter=16,
                              textColor=colors.HexColor("#1e1b4b"))
    s_footer = ParagraphStyle("s_footer", parent=styles["Normal"],
                               fontSize=8, alignment=TA_CENTER,
                               textColor=colors.HexColor("#9ca3af"))

    casa = cuota.casa
    residentes = [r.nombre for r in casa.residentes if r.activo]
    res_nombres = ", ".join(residentes) if residentes else "—"

    story = [
        Paragraph("Villa Los Ceibos", s_title),
        Paragraph("Urbanización Residencial — Guayas, Ecuador", s_sub),
        Spacer(1, 0.4*cm),
        Paragraph("COMPROBANTE DE PAGO DE ALÍCUOTA", s_label),
    ]

    recargo = cuota.recargo or 0
    es_extra = getattr(cuota, "tipo", "ordinaria") == "extraordinaria"
    concepto = (cuota.concepto or "").strip()

    data = [
        ["Comprobante N°", f"CUO-{cuota.id:05d}"],
        ["Fecha de emisión", datetime.now().strftime("%d/%m/%Y  %H:%M")],
        ["", ""],
        ["Casa / Manzana", f"Manzana {casa.manzana} — Casa {casa.numero}"],
        ["Residente(s)", res_nombres],
        ["", ""],
        ["Concepto", concepto if es_extra and concepto else "Alícuota ordinaria"],
        ["Período facturado", f"{MESES[cuota.mes]}  {cuota.anio}"],
        ["Monto", f"$ {cuota.monto:.2f}"],
    ]
    if recargo > 0:
        data.append(["Recargo por mora", f"$ {recargo:.2f}"])
        data.append(["Total pagado", f"$ {cuota.monto + recargo:.2f}"])
    data += [
        ["Fecha de pago", cuota.fecha_pago or "—"],
        ["Método de pago", (cuota.metodo_pago or "efectivo").capitalize()],
        ["Observaciones", cuota.observacion or "—"],
        ["", ""],
        ["ESTADO", "PAGADO"],
    ]

    gray_light = colors.HexColor("#f9fafb")
    green = colors.HexColor("#16a34a")

    tbl = Table(data, colWidths=[4.5*cm, 11*cm])
    tbl.setStyle(TableStyle([
        ("FONTSIZE",       (0, 0),  (-1, -1), 10),
        ("FONTNAME",       (0, 0),  (0, -1),  "Helvetica-Bold"),
        ("FONTNAME",       (1, 0),  (1, -1),  "Helvetica"),
        ("TOPPADDING",     (0, 0),  (-1, -1), 7),
        ("BOTTOMPADDING",  (0, 0),  (-1, -1), 7),
        ("LEFTPADDING",    (0, 0),  (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 0),  (-1, -2), [colors.white, gray_light]),
        ("GRID",           (0, 0),  (-1, -2), 0.5, colors.HexColor("#e5e7eb")),

        ("BACKGROUND",     (0, -1), (-1, -1), green),
        ("TEXTCOLOR",      (0, -1), (-1, -1), colors.white),
        ("FONTNAME",       (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",       (0, -1), (-1, -1), 12),
        ("ALIGN",          (0, -1), (-1, -1), "CENTER"),
        ("TOPPADDING",     (0, -1), (-1, -1), 10),
        ("BOTTOMPADDING",  (0, -1), (-1, -1), 10),
    ]))

    story.append(tbl)
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("Este documento es válido como constancia de pago.", s_footer))
    story.append(Paragraph(
        f"Generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')} — Sistema Villa Los Ceibos",
        s_footer,
    ))

    doc.build(story)
    buf.seek(0)
    return buf
