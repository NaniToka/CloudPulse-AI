"""
Enterprise PDF Report Generator for AI Log Analysis using ReportLab.
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Theme Colors
PRIMARY_COLOR = colors.HexColor("#0f172a")  # Deep Slate
BRAND_BLUE = colors.HexColor("#3b82f6")     # Brand Accent
SUCCESS_GREEN = colors.HexColor("#10b981")  # Emerald
WARN_AMBER = colors.HexColor("#f59e0b")     # Amber
DANGER_ROSE = colors.HexColor("#f43f5e")    # Rose
CARD_BG = colors.HexColor("#f8fafc")        # Light Slate
BORDER_COLOR = colors.HexColor("#e2e8f0")   # Slate Border


def generate_log_analysis_pdf(analysis_data: dict[str, Any]) -> bytes:
    """
    Generates a PDF document for a log analysis record.
    Returns the binary content (bytes).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=PRIMARY_COLOR,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=12,
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=PRIMARY_COLOR,
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyTextCustom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    )
    code_style = ParagraphStyle(
        "CodeSnippet",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0f172a"),
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("CloudPulse AI", title_style))
    story.append(Paragraph("Automated SRE Root Cause Analysis & Log Diagnostic Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=BRAND_BLUE, spaceAfter=14))

    # 2. Metadata Grid
    filename = analysis_data.get("filename", "unknown.log")
    created_at = analysis_data.get("created_at")
    date_str = created_at.strftime("%Y-%m-%d %H:%M:%S UTC") if isinstance(created_at, datetime) else str(created_at or "N/A")
    severity = (analysis_data.get("severity") or "UNKNOWN").upper()
    confidence = f"{int((analysis_data.get('confidence_score') or 0.95) * 100)}%"
    total_lines = str(analysis_data.get("total_lines", 0))
    error_count = str(analysis_data.get("error_count", 0))
    warn_count = str(analysis_data.get("warning_count", 0))
    crit_count = str(analysis_data.get("critical_count", 0))
    engine_used = analysis_data.get("engine_used", "Google Gemini / Local SRE Engine")

    meta_table_data = [
        [
            Paragraph("<b>Target Log File:</b>", body_style),
            Paragraph(filename, body_style),
            Paragraph("<b>Analysis Date:</b>", body_style),
            Paragraph(date_str, body_style),
        ],
        [
            Paragraph("<b>Severity Assessment:</b>", body_style),
            Paragraph(f"<b>{severity}</b>", body_style),
            Paragraph("<b>AI Confidence:</b>", body_style),
            Paragraph(confidence, body_style),
        ],
        [
            Paragraph("<b>Scanned Lines:</b>", body_style),
            Paragraph(total_lines, body_style),
            Paragraph("<b>Errors / Warnings:</b>", body_style),
            Paragraph(f"{error_count} ERR / {warn_count} WARN / {crit_count} CRIT", body_style),
        ],
        [
            Paragraph("<b>Diagnostic Engine:</b>", body_style),
            Paragraph(engine_used, body_style),
            Paragraph("<b>Platform:</b>", body_style),
            Paragraph("CloudPulse-AI Observability", body_style),
        ],
    ]

    meta_table = Table(meta_table_data, colWidths=[1.3 * inch, 2.3 * inch, 1.3 * inch, 2.3 * inch])
    meta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), CARD_BG),
                ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # 3. Executive Summary
    story.append(Paragraph("1. Executive Summary", section_heading))
    summary_text = analysis_data.get("executive_summary") or "Automated analysis completed successfully."
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 8))

    # 4. Root Cause Analysis
    story.append(Paragraph("2. Root Cause Analysis (RCA)", section_heading))
    rca_text = analysis_data.get("root_cause") or "Root cause under automated investigation."
    story.append(Paragraph(rca_text, body_style))
    story.append(Spacer(1, 8))

    # 5. Evidence & Parsed Log Snippets
    story.append(Paragraph("3. Log Evidence & Error Signatures", section_heading))
    parsed_entries = analysis_data.get("parsed_entries") or []
    error_entries = [e for e in parsed_entries if (e.get("level") or "").upper() in ("ERROR", "CRITICAL", "WARN")][:5]
    if not error_entries and parsed_entries:
        error_entries = parsed_entries[:5]

    if error_entries:
        evidence_rows = [
            [
                Paragraph("<b>Line</b>", body_style),
                Paragraph("<b>Level</b>", body_style),
                Paragraph("<b>Service</b>", body_style),
                Paragraph("<b>Message</b>", body_style),
            ]
        ]
        for e in error_entries:
            line_no = str(e.get("line_number", "-"))
            level_str = str(e.get("level", "INFO")).upper()
            service_str = str(e.get("service") or "system")
            msg_str = str(e.get("message") or e.get("raw") or "")[:120]
            evidence_rows.append(
                [
                    Paragraph(line_no, code_style),
                    Paragraph(f"<b>{level_str}</b>", body_style),
                    Paragraph(service_str, body_style),
                    Paragraph(msg_str, code_style),
                ]
            )

        evidence_table = Table(evidence_rows, colWidths=[0.6 * inch, 0.9 * inch, 1.3 * inch, 4.4 * inch])
        evidence_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                    ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(evidence_table)
    else:
        story.append(Paragraph("No critical error signatures identified in the uploaded log excerpt.", body_style))

    story.append(Spacer(1, 10))

    # 6. Recommended Immediate Fixes
    story.append(Paragraph("4. Recommended Immediate Fixes", section_heading))
    fixes = analysis_data.get("recommended_fixes") or "1. Inspect service metrics and scale resource allocation."
    for fix_line in fixes.split("\n"):
        if fix_line.strip():
            story.append(Paragraph(f"• {fix_line.strip().lstrip('1234567890.-• ')}", body_style))
    story.append(Spacer(1, 8))

    # 7. Long-Term Preventive Measures
    story.append(Paragraph("5. Long-Term Preventive Measures", section_heading))
    prevs = analysis_data.get("preventive_measures") or "1. Configure threshold alerting on error count and memory."
    for prev_line in prevs.split("\n"):
        if prev_line.strip():
            story.append(Paragraph(f"• {prev_line.strip().lstrip('1234567890.-• ')}", body_style))

    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
    story.append(Paragraph("Generated by CloudPulse-AI Observability Platform | https://cloudpulse.io", subtitle_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def generate_pdf_bytes(title: str, content: str) -> bytes:
    """
    Generates a generic ReportLab PDF from title and text content.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "PDFTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=PRIMARY_COLOR,
        spaceAfter=12,
    )
    body_style = ParagraphStyle(
        "PDFBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
    )

    story = [
        Paragraph(title, title_style),
        HRFlowable(width="100%", thickness=1, color=BRAND_BLUE, spaceAfter=14),
    ]

    for line in content.split("\n"):
        if line.strip():
            story.append(Paragraph(line.strip(), body_style))
        else:
            story.append(Spacer(1, 4))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

