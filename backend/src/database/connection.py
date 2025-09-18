"""
Database connection and migration - Phase 1 手動動画管理システム
T053: SQLite database connection, table creation, and schema management
"""
import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool


class DatabaseConnection:
    """SQLite database connection manager with proper session handling"""
    
    def __init__(self, db_path: str):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Create SQLAlchemy engine with SQLite-specific settings
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            poolclass=StaticPool,
            connect_args={
                'check_same_thread': False,
                'timeout': 20,
            },
            echo=False  # Set to True for SQL debugging
        )
        
        # Enable foreign key constraints for SQLite
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()
        
        # Create session factory
        self.session_factory = sessionmaker(bind=self.engine)
    
    def create_tables(self) -> None:
        """Create all database tables with proper schema"""
        with self.engine.connect() as conn:
            # Videos table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS videos (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    file_path TEXT UNIQUE NOT NULL,
                    file_size INTEGER NOT NULL,
                    duration REAL NOT NULL,
                    format TEXT NOT NULL DEFAULT 'mp4',
                    resolution TEXT,
                    thumbnail_path TEXT,
                    upload_timestamp DATETIME NOT NULL,
                    last_played DATETIME,
                    play_count INTEGER DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'processing',
                    CHECK (file_size <= 524288000),
                    CHECK (status IN ('active', 'archived', 'processing', 'error'))
                )
            """))
            
            # Display Sessions table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS display_sessions (
                    id TEXT PRIMARY KEY,
                    video_id TEXT NOT NULL,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    session_type TEXT NOT NULL DEFAULT 'manual',
                    current_position REAL DEFAULT 0.0,
                    playback_status TEXT NOT NULL DEFAULT 'stopped',
                    display_mode TEXT NOT NULL DEFAULT 'fullscreen',
                    loop_enabled BOOLEAN DEFAULT FALSE,
                    created_by TEXT NOT NULL,
                    FOREIGN KEY (video_id) REFERENCES videos(id),
                    CHECK (session_type IN ('manual', 'scheduled', 'loop')),
                    CHECK (playback_status IN ('playing', 'paused', 'stopped', 'loading')),
                    CHECK (display_mode IN ('fullscreen', 'windowed'))
                )
            """))
            
            # User Devices table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_devices (
                    id TEXT PRIMARY KEY,
                    device_type TEXT NOT NULL,
                    device_name TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    last_seen DATETIME NOT NULL,
                    session_count INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    CHECK (device_type IN ('web_browser', 'm5stack'))
                )
            """))
            
            # System Status table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS system_status (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    uptime INTEGER,
                    active_sessions INTEGER DEFAULT 0,
                    total_videos INTEGER DEFAULT 0,
                    m5stack_status TEXT DEFAULT 'offline',
                    display_status TEXT DEFAULT 'idle',
                    api_status TEXT DEFAULT 'healthy',
                    CHECK (cpu_usage >= 0 AND cpu_usage <= 100),
                    CHECK (memory_usage >= 0 AND memory_usage <= 100),
                    CHECK (disk_usage >= 0 AND disk_usage <= 100)
                )
            """))
            
            # Control Events table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS control_events (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    device_id TEXT,
                    event_type TEXT NOT NULL,
                    event_data JSON,
                    timestamp DATETIME NOT NULL,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT,
                    FOREIGN KEY (session_id) REFERENCES display_sessions(id),
                    FOREIGN KEY (device_id) REFERENCES user_devices(id),
                    CHECK (event_type IN ('play', 'pause', 'stop', 'next', 'previous', 'volume', 'upload'))
                )
            """))
            
            # Create indexes for performance
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_videos_upload_time ON videos(upload_timestamp DESC)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_sessions_video_id ON display_sessions(video_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON display_sessions(start_time DESC)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON control_events(timestamp DESC)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_events_session_id ON control_events(session_id)"))
            
            conn.commit()
    
    def drop_tables(self) -> None:
        """Drop all database tables (useful for testing)"""
        with self.engine.connect() as conn:
            # Drop in reverse order to handle foreign key constraints
            tables = [
                'control_events',
                'system_status', 
                'user_devices',
                'display_sessions',
                'videos'
            ]
            
            for table in tables:
                conn.execute(text(f"DROP TABLE IF EXISTS {table}"))
            
            conn.commit()
    
    @contextmanager
    def get_session(self):
        """
        Get database session with proper cleanup
        
        Usage:
            with db_conn.get_session() as session:
                session.execute("SELECT * FROM videos")
        """
        session = self.session_factory()
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


def get_database_path(environment: Optional[str] = None) -> str:
    """
    Get appropriate database path based on environment
    
    Args:
        environment: 'test', 'dev', 'prod', or None for default
        
    Returns:
        Path to database file
    """
    if environment == 'test':
        return ":memory:"  # In-memory database for testing
    
    # Default to local database file
    db_dir = Path(__file__).parent.parent.parent / "data"
    db_dir.mkdir(exist_ok=True)
    
    if environment == 'prod':
        return str(db_dir / "ai_painting_production.db")
    else:  # dev or default
        return str(db_dir / "ai_painting_development.db")


def init_database(db_path: Optional[str] = None) -> bool:
    """
    Initialize database with schema and optional default data
    
    Args:
        db_path: Custom database path, or None for default
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if db_path is None:
            db_path = get_database_path()
        
        # Create database connection and tables
        db_conn = DatabaseConnection(db_path)
        db_conn.create_tables()
        
        # Optional: Add default data for development
        _add_default_data(db_conn)
        
        return True
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False


def _add_default_data(db_conn: DatabaseConnection) -> None:
    """Add default data for development and testing"""
    try:
        with db_conn.get_session() as session:
            # Check if default data already exists
            result = session.execute(text("SELECT COUNT(*) FROM videos"))
            if result.fetchone()[0] > 0:
                return  # Data already exists
            
            # Add sample video entry for testing
            session.execute(text("""
                INSERT INTO videos (
                    id, title, file_path, file_size, duration, format,
                    upload_timestamp, status
                ) VALUES (
                    'sample-video-123',
                    'Sample Video for Testing',
                    '/data/videos/sample.mp4',
                    5000000,
                    120.5,
                    'mp4',
                    datetime('now'),
                    'active'
                )
            """))
            
            # Add default device entries
            session.execute(text("""
                INSERT INTO user_devices (
                    id, device_type, device_name, ip_address,
                    user_agent, last_seen, session_count, is_active
                ) VALUES (
                    'localhost-browser',
                    'web_browser',
                    'Localhost Browser',
                    '127.0.0.1',
                    'Development Browser',
                    datetime('now'),
                    0,
                    1
                )
            """))
            
            session.execute(text("""
                INSERT INTO user_devices (
                    id, device_type, device_name, ip_address,
                    user_agent, last_seen, session_count, is_active
                ) VALUES (
                    'm5stack-default',
                    'm5stack',
                    'M5STACK Core2',
                    '192.168.1.100',
                    'M5STACK/1.0',
                    datetime('now'),
                    0,
                    0
                )
            """))
            
            session.commit()
            
    except Exception as e:
        print(f"Warning: Could not add default data: {e}")
        # Don't fail initialization if default data fails