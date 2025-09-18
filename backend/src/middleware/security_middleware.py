"""
CORS and security headers middleware - Phase 1 手動動画管理システム
T055: Cross-Origin Resource Sharing and security headers implementation
"""
from typing import List, Dict, Any, Optional


class SecurityMiddleware:
    """CORS and security headers middleware"""
    
    def __init__(self, allowed_origins: List[str], allowed_methods: List[str], 
                 allowed_headers: List[str], max_age: int = 86400):
        """
        Initialize security middleware
        
        Args:
            allowed_origins: List of allowed CORS origins
            allowed_methods: List of allowed HTTP methods
            allowed_headers: List of allowed request headers
            max_age: CORS preflight cache time in seconds
        """
        self.allowed_origins = allowed_origins
        self.allowed_methods = allowed_methods
        self.allowed_headers = allowed_headers
        self.max_age = max_age
    
    def apply_cors(self, request: Any, response: Any) -> None:
        """
        Apply CORS headers to response
        
        Args:
            request: HTTP request object with headers and method
            response: HTTP response object with headers dict
        """
        cors_middleware(
            request, response, 
            self.allowed_origins, 
            self.allowed_methods, 
            self.allowed_headers,
            self.max_age
        )
    
    def apply_security_headers(self, response: Any) -> None:
        """
        Apply security headers to response
        
        Args:
            response: HTTP response object with headers dict
        """
        security_headers_middleware(response)


def cors_middleware(request: Any, response: Any, allowed_origins: List[str], 
                   allowed_methods: List[str], allowed_headers: List[str], 
                   max_age: int = 86400) -> None:
    """
    Apply CORS (Cross-Origin Resource Sharing) headers
    
    Args:
        request: HTTP request with headers and method
        response: HTTP response to add headers to
        allowed_origins: List of allowed origins
        allowed_methods: List of allowed HTTP methods
        allowed_headers: List of allowed request headers
        max_age: Preflight cache time in seconds
    """
    # Get origin from request
    origin = request.headers.get("Origin", "")
    
    # Check if origin is allowed
    if origin in allowed_origins:
        # Add CORS headers for allowed origin
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        
        # Add allowed methods
        response.headers["Access-Control-Allow-Methods"] = ", ".join(allowed_methods)
        
        # Add allowed headers
        response.headers["Access-Control-Allow-Headers"] = ", ".join(allowed_headers)
        
        # Handle preflight requests (OPTIONS method)
        if request.method == "OPTIONS":
            response.headers["Access-Control-Max-Age"] = str(max_age)
    
    # For non-CORS requests without origin, don't add CORS headers
    elif not origin:
        # Allow same-origin requests
        pass
    
    # For unauthorized origins, don't add CORS headers (implicit deny)


def security_headers_middleware(response: Any) -> None:
    """
    Apply security headers to prevent common attacks
    
    Args:
        response: HTTP response to add headers to
    """
    security_config = get_security_headers_config()
    
    # Apply all security headers
    for header_name, header_value in security_config.items():
        response.headers[header_name] = header_value


def get_cors_config() -> Dict[str, Any]:
    """
    Get CORS configuration for the application
    
    Returns:
        Dictionary with CORS settings
    """
    return {
        "allowed_origins": [
            # Local development
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            
            # Local network (Raspberry Pi common addresses)
            "http://192.168.1.100",
            "http://192.168.1.101",
            "http://192.168.1.102",
            "http://192.168.0.100",
            "http://192.168.0.101",
            
            # M5STACK and IoT device access
            "http://192.168.1.200",
            "http://192.168.1.201"
        ],
        "allowed_methods": [
            "GET", 
            "POST", 
            "PUT", 
            "DELETE", 
            "OPTIONS", 
            "HEAD"
        ],
        "allowed_headers": [
            "Content-Type",
            "Authorization", 
            "X-Requested-With",
            "Accept",
            "Origin",
            "X-CSRF-Token",
            "X-API-Key"
        ],
        "max_age": 86400  # 24 hours
    }


def get_security_headers_config() -> Dict[str, str]:
    """
    Get security headers configuration
    
    Returns:
        Dictionary with security header names and values
    """
    return {
        # Prevent MIME type sniffing attacks
        "X-Content-Type-Options": "nosniff",
        
        # Prevent clickjacking attacks
        "X-Frame-Options": "DENY",
        
        # Enable XSS protection (legacy, but still useful)
        "X-XSS-Protection": "1; mode=block",
        
        # Force HTTPS (in production)
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        
        # Content Security Policy - restrictive but functional
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "media-src 'self' data: blob:; "
            "connect-src 'self' ws: wss:; "
            "font-src 'self'; "
            "object-src 'none'; "
            "base-uri 'self';"
        ),
        
        # Control referrer information
        "Referrer-Policy": "strict-origin-when-cross-origin",
        
        # Disable DNS prefetching for privacy
        "X-DNS-Prefetch-Control": "off",
        
        # Prevent Flash/PDF from loading content
        "X-Permitted-Cross-Domain-Policies": "none"
    }