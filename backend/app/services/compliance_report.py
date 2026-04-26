"""
Gap 8 — Rich Compliance Report Service

Generates an EU AI Act Article 13/17-compliant PDF report including:
  - Executive summary with compliance rate gauge
  - Per-domain bias breakdown table
  - 7-day bias trend summary
  - Hash-chain integrity status
  - Methodology appendix

Uses ReportLab if available; degrades gracefully to structured JSON otherwise.
"""
import io
import datetime
import json
import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from app.models.database import (
    get_tenant_analytics,
    get_domain_analytics,
    get_recent_audit_logs,
    verify_audit_chain,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bias_trend(tenant_id: str, days: int = 7) -> Dict[str, Any]:
    """Count bias detections per day over the last `days` days."""
    logs = get_recent_audit_logs(tenant_id, limit=500)
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    daily: Dict[str, int] = {}
    biased_total = 0
    for log in logs:
        ts = datetime.datetime.fromisoformat(log["timestamp"])
        if ts < cutoff:
            continue
        day = ts.strftime("%Y-%m-%d")
        daily[day] = daily.get(day, 0) + (1 if log.get("correction_applied") else 0)
        if log.get("correction_applied"):
            biased_total += 1
    return {"daily_interventions": daily, "period_days": days, "total_interventions": biased_total}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_pdf_report(tenant_id: str) -> bytes:
    """Generate and return a rich EU AI Act compliance report as PDF bytes."""
    analytics    = get_tenant_analytics(tenant_id)
    domains      = get_domain_analytics(tenant_id)
    trend        = _bias_trend(tenant_id)
    chain_result = verify_audit_chain(tenant_id)

    total        = analytics["total_decisions"]
    interventions= analytics["interventions"]
    compliance   = analytics["compliance_rate"]
    generated_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    if REPORTLAB_AVAILABLE:
        return _build_pdf(
            tenant_id, generated_at, total, interventions, compliance,
            domains, trend, chain_result,
        )
    else:
        return _build_text_fallback(
            tenant_id, generated_at, total, interventions, compliance,
            domains, trend, chain_result,
        )


def _build_pdf(
    tenant_id, generated_at, total, interventions, compliance,
    domains, trend, chain_result,
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )
    styles = getSampleStyleSheet()

    # Custom styles
    title_style  = ParagraphStyle("Title2", parent=styles["Title"], fontSize=18, spaceAfter=6)
    h2_style     = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, spaceAfter=4)
    body_style   = styles["BodyText"]
    small_style  = ParagraphStyle("Small", parent=body_style, fontSize=9)

    # Compliance colour coding
    if compliance >= 95:
        compliance_color = colors.HexColor("#16a34a")   # green
    elif compliance >= 80:
        compliance_color = colors.HexColor("#d97706")   # amber
    else:
        compliance_color = colors.HexColor("#dc2626")   # red

    gauge_style = ParagraphStyle(
        "Gauge", parent=styles["BodyText"], fontSize=28, textColor=compliance_color, spaceAfter=4,
    )

    elements = []

    # ── Header ──────────────────────────────────────────────────────────────
    elements.append(Paragraph("FairGuard — EU AI Act Compliance Report", title_style))
    elements.append(Paragraph(f"Tenant: <b>{tenant_id}</b> &nbsp;|&nbsp; Generated: {generated_at}", small_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb")))
    elements.append(Spacer(1, 0.4*cm))

    # ── Executive summary ───────────────────────────────────────────────────
    elements.append(Paragraph("Executive Summary", h2_style))
    elements.append(Paragraph(f"<b>{compliance}%</b>", gauge_style))
    elements.append(Paragraph("System Compliance Rate (% decisions without bias intervention)", small_style))
    elements.append(Spacer(1, 0.3*cm))

    summary_data = [
        ["Metric", "Value"],
        ["Total Decisions Monitored", f"{total:,}"],
        ["Bias Interventions Applied", f"{interventions:,}"],
        ["Compliance Rate", f"{compliance}%"],
        ["Audit Chain Integrity", "✅ Valid" if chain_result.get("valid") else "⚠️ INVALID"],
        ["Records in Chain", f"{chain_result.get('records_checked', 0):,}"],
        ["Report Period", f"All time (last {trend['period_days']}d trend below)"],
    ]
    summary_table = Table(summary_data, colWidths=[9*cm, 7*cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#1e40af")),
        ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",(0, 0), (-1, -1), 8),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5*cm))

    # ── Per-domain breakdown ─────────────────────────────────────────────────
    elements.append(Paragraph("Per-Domain Bias Breakdown (Gap 2 — Multi-Vertical)", h2_style))
    if domains:
        domain_data = [["Domain", "Decisions", "Interventions", "Compliance Rate"]]
        for d in sorted(domains, key=lambda x: x["domain"]):
            domain_data.append([
                d["domain"],
                f"{d['total_decisions']:,}",
                f"{d['interventions']:,}",
                f"{d['compliance_rate']}%",
            ])
        domain_table = Table(domain_data, colWidths=[5*cm, 4*cm, 4*cm, 4*cm])
        domain_table.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f1f5f9"), colors.white]),
            ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",(0, 0), (-1, -1), 8),
            ("TOPPADDING",  (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ]))
        elements.append(domain_table)
    else:
        elements.append(Paragraph(
            "No domain-tagged decisions found. Pass <code>domain</code> in your API request to enable per-domain reporting.",
            body_style,
        ))
    elements.append(Spacer(1, 0.5*cm))

    # ── Bias trend ───────────────────────────────────────────────────────────
    elements.append(Paragraph(f"Bias Intervention Trend (Last {trend['period_days']} Days)", h2_style))
    daily = trend["daily_interventions"]
    if daily:
        trend_data = [["Date", "Interventions"]] + [
            [day, str(count)] for day, count in sorted(daily.items())
        ]
        trend_table = Table(trend_data, colWidths=[8*cm, 5*cm])
        trend_table.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0), colors.HexColor("#1e40af")),
            ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
            ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING",  (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
        ]))
        elements.append(trend_table)
    else:
        elements.append(Paragraph("No interventions recorded in the last 7 days.", body_style))
    elements.append(Spacer(1, 0.5*cm))

    # ── Regulatory basis ─────────────────────────────────────────────────────
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e5e7eb")))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph("Regulatory Basis & Methodology", h2_style))
    elements.append(Paragraph(
        "This report is generated in compliance with <b>EU AI Act Article 13</b> (Transparency) "
        "and <b>Article 17</b> (Quality Management). FairGuard evaluates bias using four metrics: "
        "<b>DPD</b> (Demographic Parity Difference), <b>EOD</b> (Equalized Odds Difference), "
        "<b>ICD</b> (Individual Counterfactual Disparity), and <b>CAS</b> (Causal Attribution Score). "
        "All decisions are recorded in an immutable SHA-256 hash chain (Art. 12).",
        body_style,
    ))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        f"<i>Hash-chain status: {'VALID — all records consistent' if chain_result.get('valid') else 'INTEGRITY WARNING — manual review required'}. "
        f"Records verified: {chain_result.get('records_checked', 0):,}.</i>",
        small_style,
    ))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def _build_text_fallback(
    tenant_id, generated_at, total, interventions, compliance,
    domains, trend, chain_result,
) -> bytes:
    """Plain-text fallback when ReportLab is unavailable."""
    lines = [
        "=" * 70,
        "FAIRGUARD EU AI ACT COMPLIANCE REPORT",
        "=" * 70,
        f"Tenant:    {tenant_id}",
        f"Generated: {generated_at}",
        "",
        "── EXECUTIVE SUMMARY ──────────────────────────────────────────────",
        f"  Total Decisions:     {total:,}",
        f"  Interventions:       {interventions:,}",
        f"  Compliance Rate:     {compliance}%",
        f"  Chain Integrity:     {'VALID' if chain_result.get('valid') else 'INVALID'}",
        f"  Records Verified:    {chain_result.get('records_checked', 0):,}",
        "",
        "── PER-DOMAIN BREAKDOWN ───────────────────────────────────────────",
    ]
    if domains:
        for d in sorted(domains, key=lambda x: x["domain"]):
            lines.append(
                f"  {d['domain']:20s}  decisions={d['total_decisions']:>6,}  "
                f"interventions={d['interventions']:>5,}  compliance={d['compliance_rate']}%"
            )
    else:
        lines.append("  No domain-tagged decisions found.")

    lines += [
        "",
        f"── BIAS TREND (LAST {trend['period_days']} DAYS) ─────────────────────────────────",
    ]
    daily = trend["daily_interventions"]
    if daily:
        for day, count in sorted(daily.items()):
            lines.append(f"  {day}: {count} interventions")
    else:
        lines.append("  No interventions in this period.")

    lines += [
        "",
        "── REGULATORY BASIS ───────────────────────────────────────────────",
        "  EU AI Act Art. 13 (Transparency), Art. 17 (Quality Management),",
        "  Art. 12 (Immutable Audit Logging via SHA-256 hash chain).",
        "=" * 70,
    ]
    return "\n".join(lines).encode("utf-8")
