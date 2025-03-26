import os
import atexit
from typing import Set

_temp_files: Set[str] = set()

def register_temp_file(file_path: str) -> str:
    """Register a temporary file for cleanup."""
    _temp_files.add(file_path)
    return file_path

def cleanup_temp_files():
    """Clean up all registered temporary files."""
    for file_path in list(_temp_files):
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
            _temp_files.remove(file_path)
        except Exception:
            pass

atexit.register(cleanup_temp_files)