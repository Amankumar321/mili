import aspose.words as aw
import aspose.words
import imgkit
from app.models.request_models import DocumentRequest
from app.utils.tempfile_manager import ManagedTempFile


def generate_docx(request: DocumentRequest) -> str:
    """Generates a DOCX file from HTML input with proper watermark handling."""
    try:
        with ManagedTempFile(suffix='.docx') as temp_path:
            doc = aw.Document()
            builder = aw.DocumentBuilder(doc)

            # Add watermark if provided
            if request.watermark_html:
                add_watermark(doc, builder, request)

            # Add header if provided
            if request.header_html:
                builder.move_to_header_footer(aw.HeaderFooterType.HEADER_PRIMARY)
                builder.insert_html(request.header_html)

            # Add main content
            builder.move_to_section(0)
            builder.insert_html(request.content_html)

            # Add footer if provided
            if request.footer_html:
                handle_docx_footer(doc, builder, request)

            doc.save(temp_path)
            return temp_path
        
    except Exception as e:
        raise RuntimeError(f"Error generating DOCX: ", str(e))

def add_watermark(doc: aw.Document, builder: aw.DocumentBuilder, request: DocumentRequest):
    """Adds HTML watermark as image with proper positioning."""
    try:
        with ManagedTempFile(suffix='.png') as img_path:
            # Convert HTML to image
            options = {
                'format': 'png',
                'width': request.watermark_width,
                'height': request.watermark_height,
                'encoding': "UTF-8",
                'quiet': '',
                'transparent': ''
            }
            imgkit.from_string(request.watermark_html, img_path, options=options)

            # Create watermark shape
            watermark = aw.drawing.Shape(doc, aw.drawing.ShapeType.IMAGE)
            watermark.image_data.set_image(img_path)
            watermark.width = request.watermark_width
            watermark.height = request.watermark_height
            watermark.rotation = request.watermark_rotation
            watermark.fill.transparency = request.watermark_opacity
            watermark.z_order = -100  # Behind content

            # Center watermark
            watermark.relative_horizontal_position = aw.drawing.RelativeHorizontalPosition.PAGE
            watermark.relative_vertical_position = aw.drawing.RelativeVerticalPosition.PAGE
            watermark.horizontal_alignment = aw.drawing.HorizontalAlignment.CENTER
            watermark.vertical_alignment = aw.drawing.VerticalAlignment.CENTER

            # Add to all pages
            watermark_para = aw.Paragraph(doc)
            watermark_para.append_child(watermark)
            for sect in doc.sections:
                sect = sect.as_section()
                insert_watermark_into_header(watermark_para, sect, aw.HeaderFooterType.HEADER_PRIMARY)

    except Exception as e:
        raise RuntimeError(f"Failed to add watermark")

def insert_watermark_into_header(watermark_para: aw.Paragraph, sect: aw.Section, header_type: aw.HeaderFooterType):
    """Helper to insert watermark into document headers."""
    header = sect.headers_footers.get_by_header_footer_type(header_type)
    if header is None:
        header = aw.HeaderFooter(sect.document, header_type)
        sect.headers_footers.add(header)
    header.append_child(watermark_para.clone(True))

def handle_docx_footer(doc: aw.Document, builder: aw.DocumentBuilder, request: DocumentRequest):
    """Handles footer placement based on request settings."""
        
    # Create layout collector to get page information
    layout_collector = aw.layout.LayoutCollector(doc)

    if request.footer_last_page_only:
        # Find the paragraph that ends on the last page
        last_page = doc.page_count - 1
        last_para = next(
            (p for p in doc.get_child_nodes(aw.NodeType.PARAGRAPH, True)
            if layout_collector.get_end_page_index(p) == last_page
        ), None)
        
        if last_para:
            # Create new section at the start of the last page
            first_para_on_last = next(
                (p for p in doc.get_child_nodes(aw.NodeType.PARAGRAPH, True)
                if layout_collector.get_start_page_index(p) == last_page
            ), None)
            
            if first_para_on_last:
                builder.move_to(first_para_on_last)
                builder.insert_break(aw.BreakType.SECTION_BREAK_CONTINUOUS)
                new_section = builder.current_section
                new_section.headers_footers.link_to_previous(False)
                
                builder.move_to_header_footer(aw.HeaderFooterType.FOOTER_PRIMARY)
                builder.insert_html(request.footer_html)
    else:
        # Add footer to the primary section (will appear on all pages)
        builder.move_to_header_footer(aw.HeaderFooterType.FOOTER_PRIMARY)
        builder.insert_html(request.footer_html)
        builder.move_to_document_end()