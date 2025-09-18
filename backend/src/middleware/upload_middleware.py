"""
File upload middleware and validation - Phase 1 手動動画管理システム
T054: File upload validation, security checks, and file management
"""
import os
import re
import uuid
import shutil
from pathlib import Path
from typing import Tuple, Dict, Optional, List, Any
from datetime import datetime


class FileUploadMiddleware:
    """File upload middleware with validation and security checks"""
    
    def __init__(self, upload_dir: str, max_file_size: int, allowed_types: List[str]):
        """
        Initialize file upload middleware
        
        Args:
            upload_dir: Directory to save uploaded files
            max_file_size: Maximum file size in bytes
            allowed_types: List of allowed MIME types
        """
        self.upload_dir = upload_dir
        self.max_file_size = max_file_size
        self.allowed_types = allowed_types
        
        # Ensure upload directory exists
        create_upload_directory(self.upload_dir)
    
    def validate_upload(self, file: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file for security and requirements
        
        Args:
            file: Uploaded file object with filename, content_type, size
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Validate filename security
            if not self._validate_filename_security(file.filename):
                return False, "Invalid filename: contains potentially dangerous characters"
            
            # Validate file type
            if not validate_file_type(file.content_type, self.allowed_types):
                allowed_str = ", ".join(self.allowed_types)
                return False, f"Invalid file type '{file.content_type}'. Allowed types: {allowed_str}"
            
            # Validate file size
            if not validate_file_size(file.size, self.max_file_size):
                max_mb = self.max_file_size / (1024 * 1024)
                actual_mb = file.size / (1024 * 1024)
                return False, f"File too large: {actual_mb:.1f}MB exceeds limit of {max_mb:.1f}MB"
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def save_file(self, file: Any) -> Dict[str, Any]:
        """
        Save uploaded file to upload directory
        
        Args:
            file: Validated uploaded file object
            
        Returns:
            Dictionary with file information
        """
        # Generate unique filename
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # Save file content
        file_content = file.read()
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Get actual file size after save
        actual_size = os.path.getsize(file_path)
        
        return {
            'filename': unique_filename,
            'original_filename': file.filename,
            'file_path': file_path,
            'file_size': actual_size,
            'content_type': file.content_type,
            'upload_timestamp': datetime.now().isoformat()
        }
    
    def _validate_filename_security(self, filename: str) -> bool:
        """
        Validate filename for security issues
        
        Args:
            filename: Original filename
            
        Returns:
            True if filename is safe
        """
        if not filename:
            return False
        
        # Check for path traversal attacks
        if '..' in filename or filename.startswith('/') or '\\' in filename:
            return False
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', '"', '|', ':', '*', '?', ';']
        if any(char in filename for char in dangerous_chars):
            return False
        
        # Check for control characters
        if any(ord(char) < 32 for char in filename):
            return False
        
        return True


def validate_file_type(content_type: str, allowed_types: List[str]) -> bool:
    """
    Validate file MIME type against allowed types
    
    Args:
        content_type: File MIME type
        allowed_types: List of allowed MIME types
        
    Returns:
        True if file type is allowed
    """
    return content_type in allowed_types


def validate_file_size(file_size: int, max_size: int) -> bool:
    """
    Validate file size against maximum allowed size
    
    Args:
        file_size: File size in bytes
        max_size: Maximum allowed size in bytes
        
    Returns:
        True if file size is within limit
    """
    return file_size <= max_size


def create_upload_directory(upload_dir: str) -> bool:
    """
    Create upload directory if it doesn't exist
    
    Args:
        upload_dir: Directory path to create
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        Path(upload_dir).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Failed to create upload directory {upload_dir}: {e}")
        return False


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate unique filename preserving extension
    
    Args:
        original_filename: Original filename from upload
        
    Returns:
        Unique filename with timestamp and UUID
    """
    # Extract file extension
    file_ext = Path(original_filename).suffix
    
    # Generate unique identifier
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    # Combine into unique filename
    unique_name = f"{timestamp}_{unique_id}{file_ext}"
    
    return unique_name