"""
Contract test for Database connection and migration
T053: This test MUST FAIL initially (TDD Red phase)
"""
import pytest
import os
import tempfile
from pathlib import Path
from sqlalchemy import text

# This import will FAIL because the module doesn't exist yet
from src.database.connection import DatabaseConnection, init_database, get_database_path


class TestDatabaseConnectionContract:
    """Contract tests for database connection and migration functionality"""
    
    def setup_method(self):
        """Setup test with temporary database"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test.db")
    
    def teardown_method(self):
        """Cleanup test database"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        try:
            os.rmdir(self.temp_dir)
        except OSError:
            pass  # Directory might not be empty due to other files
    
    def test_database_connection_initialization(self):
        """
        DatabaseConnection should initialize properly with SQLite
        Expected to FAIL: class doesn't exist yet
        """
        db_conn = DatabaseConnection(self.test_db_path)
        
        # Contract: Database connection should be created
        assert db_conn is not None
        assert hasattr(db_conn, 'engine')
        assert hasattr(db_conn, 'session_factory')
        assert hasattr(db_conn, 'create_tables')
        assert hasattr(db_conn, 'drop_tables')
        assert hasattr(db_conn, 'get_session')
    
    def test_database_tables_creation(self):
        """
        create_tables() should create all required tables with proper schema
        """
        db_conn = DatabaseConnection(self.test_db_path)
        
        # Create tables
        db_conn.create_tables()
        
        # Contract: Database file should exist
        assert os.path.exists(self.test_db_path)
        
        # Contract: All required tables should exist
        with db_conn.get_session() as session:
            # Check if tables exist by querying their schema
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            table_names = [row[0] for row in result.fetchall()]
            
            required_tables = [
                'videos', 
                'display_sessions', 
                'user_devices', 
                'system_status', 
                'control_events'
            ]
            
            for table_name in required_tables:
                assert table_name in table_names, f"Table {table_name} not found"
    
    def test_get_database_path_function(self):
        """
        get_database_path() should return appropriate database path
        """
        db_path = get_database_path()
        
        # Contract: Should return string path
        assert isinstance(db_path, (str, Path))
        
        # Contract: Should be a reasonable database path
        db_path_str = str(db_path)
        assert db_path_str.endswith('.db') or 'database' in db_path_str
    
    def test_init_database_function(self):
        """
        init_database() function should initialize database with default data
        """
        # Should work with custom path
        init_result = init_database(self.test_db_path)
        
        # Contract: Should return success indicator
        assert init_result == True or init_result is None  # Success
        
        # Contract: Database should exist and be functional
        assert os.path.exists(self.test_db_path)
        
        # Should be able to connect to initialized database
        db_conn = DatabaseConnection(self.test_db_path)
        with db_conn.get_session() as session:
            # Should have tables
            result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            tables = [row[0] for row in result.fetchall()]
            assert len(tables) >= 5  # At least our 5 main tables