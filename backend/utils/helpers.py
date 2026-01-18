"""
Utility helper functions
"""

import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import List


def generate_job_id() -> str:
    """Generate unique job ID"""
    return str(uuid.uuid4())


def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return Path(filename).suffix.lower()


def get_filename_without_extension(filename: str) -> str:
    """Get filename without extension"""
    return Path(filename).stem


def create_directory_if_not_exists(directory: str) -> str:
    """Create directory if it doesn't exist"""
    os.makedirs(directory, exist_ok=True)
    return directory


def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    return os.path.getsize(file_path)


def format_file_size(size_bytes: int) -> str:
    """Format bytes to human readable format"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def get_timestamp() -> str:
    """Get current timestamp"""
    return datetime.now().isoformat()


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Check if file has allowed extension"""
    ext = get_file_extension(filename)
    return ext in allowed_extensions


def delete_file_if_exists(file_path: str) -> bool:
    """Delete file if it exists"""
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def clean_temp_directory(directory: str, max_age_hours: int = 24) -> int:
    """
    Delete old temporary files
    
    Args:
        directory: Directory to clean
        max_age_hours: Delete files older than this
        
    Returns:
        Number of files deleted
    """
    deleted_count = 0
    current_time = datetime.now().timestamp()

    if not os.path.exists(directory):
        return 0

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        file_age = current_time - os.path.getmtime(file_path)

        if file_age > (max_age_hours * 3600):
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    deleted_count += 1
            except Exception:
                pass

    return deleted_count


def read_file(file_path: str, mode: str = "r") -> str:
    """Read file content"""
    with open(file_path, mode) as f:
        return f.read()


def write_file(file_path: str, content: str, mode: str = "w") -> None:
    """Write content to file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, mode) as f:
        f.write(content)


def list_files_in_directory(directory: str, extension: str = None) -> List[str]:
    """List files in directory, optionally filtered by extension"""
    files = []
    
    if not os.path.exists(directory):
        return files

    for filename in os.listdir(directory):
        if extension and not filename.endswith(extension):
            continue
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            files.append(file_path)

    return files
