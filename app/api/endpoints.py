from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models.request_models import DocumentRequest
from app.services.pdf_service import generate_pdf
from app.services.docx_service import generate_docx
import os

router = APIRouter(tags=["Document Generation"])

@router.post(
    "/generate-document",
    response_class=FileResponse,
    summary="Generate PDF or DOCX document",
    description="""Generates a document with the specified content, header, footer, and watermark options.
    
**Features:**
- Supports both PDF and DOCX formats
- Customizable headers and footers
- Watermark support with rotation and opacity control
- Conditional footer placement""",
    responses={
        200: {
            "content": {
                "application/pdf": {},
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {}
            },
            "description": "Returns the generated document file",
        },
        400: {"description": "Invalid document type or parameters"},
        500: {"description": "Document generation failed"}
    }
)
async def generate_document(request: DocumentRequest):
    """Generates a document based on input HTML and type.
    
    Args:
        request (DocumentRequest): Document generation parameters
    
    Returns:
        FileResponse: Generated document file with appropriate content-type
    
    Raises:
        HTTPException: If document generation fails
    """
    try:
        if request.document_type == "pdf":
            file_path = generate_pdf(request)
        elif request.document_type == "docx":
            file_path = generate_docx(request)
        else:
            raise HTTPException(status_code=400, detail="Invalid document type")

        return FileResponse(
            file_path,
            filename=os.path.basename(file_path),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={os.path.basename(file_path)}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))