"""
Request/Response logging middleware - Phase 1 手動動画管理システム
T055: HTTP request/response logging with structured format and performance metrics
"""
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from src.utils.logger import get_logger


class LoggingMiddleware:
    """Request/response logging middleware with structured logging and metrics"""
    
    def __init__(self, 
                 log_requests: bool = True,
                 log_responses: bool = True,
                 log_request_body: bool = False,
                 log_response_body: bool = False,
                 exclude_paths: Optional[List[str]] = None,
                 max_body_size: int = 1024):
        """
        Initialize logging middleware
        
        Args:
            log_requests: Whether to log incoming requests
            log_responses: Whether to log outgoing responses
            log_request_body: Whether to include request body in logs
            log_response_body: Whether to include response body in logs
            exclude_paths: List of paths to exclude from logging
            max_body_size: Maximum body size to log (bytes)
        """
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.exclude_paths = exclude_paths or ['/health', '/status', '/metrics']
        self.max_body_size = max_body_size
        
        # Initialize loggers
        self.access_logger = get_logger("access", "logs/access.log")
        self.performance_logger = get_logger("performance", "logs/performance.log")
        self.error_logger = get_logger("error", "logs/errors.log")
    
    def log_request(self, request: Any, session_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Log incoming HTTP request
        
        Args:
            request: HTTP request object
            session_info: Optional session information
            
        Returns:
            Request context dictionary for response logging
        """
        start_time = time.time()
        request_id = self._generate_request_id()
        
        # Check if path should be excluded
        path = getattr(request.url, 'path', str(request.url))
        if self._should_exclude_path(path):
            return {
                'request_id': request_id,
                'start_time': start_time,
                'excluded': True
            }
        
        if self.log_requests:
            log_data = self._build_request_log_data(request, request_id, session_info)
            self.access_logger.info("Request received", extra=log_data)
        
        return {
            'request_id': request_id,
            'start_time': start_time,
            'excluded': False,
            'path': path,
            'method': getattr(request, 'method', 'UNKNOWN')
        }
    
    def log_response(self, request: Any, response: Any, 
                    request_context: Dict[str, Any]) -> None:
        """
        Log outgoing HTTP response
        
        Args:
            request: HTTP request object
            response: HTTP response object
            request_context: Request context from log_request
        """
        # Skip if request was excluded
        if request_context.get('excluded', False):
            return
        
        if self.log_responses:
            end_time = time.time()
            response_time = end_time - request_context['start_time']
            
            log_data = self._build_response_log_data(
                request, response, request_context, response_time
            )
            
            # Log to access log
            self.access_logger.info("Request completed", extra=log_data)
            
            # Log performance metrics for slow requests
            if response_time > 1.0:  # Log slow requests (> 1 second)
                perf_data = self._build_performance_log_data(
                    request_context, response_time, response
                )
                self.performance_logger.warning("Slow request detected", extra=perf_data)
    
    def log_error(self, request: Any, error: Exception, 
                 request_context: Dict[str, Any]) -> None:
        """
        Log request error
        
        Args:
            request: HTTP request object
            error: Exception that occurred
            request_context: Request context from log_request
        """
        if request_context.get('excluded', False):
            return
        
        end_time = time.time()
        response_time = end_time - request_context['start_time']
        
        error_data = self._build_error_log_data(
            request, error, request_context, response_time
        )
        
        self.error_logger.error("Request failed", extra=error_data)
    
    def _generate_request_id(self) -> str:
        """
        Generate unique request ID
        
        Returns:
            Request ID string
        """
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _should_exclude_path(self, path: str) -> bool:
        """
        Check if path should be excluded from logging
        
        Args:
            path: Request path
            
        Returns:
            True if path should be excluded
        """
        return any(excluded in path for excluded in self.exclude_paths)
    
    def _build_request_log_data(self, request: Any, request_id: str,
                               session_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Build structured log data for request
        
        Args:
            request: HTTP request object
            request_id: Request ID
            session_info: Optional session information
            
        Returns:
            Log data dictionary
        """
        log_data = {
            'event_type': 'request',
            'request_id': request_id,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'method': getattr(request, 'method', 'UNKNOWN'),
            'path': getattr(request.url, 'path', str(request.url)),
            'query_params': dict(getattr(request.url, 'query', {})) if hasattr(request, 'url') else {},
            'headers': self._sanitize_headers(dict(request.headers)) if hasattr(request, 'headers') else {},
            'client_ip': self._get_client_ip(request),
            'user_agent': getattr(request.headers, 'get', lambda x, y: None)('User-Agent', None) if hasattr(request, 'headers') else None
        }
        
        # Add session info if available
        if session_info:
            log_data.update({
                'session_id': session_info.get('session_id'),
                'device_id': session_info.get('device_id'),
                'device_type': session_info.get('device_type')
            })
        
        # Add request body if enabled
        if self.log_request_body and hasattr(request, 'body'):
            try:
                body = request.body
                if len(body) <= self.max_body_size:
                    log_data['request_body'] = self._safe_decode_body(body)
                else:
                    log_data['request_body_size'] = len(body)
                    log_data['request_body'] = '[TRUNCATED - Too Large]'
            except Exception:
                log_data['request_body'] = '[COULD NOT READ]'
        
        return log_data
    
    def _build_response_log_data(self, request: Any, response: Any,
                                request_context: Dict[str, Any], 
                                response_time: float) -> Dict[str, Any]:
        """
        Build structured log data for response
        
        Args:
            request: HTTP request object
            response: HTTP response object
            request_context: Request context from log_request
            response_time: Response time in seconds
            
        Returns:
            Log data dictionary
        """
        log_data = {
            'event_type': 'response',
            'request_id': request_context['request_id'],
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'method': request_context.get('method', 'UNKNOWN'),
            'path': request_context.get('path', ''),
            'status_code': getattr(response, 'status_code', 0),
            'response_time_ms': round(response_time * 1000, 2),
            'response_size': self._get_response_size(response)
        }
        
        # Add response headers
        if hasattr(response, 'headers'):
            log_data['response_headers'] = self._sanitize_headers(dict(response.headers))
        
        # Add response body if enabled
        if self.log_response_body and hasattr(response, 'body'):
            try:
                body = response.body
                if len(body) <= self.max_body_size:
                    log_data['response_body'] = self._safe_decode_body(body)
                else:
                    log_data['response_body_size'] = len(body)
                    log_data['response_body'] = '[TRUNCATED - Too Large]'
            except Exception:
                log_data['response_body'] = '[COULD NOT READ]'
        
        return log_data
    
    def _build_performance_log_data(self, request_context: Dict[str, Any],
                                   response_time: float, response: Any) -> Dict[str, Any]:
        """
        Build performance log data for slow requests
        
        Args:
            request_context: Request context
            response_time: Response time in seconds
            response: HTTP response object
            
        Returns:
            Performance log data dictionary
        """
        return {
            'event_type': 'performance',
            'request_id': request_context['request_id'],
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'method': request_context.get('method'),
            'path': request_context.get('path'),
            'response_time_ms': round(response_time * 1000, 2),
            'status_code': getattr(response, 'status_code', 0),
            'performance_category': self._categorize_performance(response_time),
            'needs_optimization': response_time > 5.0  # Flag very slow requests
        }
    
    def _build_error_log_data(self, request: Any, error: Exception,
                             request_context: Dict[str, Any], 
                             response_time: float) -> Dict[str, Any]:
        """
        Build error log data for failed requests
        
        Args:
            request: HTTP request object
            error: Exception that occurred
            request_context: Request context
            response_time: Response time in seconds
            
        Returns:
            Error log data dictionary
        """
        return {
            'event_type': 'error',
            'request_id': request_context['request_id'],
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'method': request_context.get('method'),
            'path': request_context.get('path'),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'response_time_ms': round(response_time * 1000, 2),
            'client_ip': self._get_client_ip(request),
            'user_agent': getattr(request.headers, 'get', lambda x, y: None)('User-Agent', None) if hasattr(request, 'headers') else None
        }
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        Sanitize headers by removing sensitive information
        
        Args:
            headers: Request/response headers dictionary
            
        Returns:
            Sanitized headers dictionary
        """
        sensitive_headers = {
            'authorization', 'cookie', 'x-api-key', 'x-auth-token', 
            'x-csrf-token', 'set-cookie'
        }
        
        sanitized = {}
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = value
                
        return sanitized
    
    def _get_client_ip(self, request: Any) -> str:
        """
        Get client IP from request
        
        Args:
            request: HTTP request object
            
        Returns:
            Client IP address
        """
        if hasattr(request, 'headers'):
            # Check forwarded headers
            forwarded_for = request.headers.get('X-Forwarded-For')
            if forwarded_for:
                return forwarded_for.split(',')[0].strip()
            
            real_ip = request.headers.get('X-Real-IP')
            if real_ip:
                return real_ip
        
        # Fall back to client address
        if hasattr(request, 'client') and hasattr(request.client, 'host'):
            return request.client.host
        
        return '127.0.0.1'
    
    def _get_response_size(self, response: Any) -> Optional[int]:
        """
        Get response content size
        
        Args:
            response: HTTP response object
            
        Returns:
            Response size in bytes or None
        """
        if hasattr(response, 'headers'):
            content_length = response.headers.get('Content-Length')
            if content_length:
                try:
                    return int(content_length)
                except ValueError:
                    pass
        
        if hasattr(response, 'body'):
            try:
                return len(response.body)
            except (TypeError, AttributeError):
                pass
        
        return None
    
    def _safe_decode_body(self, body: bytes) -> str:
        """
        Safely decode request/response body
        
        Args:
            body: Body bytes
            
        Returns:
            Decoded string or error message
        """
        try:
            decoded = body.decode('utf-8')
            # Try to parse as JSON for better formatting
            try:
                parsed = json.loads(decoded)
                return json.dumps(parsed, separators=(',', ':'))  # Compact JSON
            except json.JSONDecodeError:
                return decoded
        except UnicodeDecodeError:
            return f'[BINARY DATA - {len(body)} bytes]'
    
    def _categorize_performance(self, response_time: float) -> str:
        """
        Categorize request performance
        
        Args:
            response_time: Response time in seconds
            
        Returns:
            Performance category string
        """
        if response_time < 0.1:
            return 'fast'
        elif response_time < 0.5:
            return 'acceptable'
        elif response_time < 1.0:
            return 'slow'
        elif response_time < 5.0:
            return 'very_slow'
        else:
            return 'critical'


def create_logging_middleware(log_request_body: bool = False,
                             log_response_body: bool = False) -> LoggingMiddleware:
    """
    Create logging middleware instance
    
    Args:
        log_request_body: Whether to log request bodies
        log_response_body: Whether to log response bodies
        
    Returns:
        LoggingMiddleware instance
    """
    return LoggingMiddleware(
        log_request_body=log_request_body,
        log_response_body=log_response_body
    )


def log_api_access(request: Any, response: Any, 
                  response_time: float, session_info: Optional[Dict[str, Any]] = None) -> None:
    """
    Utility function to log API access
    
    Args:
        request: HTTP request object
        response: HTTP response object
        response_time: Response time in seconds
        session_info: Optional session information
    """
    middleware = create_logging_middleware()
    request_context = middleware.log_request(request, session_info)
    middleware.log_response(request, response, request_context)