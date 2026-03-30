"""
report_generator.py — PDF health report generation with ReportLab
"""

import os
import io
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------
BRAND_BLUE = colors.HexColor("#1A73E8")
BRAND_DARK = colors.HexColor("#0D1B2A")
BRAND_LIGHT_BG = colors.HexColor("#F0F4FF")
STATUS_COLORS = {
    "Normal":   colors.HexColor("#34A853"),
    "Low":      colors.HexColor("#FBBC04"),
    "High":     colors.HexColor("#EA4335"),
    "Critical": colors.HexColor("#B71C1C"),
}
SEVERITY_COLORS = {
    "Critical": colors.HexColor("#B71C1C"),
    "High":     colors.HexColor("#EA4335"),
    "Moderate": colors.HexColor("#FBBC04"),
    "Low":      colors.HexColor("#34A853"),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _status_color(status: str) -> colors.Color:
    return STATUS_COLORS.get(status, colors.grey)


def _severity_color(severity: str) -> colors.Color:
    return SEVERITY_COLORS.get(severity, colors.grey)


def _build_styles():
    base = getSampleStyleSheet()
    custom = {
        "title": ParagraphStyle(
            "title", parent=base["Title"],
            fontSize=22, textColor=BRAND_BLUE, spaceAfter=4,
            fontName="Helvetica-Bold",
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"],
            fontSize=10, textColor=colors.grey, spaceAfter=12,
            fontName="Helvetica",
        ),
        "section": ParagraphStyle(
            "section", parent=base["Heading2"],
            fontSize=13, textColor=BRAND_DARK, spaceBefore=14, spaceAfter=6,
            fontName="Helvetica-Bold",
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"],
            fontSize=9, leading=14, fontName="Helvetica",
        ),
        "footer": ParagraphStyle(
            "footer", parent=base["Normal"],
            fontSize=7, textColor=colors.grey, alignment=TA_CENTER,
            fontName="Helvetica",
        ),
        "risk_title": ParagraphStyle(
            "risk_title", fontName="Helvetica-Bold",
            fontSize=9, textColor=BRAND_DARK,
        ),
        "risk_body": ParagraphStyle(
            "risk_body", fontName="Helvetica",
            fontSize=8, textColor=colors.HexColor("#444444"), leading=12,
        ),
    }
    return {**{k: base[k] for k in base.byName}, **custom}


# ---------------------------------------------------------------------------
# PDF builder
# ---------------------------------------------------------------------------

def generate_pdf(
    report_id: int,
    filename: str,
    upload_time: str,
    analysis_result: Dict[str, Any],
    risk_summary: Dict[str, Any],
    extracted_text: Optional[str] = None,
) -> bytes:
    """
    Build a PDF health report and return as bytes.
    """
    buffer = io.BytesIO()
    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2 * cm,
    )
    styles = _build_styles()
    W, H = A4
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        W - doc.leftMargin - doc.rightMargin,
        H - doc.topMargin - doc.bottomMargin,
        id="main"
    )

    def _header_footer(canvas, doc):
        canvas.saveState()
        # Header bar
        canvas.setFillColor(BRAND_BLUE)
        canvas.rect(0, H - 1.8 * cm, W, 1.8 * cm, fill=True, stroke=False)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 13)
        canvas.drawString(2 * cm, H - 1.2 * cm, "🩺  MedScan AI")
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(
            W - 2 * cm, H - 1.2 * cm,
            f"Report #{report_id}  |  {upload_time[:19].replace('T', '  ')}"
        )
        # Footer
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.setFont("Helvetica", 7)
        canvas.drawCentredString(
            W / 2, 1 * cm,
            "MedScan AI — Intelligent Medical Report Analyzer  |  "
            "This report is for informational purposes only. Consult a qualified physician."
        )
        canvas.restoreState()

    doc.addPageTemplates([
        PageTemplate(id="main", frames=[frame], onPage=_header_footer)
    ])

    story = []

    # -----------------------------------------------------------------------
    # Title block
    # -----------------------------------------------------------------------
    summary = analysis_result.get("summary", {})
    overall = summary.get("overall_status", "Unknown")
    overall_color = {
        "Healthy": colors.HexColor("#34A853"),
        "Needs Attention": colors.HexColor("#EA4335"),
        "Critical": colors.HexColor("#B71C1C"),
        "Insufficient Data": colors.grey,
    }.get(overall, colors.grey)

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Patient Health Summary", styles["title"]))
    story.append(Paragraph(f"Source file: <i>{filename}</i>", styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1, color=BRAND_BLUE))
    story.append(Spacer(1, 0.3 * cm))

    # Overall status badge (table trick)
    status_table = Table(
        [[
            Paragraph("<b>Overall Health Status</b>", styles["body"]),
            Paragraph(
                f'<font color="white"><b>{overall}</b></font>',
                ParagraphStyle("sb", fontName="Helvetica-Bold", fontSize=10, textColor=colors.white)
            ),
        ]],
        colWidths=["60%", "40%"],
    )
    status_table.setStyle(TableStyle([
        ("BACKGROUND", (1, 0), (1, 0), overall_color),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("ALIGN", (1, 0), (1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 0.4 * cm))

    # Quick stats row
    stats = [
        ["Parameters Detected", str(summary.get("total_detected", 0))],
        ["Abnormal Values", str(summary.get("abnormal_count", 0))],
        ["Risk Conditions", str(summary.get("risk_count", 0))],
    ]
    stats_table_data = [[
        Paragraph(f"<b>{s[0]}</b><br/><font size='14'>{s[1]}</font>", styles["body"])
        for s in stats
    ]]
    st = Table(stats_table_data, colWidths=["33%", "33%", "34%"])
    st.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_LIGHT_BG),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
    ]))
    story.append(st)
    story.append(Spacer(1, 0.6 * cm))

    # -----------------------------------------------------------------------
    # Parameter table
    # -----------------------------------------------------------------------
    parameters = analysis_result.get("parameters", {})
    if parameters:
        story.append(Paragraph("Detected Parameters", styles["section"]))
        header = ["Parameter", "Value", "Unit", "Normal Range", "Status"]
        rows = [header]
        for param_name, data in parameters.items():
            display_name = param_name.replace("BloodPressure", "BP ")
            rows.append([
                display_name,
                str(data["value"]),
                data["unit"],
                f"{data['range_low']} – {data['range_high']}",
                data["status"],
            ])

        param_table = Table(rows, colWidths=["28%", "14%", "16%", "24%", "18%"])
        ts = TableStyle([
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            # Body
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BRAND_LIGHT_BG]),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CCCCCC")),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ])
        # Color-code status column
        for i, (pname, data) in enumerate(parameters.items(), start=1):
            cell_color = _status_color(data["status"])
            ts.add("TEXTCOLOR", (4, i), (4, i), cell_color)
            ts.add("FONTNAME",  (4, i), (4, i), "Helvetica-Bold")

        param_table.setStyle(ts)
        story.append(param_table)
        story.append(Spacer(1, 0.6 * cm))

    # -----------------------------------------------------------------------
    # Risk conditions
    # -----------------------------------------------------------------------
    risks = analysis_result.get("risks", [])
    if risks:
        story.append(Paragraph("Identified Risk Conditions", styles["section"]))
        for risk in risks:
            sev_color = _severity_color(risk["severity"])
            risk_row = Table(
                [[
                    Paragraph(f"<b>{risk['name']}</b>", styles["risk_title"]),
                    Paragraph(
                        f'<font color="white"> {risk["severity"]} </font>',
                        ParagraphStyle(
                            "rb", fontName="Helvetica-Bold", fontSize=8, textColor=colors.white
                        )
                    ),
                ]],
                colWidths=["75%", "25%"],
            )
            risk_row.setStyle(TableStyle([
                ("BACKGROUND", (1, 0), (1, 0), sev_color),
                ("ALIGN", (1, 0), (1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(risk_row)
            story.append(
                Paragraph(f"💡 {risk['recommendation']}", styles["risk_body"])
            )
            story.append(Spacer(1, 0.25 * cm))

        story.append(Spacer(1, 0.4 * cm))

    # -----------------------------------------------------------------------
    # Disclaimer
    # -----------------------------------------------------------------------
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "<i>This report was generated automatically by MedScan AI. "
        "Values are extracted using OCR and may contain errors. "
        "Always consult a qualified healthcare professional before making medical decisions.</i>",
        styles["body"]
    ))

    doc.build(story)
    return buffer.getvalue()
