import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.request_models import DocumentRequest
import zipfile
from xml.etree import ElementTree as ET

client = TestClient(app)

# Common test data
TEST_CONTENT = "<h1>Test Document</h1><p>This is test content for document generation.</p>"
TEST_HEADER = "<header style='background-color: #f0f0f0; padding: 10px;'>Test Header</header>"
TEST_FOOTER = "<footer style='border-top: 1px solid #ccc; padding: 5px;'>Page {page_number}</footer>"
TEST_FOOTER_TEXT = "Page {page_number}"
WATERMARK = "<div style='font-size: 48px; color: gray;'>CONFIDENTIAL</div>"

@pytest.fixture
def cleanup_test_files():
    """Fixture to clean up test files after each test"""
    yield
    for filename in os.listdir('./temp'):
        if filename.startswith("test_output_") and (filename.endswith(".pdf") or filename.endswith(".docx")):
            try:
                os.remove(os.path.join('./temp', filename))
            except:
                pass

def test_generate_pdf_basic(cleanup_test_files):
    """Test basic PDF generation without optional fields"""
    response = client.post("/generate-document", json={
        "content_html": TEST_CONTENT,
        "document_type": "pdf"
    })
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"
    assert "attachment" in response.headers["content-disposition"]
    
    # Verify file content
    assert len(response.content) > 1000  # Basic check that we got a PDF file

def test_generate_pdf_full_features(cleanup_test_files):
    """Test PDF generation with all features"""
    response = client.post("/generate-document", json={
        "content_html": TEST_CONTENT,
        "header_html": TEST_HEADER,
        "footer_html": TEST_FOOTER,
        "document_type": "pdf",
        "watermark_html": WATERMARK,
        "watermark_opacity": 0.3,
        "footer_last_page_only": True
    })
    print(response.text)
    assert response.status_code == 200
    output_path = "./temp/test_output_full.pdf"
    with open(output_path, "wb") as f:
        f.write(response.content)
    
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 2000  # Should be larger than basic PDF

def test_generate_docx_basic(cleanup_test_files):
    """Test basic DOCX generation"""
    response = client.post("/generate-document", json={
        "content_html": TEST_CONTENT,
        "document_type": "docx"
    })

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/octet-stream"
    
    # Verify file content
    assert len(response.content) > 1000  # Basic check for DOCX file

def test_generate_docx_with_watermark(cleanup_test_files):
    """Test DOCX generation with watermark"""
    response = client.post("/generate-document", json={
        "content_html": TEST_CONTENT,
        "document_type": "docx",
        "watermark_html": WATERMARK,
        "watermark_opacity": 0.3
    })
 
    assert response.status_code == 200
    output_path = "./temp/test_output_watermark.docx"
    with open(output_path, "wb") as f:
        f.write(response.content)
    
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 1500  # Should be larger than basic DOCX

def test_invalid_document_type(cleanup_test_files):
    """Test invalid document type handling"""
    response = client.post("/generate-document", json={
        "content_html": TEST_CONTENT,
        "document_type": "invalid_type"
    })
    
    assert response.status_code == 422  # Unprocessable Entity
    assert "document_type" in response.text
    assert "must be either" in response.text.lower()

def test_missing_content(cleanup_test_files):
    """Test validation for missing content"""
    response = client.post("/generate-document", json={
        "content_html": "",
        "document_type": "pdf"
    })
    
    assert response.status_code == 422
    assert "content_html" in response.text
    assert "cannot be empty" in response.text.lower()

def test_large_html_input(cleanup_test_files):
    """Test handling of large HTML input"""
    large_content = "<div>" + ("<p>Test paragraph</p>" * 1000) + "</div>"
    response = client.post("/generate-document", json={
        "content_html": large_content,
        "document_type": "pdf"
    })
    
    assert response.status_code == 200
    assert len(response.content) > 10000  # Should be a substantial PDF file

def test_special_characters(cleanup_test_files):
    """Test handling of special characters in HTML"""
    response = client.post("/generate-document", json={
        "content_html": "<p>Special chars: © ® ™ € ¥ ¢ §</p>",
        "document_type": "pdf"
    })
    
    assert response.status_code == 200
    output_path = "./temp/test_output_special_chars.pdf"
    with open(output_path, "wb") as f:
        f.write(response.content)
    
    assert os.path.exists(output_path)

def test_footer_last_page_only_pdf(cleanup_test_files):
    """Test footer_last_page_only functionality"""
    multi_page_content = "<div style='page-break-after: always;'>Page 1</div><div>Page 2</div>"
    response = client.post("/generate-document", json={
        "content_html": multi_page_content,
        "footer_html": TEST_FOOTER,
        "document_type": "pdf",
        "footer_last_page_only": True
    })
    
    assert response.status_code == 200
    output_path = "./temp/test_output_footer_last.pdf"
    with open(output_path, "wb") as f:
        f.write(response.content)
    
    assert os.path.exists(output_path)

def test_footer_last_page_only_docx(cleanup_test_files):
    """Test footer_last_page_only functionality for DOCX documents"""
    multi_page_content = "<p>" + "</p><p>".join([f"Paragraph {i}" for i in range(30)]) + "</p>"
    response = client.post("/generate-document", json={
        "content_html": multi_page_content,
        "footer_html": TEST_FOOTER,
        "document_type": "docx",
        "footer_last_page_only": True  # Should only appear on last page
    })
    print(response.text)
    assert response.status_code == 200
    output_path = "./temp/test_output_footer_last.docx"
    
    with open(output_path, "wb") as f:
        f.write(response.content)
    assert os.path.exists(output_path)
    
    with zipfile.ZipFile(output_path) as z:
        footer_files = [f for f in z.namelist() if 'footer' in f and f.endswith('.xml')]
        
        assert len(footer_files) >= 1
        
        for footer_file in footer_files:
            with z.open(footer_file) as f:
                xml_content = f.read().decode('utf-8')
                print(footer_file)
                if 'footer3.xml' in footer_file:  # Last page footer
                    assert TEST_FOOTER_TEXT in xml_content
                else:
                    assert TEST_FOOTER_TEXT not in xml_content
