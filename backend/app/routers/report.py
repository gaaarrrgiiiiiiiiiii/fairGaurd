from fastapi import APIRouter, Response
from app.services.compliance_report import generate_pdf_report

router = APIRouter()

@router.get("/generate")
async def get_compliance_report(tenant_id: str = "tenant_local_dev"):
    # Generate the PDF byte stream
    pdf_bytes = generate_pdf_report(tenant_id)
    
    # Return as a downloadable file
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="fairguard_eu_aia_report_{tenant_id}.pdf"'
        }
    )
