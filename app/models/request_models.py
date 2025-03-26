from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bs4 import BeautifulSoup

class DocumentRequest(BaseModel):
    """Request model for document generation"""
    content_html: str = Field(..., example="<h1>Main Content</h1><p>This is the document body</p>", 
                            description="HTML content for the document body")
    
    header_html: Optional[str] = Field(None, example="<header>Company Name</header>", 
                                     description="HTML for document header")
    
    footer_html: Optional[str] = Field(None, example="<footer>Page {page_number}</footer>", 
                                     description="HTML for document footer")
    
    document_type: str = Field(..., example="pdf", 
                             description="Output format: 'pdf' or 'docx'")
    
    watermark_html: Optional[str] = Field(None, example="<div>CONFIDENTIAL</div>", 
                                       description="HTML for watermark content")
    
    watermark_width: Optional[int] = Field(200, ge=50, le=1000, 
                                         description="Watermark width in points")
    
    watermark_height: Optional[int] = Field(100, ge=50, le=1000, 
                                          description="Watermark height in points")
    
    watermark_rotation: Optional[int] = Field(-45, ge=-180, le=180, 
                                            description="Watermark rotation in degrees")
    
    watermark_opacity: Optional[float] = Field(0.5, ge=0, le=1, 
                                             description="Watermark opacity (0-1)")
    
    footer_last_page_only: Optional[bool] = Field(False, 
                                                description="Show footer only on last page")

    @field_validator('document_type')
    def validate_document_type(cls, v):
        if v.lower() not in ['pdf', 'docx']:
            raise ValueError('document_type must be either "pdf" or "docx"')
        return v.lower()
    
    @field_validator('content_html')
    def validate_content_html(cls, v):
        if not v.strip():
            raise ValueError('content_html cannot be empty')
        try:
            BeautifulSoup(v, 'html.parser')
            return v
        except Exception as e:
            raise ValueError(f'Invalid HTML')
    
    @field_validator('watermark_html', 'header_html', 'footer_html')
    def validate_html(cls, v):
        if v is None:
            return v
        try:
            BeautifulSoup(v, 'html.parser')
            return v
        except Exception as e:
            raise ValueError(f'Invalid HTML')
    
    @field_validator('watermark_opacity')
    def validate_opacity(cls, v):
        if v is not None and (v < 0 or v > 1):
            raise ValueError('Opacity must be between 0 and 1')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "content_html": "<h1>Annual Report</h1><p>Financial results for Q4 2023</p><p>Revenue: $1.2M</p>",
                "header_html": "<div style='text-align: center; border-bottom: 1px solid #ccc; padding: 10px;'>ACME Corporation</div>",
                "footer_html": "<div style='font-size: 10pt; color: #666;'>Page {page_number} | Confidential</div>",
                "document_type": "pdf",
                "watermark_html": "<div style='color: rgba(150,150,150,1); font-size: 150px; text-align: center;'>DRAFT</div>",
                "watermark_width": 800,
                "watermark_height": 200,
                "watermark_rotation": 45,
                "watermark_opacity": 0.5,
                "footer_last_page_only": False
            }

        }