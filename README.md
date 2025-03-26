 # Document Generation Service

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95.2-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

A FastAPI backend service that generates PDF and DOCX documents from HTML input with support for headers, footers, and watermarks.

## ✨ Features

### Core Functionality
- Generate PDF documents from HTML content
- Generate DOCX (Word) documents from HTML content
- Custom headers and footers
- File download with proper content disposition

### Bonus Features
- **Watermark Support**:
  - Text or HTML watermarks
  - Configurable size, rotation, and opacity
  - Appears behind content on all pages
- **Conditional Footer**:
  - Option to render footer only on last page
- **Validation**:
  - HTML content validation
  - Document type verification
  - Parameter range checks

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **PDF Generation**: pdfkit + PyMuPDF
- **DOCX Generation**: Aspose.Words
- **HTML Processing**: BeautifulSoup
- **Testing**: pytest

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- wkhtmltopdf installed

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/document-generation-service.git
cd document-generation-service
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Running the Service
```bash
uvicorn app.main:app --reload
```
Access interactive docs at: http://localhost:8000/docs

##  API Documentation

Generate Document

Endpoint: POST /api/v1/generate-document

Request Body Example:

```json
{
  "content_html": "<h1>Report</h1><p>Content</p>",
  "header_html": "<div>Header</div>",
  "footer_html": "<div>Footer</div>",
  "document_type": "pdf",
  "watermark_html": "<div style='font-size: 100px;'>DRAFT</div>",
  "watermark_width": 800,
  "watermark_height": 300,
  "watermark_rotation": -45,
  "watermark_opacity": 0.3,
  "footer_last_page_only": true
}
```

Response:

- Returns generated file with proper content-type
- Filename is automatically generated

### Testing

```bash
pytest tests/
```

Test coverage includes:

- API endpoint validation
- Document generation
- Watermark functionality
- Footer placement logic
- Error handling

### Project Structure

mili/
├── app/
│   ├── api/               # API endpoints
│   ├── models/            # Pydantic models
│   ├── services/          # PDF/DOCX generators
│   ├── utils/             # Helper functions
│   └── main.py            # FastAPI app setup
├── tests/                 # Test cases
├── requirements.txt       # Dependencies
└── README.md              # This file

### Example Requests

```json
{
  "content_html": "<h1>Confidential Report</h1>",
  "document_type": "docx",
  "watermark_html": "<h2>INTERNAL USE ONLY</h2>"
}
```