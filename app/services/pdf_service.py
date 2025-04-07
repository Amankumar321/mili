import pdfkit
import fitz  # PyMuPDF
import imgkit
from app.models.request_models import DocumentRequest
from app.utils.tempfile_manager import ManagedTempFile


def generate_pdf(request: DocumentRequest) -> str:
    """Generates a PDF file with proper HTML and watermark handling."""
    try:
        with ManagedTempFile(suffix='.pdf') as temp_path:
            # Generate base PDF
            options = {
                'margin-top': '50px',
                'margin-right': '50px',
                'margin-bottom': '50px',
                'margin-left': '50px',
                'encoding': "UTF-8",
                'quiet': ''
            }
            pdfkit.from_string(construct_html(request), temp_path, options=options)

            # Apply watermark if needed
            if request.watermark_html:
                apply_watermark(temp_path, request)

            # Handle footer
            if request.footer_html:
                handle_pdf_footer(temp_path, request)

            return temp_path
        
    except Exception as e:
        raise RuntimeError(f"PDF generation failed: ", str(e))

def construct_html(request: DocumentRequest) -> str:
    """Constructs complete HTML document with proper structure."""
    return f"""<html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ margin: 50px; }}
            body {{ font-family: Arial, sans-serif; }}
        </style>
    </head>
    <body>
        <div style='width: 100%; height: 100%'>
          {request.header_html or ""}
          {request.content_html}
        </div>
    </body>
</html>"""

def apply_watermark(pdf_path: str, request: DocumentRequest):
    """Applies HTML watermark as image to PDF."""
    try:
        with ManagedTempFile(suffix='.png') as img_path:
            # Convert HTML to image
            options = {
                'format': 'png',
                'width': request.watermark_width,
                'height': request.watermark_height,
                'encoding': "UTF-8",
                'quiet': ''
            }
            imgkit.from_string(f"""
                <div style="
                    opacity: {request.watermark_opacity};
                    width: 100%;
                    height: 100%;
                ">
                    {request.watermark_html}
                </div>
                """, img_path, options=options)

            # Apply to PDF
            doc = fitz.open(pdf_path)

            watermark_doc = fitz.open()
            watermark_page = watermark_doc.new_page()
          
            watermark_page.insert_image(
                watermark_page.rect,
                filename=img_path,
            )

            for page in doc:
                rect = page.rect
                x = (rect.width - request.watermark_width) / 2
                y = (rect.height - request.watermark_height) / 2

                page.show_pdf_page(
                    fitz.Rect(x, y, x + request.watermark_width, y + request.watermark_height),
                    watermark_doc,
                    0,
                    rotate=request.watermark_rotation,
                    overlay=False
                )
            
            doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
            doc.close()
            
    except Exception as e:
        raise RuntimeError(f"Failed to apply watermark")

def handle_pdf_footer(pdf_path: str, request: DocumentRequest):
    """Handles footer placement in PDF."""
    try:
        doc = fitz.open(pdf_path)
        pages = [len(doc)-1] if request.footer_last_page_only else range(len(doc))
        
        for pg_num in pages:
            page = doc[pg_num]
            rect = page.rect
            footer_rect = fitz.Rect(
                rect.x0 + 10,
                rect.y1 - 50,
                rect.x1 - 10,
                rect.y1 - 5
            )
            page.insert_htmlbox(footer_rect, request.footer_html)
        
        doc.save(pdf_path, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
        doc.close()
        
    except Exception as e:
        raise RuntimeError(f"Failed to add footer")