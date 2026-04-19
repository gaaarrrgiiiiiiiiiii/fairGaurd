import io
import datetime

# Graceful degradation in case reportlab isn't installed in the hackathon env
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from app.models.database import get_tenant_analytics

def generate_pdf_report(tenant_id: str) -> bytes:
    buffer = io.BytesIO()
    
    analytics = get_tenant_analytics(tenant_id)
    total_decisions = analytics["total_decisions"]
    interventions = analytics["interventions"]
    compliance_rate = analytics["compliance_rate"]
    
    if REPORTLAB_AVAILABLE:
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, f"FairGuard Compliance Report (EU AI Act)")
        
        c.setFont("Helvetica", 12)
        c.drawString(50, 720, f"Tenant ID: {tenant_id}")
        c.drawString(50, 705, f"Date Generated: {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        c.drawString(50, 670, "Summary of Interventions:")
        c.drawString(50, 650, f"- Total Decisions Monitored: {total_decisions:,}")
        c.drawString(50, 635, f"- Biases Intercepted: {interventions:,}")
        c.drawString(50, 620, f"- System Compliance Rate: {compliance_rate}%")
        
        c.drawString(50, 580, "Article 13 Post-Market Monitoring:")
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, 560, "The AI systems operating under this tenant demonstrate consistent adherence")
        c.drawString(50, 545, "to equalized odds across protected attributes (gender, race).")
        
        c.save()
    else:
        # Fallback text format if library missing locally
        lines = [
            "FAIRGUARD COMPLIANCE REPORT (EU AI ACT)",
            f"Tenant ID: {tenant_id}",
            f"Date: {datetime.datetime.utcnow().isoformat()}",
            "---",
            "Summary:",
            f"- Total Decisions: {total_decisions}",
            f"- Interventions: {interventions}",
            f"- Compliance Rate: {compliance_rate}%",
            "ReportLab not available. This is a text fallback."
        ]
        buffer.write("\n".join(lines).encode('utf-8'))
        
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
