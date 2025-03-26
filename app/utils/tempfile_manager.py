import tempfile
import os
from typing import Optional
from app.utils.file_cleanup import register_temp_file

class ManagedTempFile:
    def __init__(self, suffix: Optional[str] = None):
        self.suffix = suffix
        self.path = None
        
    def __enter__(self):
        self.file = tempfile.NamedTemporaryFile(dir='./temp', delete=False, suffix=self.suffix)
        self.path = self.file.name
        self.file.close()  # Close so other processes can use it
        register_temp_file(self.path)
        return self.path
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:  # If an exception occurred
            if os.path.exists(self.path):
                os.unlink(self.path)
            try:
                from app.utils.file_cleanup import _temp_files
                _temp_files.discard(self.path)
            except:
                pass