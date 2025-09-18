"""
Error handling and exception middleware - Phase 1 手動動画管理システム
T057: Comprehensive error handling with logging and security considerations
"""
import re
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Callable, Type
from src.utils.logger import get_logger, log_error as logger_log_error


class ErrorHandlingMiddleware:
    """Error handling middleware with customizable handlers and security features"""
    
    def __init__(self, debug_mode: bool = False, log_errors: bool = True, 
                 return_stack_trace: bool = False, 
                 custom_error_handlers: Optional[Dict[Type[Exception], Callable]] = None):
        """
        Initialize error handling middleware
        
        Args:
            debug_mode: Enable debug information in responses
            log_errors: Whether to log errors
            return_stack_trace: Include stack trace in responses (debug only)
            custom_error_handlers: Custom handlers for specific exception types
        """
        self.debug_mode = debug_mode
        self.log_errors = log_errors
        self.return_stack_trace = return_stack_trace and debug_mode  # Only in debug mode
        self.custom_error_handlers = custom_error_handlers or {}
        
        # Get logger for error handling
        self.logger = get_logger("error_middleware", "logs/errors.log")
    
    def handle_error(self, error: Exception, request: Any) -> Dict[str, Any]:
        """
        Handle error with appropriate response formatting
        
        Args:
            error: Exception that occurred
            request: HTTP request object
            
        Returns:
            Formatted error response dictionary
        """
        # Check for custom handlers first
        error_type = type(error)
        if error_type in self.custom_error_handlers:
            return self.custom_error_handlers[error_type](error, request)
        
        # Log error if enabled
        if self.log_errors:
            log_error_context(error, request)
        
        # Handle specific error types
        if isinstance(error, ValueError):
            return handle_validation_error(error, request)
        elif "database" in str(error).lower() or "connection" in str(error).lower():
            return handle_database_error(error, request)
        elif "upload" in str(error).lower() or "file" in str(error).lower():
            return handle_file_upload_error(error, request)
        else:
            return handle_generic_error(error, request, self.debug_mode, self.return_stack_trace)
    
    def process_exception(self, error: Exception, request: Any) -> Optional[Dict[str, Any]]:
        """
        Process exception for middleware integration
        
        Args:
            error: Exception that occurred
            request: HTTP request object
            
        Returns:
            Error response or None to continue processing
        """
        try:
            return self.handle_error(error, request)
        except Exception as middleware_error:
            # Fallback error handling
            if self.log_errors:
                self.logger.error(f"Error in error middleware: {middleware_error}")
            
            return format_error_response(
                "MIDDLEWARE_ERROR",
                "An error occurred while processing the error",
                500
            )


def handle_validation_error(error: Exception, request: Any) -> Dict[str, Any]:
    """
    Handle validation errors (400 Bad Request)
    
    Args:
        error: Validation error
        request: HTTP request object
        
    Returns:
        Formatted validation error response
    """
    error_message = str(error)
    
    # Extract validation details if possible
    details = {}
    if "size" in error_message.lower():
        details["type"] = "file_size_validation"
    elif "type" in error_message.lower():
        details["type"] = "file_type_validation"
    elif "format" in error_message.lower():
        details["type"] = "format_validation"
    
    return format_error_response(
        "VALIDATION_ERROR",
        f"Validation failed: {error_message}",
        400,
        details if details else None
    )


def handle_database_error(error: Exception, request: Any) -> Dict[str, Any]:
    """
    Handle database errors (500 Internal Server Error)
    
    Args:
        error: Database error
        request: HTTP request object
        
    Returns:
        Formatted database error response
    """
    # Sanitize error message to avoid exposing sensitive info
    error_message = "Database operation failed"
    
    # Check for common database issues
    error_str = str(error).lower()
    if "connection" in error_str:
        error_message = "Database connection unavailable"
    elif "timeout" in error_str:
        error_message = "Database operation timed out"
    elif "constraint" in error_str or "unique" in error_str:
        error_message = "Data constraint violation"
    
    return format_error_response(
        "DATABASE_ERROR",
        error_message,
        500
    )


def handle_file_upload_error(error: Exception, request: Any) -> Dict[str, Any]:
    """
    Handle file upload errors (507 Insufficient Storage or 500)
    
    Args:
        error: File upload error
        request: HTTP request object
        
    Returns:
        Formatted file upload error response
    """
    error_str = str(error).lower()
    
    # Determine appropriate status code and message
    if "disk" in error_str or "space" in error_str:
        status_code = 507  # Insufficient Storage
        message = "Insufficient storage space for file upload"
    elif "size" in error_str:
        status_code = 413  # Payload Too Large
        message = "Uploaded file is too large"
    elif "permission" in error_str:
        status_code = 403  # Forbidden
        message = "Permission denied for file upload"
    else:
        status_code = 500  # Internal Server Error
        message = "File upload operation failed"
    
    return format_error_response(
        "FILE_UPLOAD_ERROR",
        message,
        status_code
    )


def handle_generic_error(error: Exception, request: Any, debug_mode: bool = False, 
                        return_stack_trace: bool = False) -> Dict[str, Any]:
    """
    Handle generic/unexpected errors (500 Internal Server Error)
    
    Args:
        error: Generic error
        request: HTTP request object
        debug_mode: Whether debug mode is enabled
        return_stack_trace: Whether to include stack trace
        
    Returns:
        Formatted generic error response
    """
    if debug_mode:
        message = f"Internal error: {str(error)}"
    else:
        message = "An internal server error occurred"
    
    details = None
    if debug_mode and return_stack_trace:
        details = {
            "exception_type": type(error).__name__,
            "stack_trace": traceback.format_exception(type(error), error, error.__traceback__)
        }
    
    return format_error_response(
        "INTERNAL_ERROR",
        message,
        500,
        details
    )


def format_error_response(error_code: str, message: str, status_code: int, 
                         details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Format error response with consistent structure
    
    Args:
        error_code: Error code identifier
        message: Human-readable error message
        status_code: HTTP status code
        details: Optional additional error details
        
    Returns:
        Formatted error response dictionary
    """
    response = {
        "error": {
            "code": error_code,
            "message": _sanitize_error_message(message)
        },
        "status_code": status_code,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    if details:
        response["error"]["details"] = details
    
    return response


def log_error_context(error: Exception, request: Any, 
                     additional_context: Optional[Dict[str, Any]] = None) -> bool:
    """
    Log error with request context information
    
    Args:
        error: Exception that occurred
        request: HTTP request object
        additional_context: Additional context information
        
    Returns:
        True if logged successfully
    """
    try:
        context = {
            "request_method": getattr(request, 'method', 'UNKNOWN'),
            "request_url": getattr(request, 'url', 'UNKNOWN'),
            "user_agent": getattr(request.headers, 'get', lambda x, y: 'UNKNOWN')('User-Agent', 'UNKNOWN'),
            "error_type": type(error).__name__,
            "error_message": str(error)
        }
        
        if additional_context:
            context.update(additional_context)
        
        return logger_log_error(error, context)
        
    except Exception as log_error:
        # Fallback logging to prevent logging errors from breaking the app
        print(f"Failed to log error context: {log_error}")
        return False


def _sanitize_error_message(message: str) -> str:
    """
    Sanitize error message to remove sensitive information
    
    Args:
        message: Original error message
        
    Returns:
        Sanitized error message
    """
    # Patterns to remove/replace sensitive information
    sensitive_patterns = [
        (r'password\s*[\'"][^\'\"]*[\'"]', 'password [REDACTED]'),
        (r'token\s*[\'"][^\'\"]*[\'"]', 'token [REDACTED]'),
        (r'key\s*[\'"][^\'\"]*[\'"]', 'key [REDACTED]'),
        (r'secret\s*[\'"][^\'\"]*[\'"]', 'secret [REDACTED]'),
        (r'\b\d{4}-\d{4}-\d{4}-\d{4}\b', 'XXXX-XXXX-XXXX-XXXX'),  # Credit card numbers
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),  # Email addresses
    ]
    
    sanitized = message
    for pattern, replacement in sensitive_patterns:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    
    return sanitized