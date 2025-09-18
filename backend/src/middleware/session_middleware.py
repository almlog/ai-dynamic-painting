"""
Session management middleware - Phase 1 手動動画管理システム
T054: Simple session management for device tracking and user interaction
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from src.database.connection import DatabaseConnection, get_database_path
from sqlalchemy import text


class SessionMiddleware:
    """Session management middleware for device tracking and basic session handling"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None, 
                 session_timeout: int = 86400):
        """
        Initialize session middleware
        
        Args:
            db_connection: Database connection for session storage
            session_timeout: Session timeout in seconds (default: 24 hours)
        """
        self.db_connection = db_connection or DatabaseConnection(get_database_path())
        self.session_timeout = session_timeout
        self.active_sessions: Dict[str, Dict[str, Any]] = {}  # In-memory cache
    
    def process_request(self, request: Any) -> Dict[str, Any]:
        """
        Process incoming request for session management
        
        Args:
            request: HTTP request object with headers
            
        Returns:
            Dictionary with session info and device info
        """
        # Extract session info from request
        session_id = self._extract_session_id(request)
        device_info = self._extract_device_info(request)
        
        # Create or update session
        session_data = self._get_or_create_session(session_id, device_info)
        
        # Update last seen time
        self._update_device_activity(session_data['device_id'])
        
        return {
            'session_id': session_data['session_id'],
            'device_id': session_data['device_id'],
            'device_type': session_data['device_type'],
            'is_new_session': session_data.get('is_new_session', False)
        }
    
    def _extract_session_id(self, request: Any) -> Optional[str]:
        """
        Extract session ID from request headers or cookies
        
        Args:
            request: HTTP request object
            
        Returns:
            Session ID string or None
        """
        # Try to get session ID from various sources
        session_id = None
        
        # Check X-Session-ID header
        if hasattr(request, 'headers'):
            session_id = request.headers.get('X-Session-ID')
        
        # Check Authorization header for session-based auth
        if not session_id and hasattr(request, 'headers'):
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Session '):
                session_id = auth_header.replace('Session ', '')
        
        # TODO: Add cookie support when needed
        
        return session_id
    
    def _extract_device_info(self, request: Any) -> Dict[str, Any]:
        """
        Extract device information from request
        
        Args:
            request: HTTP request object
            
        Returns:
            Dictionary with device information
        """
        user_agent = getattr(request.headers, 'get', lambda x, y: 'Unknown')('User-Agent', 'Unknown')
        client_ip = self._get_client_ip(request)
        
        # Determine device type from User-Agent
        device_type = 'web_browser'
        device_name = 'Web Browser'
        
        if 'M5STACK' in user_agent or 'ESP32' in user_agent:
            device_type = 'm5stack'
            device_name = 'M5STACK Core2'
        elif 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
            device_type = 'web_browser'
            device_name = 'Mobile Browser'
        elif 'curl' in user_agent.lower():
            device_type = 'api_client'
            device_name = 'API Client'
        
        return {
            'device_type': device_type,
            'device_name': device_name,
            'ip_address': client_ip,
            'user_agent': user_agent
        }
    
    def _get_client_ip(self, request: Any) -> str:
        """
        Get client IP address from request
        
        Args:
            request: HTTP request object
            
        Returns:
            Client IP address string
        """
        # Try to get real IP from various headers
        if hasattr(request, 'headers'):
            # Check X-Forwarded-For header
            forwarded_for = request.headers.get('X-Forwarded-For')
            if forwarded_for:
                return forwarded_for.split(',')[0].strip()
            
            # Check X-Real-IP header
            real_ip = request.headers.get('X-Real-IP')
            if real_ip:
                return real_ip
        
        # Fall back to request client address
        if hasattr(request, 'client'):
            if hasattr(request.client, 'host'):
                return request.client.host
        
        return '127.0.0.1'  # Default fallback
    
    def _get_or_create_session(self, session_id: Optional[str], 
                              device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get existing session or create new one
        
        Args:
            session_id: Existing session ID or None
            device_info: Device information dictionary
            
        Returns:
            Session data dictionary
        """
        # Check if session exists and is valid
        if session_id and self._is_session_valid(session_id):
            session_data = self._get_session_data(session_id)
            if session_data:
                return session_data
        
        # Create new session
        return self._create_new_session(device_info)
    
    def _is_session_valid(self, session_id: str) -> bool:
        """
        Check if session is valid and not expired
        
        Args:
            session_id: Session ID to check
            
        Returns:
            True if session is valid
        """
        try:
            with self.db_connection.get_session() as session:
                result = session.execute(
                    text("SELECT last_seen FROM user_devices WHERE id = :session_id"),
                    {"session_id": session_id}
                ).fetchone()
                
                if not result:
                    return False
                
                # Check if session is expired
                last_seen = datetime.fromisoformat(result[0])
                expiry_time = last_seen + timedelta(seconds=self.session_timeout)
                
                return datetime.now() < expiry_time
                
        except Exception:
            return False
    
    def _get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data from database
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data dictionary or None
        """
        try:
            with self.db_connection.get_session() as session:
                result = session.execute(
                    text("""
                        SELECT id, device_type, device_name, ip_address, 
                               user_agent, session_count, is_active
                        FROM user_devices 
                        WHERE id = :session_id AND is_active = 1
                    """),
                    {"session_id": session_id}
                ).fetchone()
                
                if result:
                    return {
                        'session_id': result[0],
                        'device_id': result[0],
                        'device_type': result[1],
                        'device_name': result[2],
                        'ip_address': result[3],
                        'user_agent': result[4],
                        'session_count': result[5],
                        'is_active': result[6],
                        'is_new_session': False
                    }
                    
        except Exception:
            pass
        
        return None
    
    def _create_new_session(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new session in database
        
        Args:
            device_info: Device information dictionary
            
        Returns:
            New session data dictionary
        """
        session_id = str(uuid.uuid4())
        device_id = f"{device_info['device_type']}-{session_id[:8]}"
        
        try:
            with self.db_connection.get_session() as session:
                # Insert new device/session record
                session.execute(
                    text("""
                        INSERT INTO user_devices (
                            id, device_type, device_name, ip_address,
                            user_agent, last_seen, session_count, is_active
                        ) VALUES (
                            :device_id, :device_type, :device_name, :ip_address,
                            :user_agent, :last_seen, 1, 1
                        )
                    """),
                    {
                        'device_id': device_id,
                        'device_type': device_info['device_type'],
                        'device_name': device_info['device_name'],
                        'ip_address': device_info['ip_address'],
                        'user_agent': device_info['user_agent'],
                        'last_seen': datetime.now().isoformat()
                    }
                )
                session.commit()
                
        except Exception as e:
            # If database insert fails, still provide session data
            print(f"Warning: Could not store session in database: {e}")
        
        return {
            'session_id': session_id,
            'device_id': device_id,
            'device_type': device_info['device_type'],
            'device_name': device_info['device_name'],
            'ip_address': device_info['ip_address'],
            'user_agent': device_info['user_agent'],
            'session_count': 1,
            'is_active': True,
            'is_new_session': True
        }
    
    def _update_device_activity(self, device_id: str) -> None:
        """
        Update device last seen timestamp
        
        Args:
            device_id: Device ID to update
        """
        try:
            with self.db_connection.get_session() as session:
                session.execute(
                    text("""
                        UPDATE user_devices 
                        SET last_seen = :last_seen,
                            session_count = session_count + 1
                        WHERE id = :device_id
                    """),
                    {
                        'device_id': device_id,
                        'last_seen': datetime.now().isoformat()
                    }
                )
                session.commit()
                
        except Exception as e:
            print(f"Warning: Could not update device activity: {e}")
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions from database
        
        Returns:
            Number of sessions cleaned up
        """
        try:
            cutoff_time = datetime.now() - timedelta(seconds=self.session_timeout)
            
            with self.db_connection.get_session() as session:
                result = session.execute(
                    text("""
                        UPDATE user_devices 
                        SET is_active = 0 
                        WHERE last_seen < :cutoff_time AND is_active = 1
                    """),
                    {'cutoff_time': cutoff_time.isoformat()}
                )
                session.commit()
                
                return result.rowcount
                
        except Exception as e:
            print(f"Warning: Could not cleanup expired sessions: {e}")
            return 0


def create_session_middleware(db_connection: Optional[DatabaseConnection] = None) -> SessionMiddleware:
    """
    Create session middleware instance
    
    Args:
        db_connection: Optional database connection
        
    Returns:
        SessionMiddleware instance
    """
    return SessionMiddleware(db_connection)


def get_session_info_from_request(request: Any, 
                                 session_middleware: Optional[SessionMiddleware] = None) -> Dict[str, Any]:
    """
    Utility function to get session info from request
    
    Args:
        request: HTTP request object
        session_middleware: Optional session middleware instance
        
    Returns:
        Session information dictionary
    """
    if not session_middleware:
        session_middleware = create_session_middleware()
    
    return session_middleware.process_request(request)