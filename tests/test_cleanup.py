import os
from fastapi.testclient import TestClient
from app.main import app
from app.utils.file_cleanup import _temp_files

client = TestClient(app)

def test_temp_file_cleanup():
    # Store initial temp files count
    initial_count = len(_temp_files)
    
    # Generate a document
    response = client.post("/generate-document", json={
        "content_html": "<p>Test Content</p>",
        "document_type": "pdf"
    })

    assert response.status_code == 200
    assert len(_temp_files) == initial_count + 1
    
    # Get the generated file path from headers
    content_disposition = response.headers["content-disposition"]
    filename = content_disposition.split("filename=")[1].strip('"')
    
    # Verify file was registered for cleanup
    assert any(filename in path for path in _temp_files)
    
    # Manual cleanup for test (in real app this happens automatically)
    for path in list(_temp_files):
        if filename in path:
            if os.path.exists(path):
                os.unlink(path)
            _temp_files.remove(path)
    
    assert len(_temp_files) == initial_count