"""
Report router — Gap 8 Rich Reporting

Endpoints:
  GET /v1/report/generate     — Download EU AI Act PDF report (auditor+)
  GET /v1/report/analytics    — JSON analytics summary with domain breakdown (auditor+)
"""
from fastapi import APIRouter, Depends
from fastapi.responses import Response

from app.auth.rbac import TenantContext, auditor_or_admin
from app.models.database import get_tenant_analytics, get_domain_analytics
from app.services.compliance_report import generate_pdf_report

router = APIRouter()


@router.get("/generate", summary="Download EU AI Act compliance report (PDF)")
async def get_compliance_report(ctx: TenantContext = Depends(auditor_or_admin)):
    """
    Generate and stream a rich EU AI Act Article 13/17 compliance PDF.
    Includes executive summary, per-domain breakdown, bias trend, and
    hash-chain integrity status.
    """
    pdf_bytes = generate_pdf_report(ctx.tenant_id)
    content_type = (
        "application/pdf"
        if pdf_bytes[:4] == b"%PDF"
        else "text/plain; charset=utf-8"
    )
    filename = f"fairguard_compliance_{ctx.tenant_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/analytics", summary="JSON compliance analytics with domain breakdown")
async def get_analytics(ctx: TenantContext = Depends(auditor_or_admin)):
    """
    Return structured JSON analytics:
      - overall: total decisions, interventions, compliance rate
      - domains: per-domain breakdown (Gap 2)
    """
    overall = get_tenant_analytics(ctx.tenant_id)
    domains = get_domain_analytics(ctx.tenant_id)
    return {
        "tenant_id": ctx.tenant_id,
        "overall": overall,
        "domains": domains,
    }
