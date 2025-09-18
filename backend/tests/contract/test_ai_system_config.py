"""
Contract test for AISystemConfig model
Test File: backend/tests/contract/test_ai_system_config.py

This test MUST FAIL initially (RED phase of TDD)
"""

import pytest
from pathlib import Path
import sys
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_ai_system_config_model_exists():
    """Test that AISystemConfig model exists and has required fields"""
    # This should initially FAIL until we implement the model
    try:
        from src.ai.models.ai_system_config import AISystemConfig
        
        # Test model can be instantiated
        config = AISystemConfig()
        assert config is not None
        
        # Test required fields exist
        required_fields = [
            'config_id', 'config_name', 'version', 'is_active', 'is_default',
            'veo_api_settings', 'generation_settings', 'scheduling_settings',
            'learning_settings', 'cost_settings', 'quality_settings',
            'performance_settings', 'creation_time', 'last_updated',
            'created_by', 'metadata'
        ]
        
        for field in required_fields:
            assert hasattr(config, field), f"Missing required field: {field}"
            
    except ImportError:
        pytest.fail("AISystemConfig model not implemented yet")


def test_ai_system_config_category_enum():
    """Test that config category enum is properly defined"""
    try:
        from src.ai.models.ai_system_config import ConfigCategory
        
        # Test enum values exist
        expected_categories = ['veo_api', 'generation', 'scheduling', 'learning', 'cost', 'quality', 'performance', 'system']
        
        for category in expected_categories:
            assert hasattr(ConfigCategory, category.upper()), f"Missing config category: {category}"
            
    except ImportError:
        pytest.fail("ConfigCategory enum not implemented yet")


def test_ai_system_config_crud_operations():
    """Test basic CRUD operations for AISystemConfig"""
    try:
        from src.ai.models.ai_system_config import AISystemConfig, ConfigCategory
        
        # Test creation with required fields
        config_data = {
            'config_id': 'config_001',
            'config_name': 'Production Config',
            'version': '1.0.0',
            'veo_api_settings': {
                'api_key': 'test_key',
                'endpoint': 'https://api.veo.com',
                'timeout_seconds': 30,
                'max_retries': 3
            },
            'generation_settings': {
                'default_resolution': '1920x1080',
                'default_fps': 30,
                'max_duration_seconds': 120
            },
            'cost_settings': {
                'monthly_budget_usd': 100.0,
                'cost_per_generation': 0.50,
                'alert_threshold': 0.8
            }
        }
        
        config = AISystemConfig(**config_data)
        assert config.config_id == 'config_001'
        assert config.config_name == 'Production Config'
        assert config.version == '1.0.0'
        
        # Test settings access
        assert config.get_setting('veo_api_settings', 'timeout_seconds') == 30
        config.set_setting('veo_api_settings', 'timeout_seconds', 45)
        assert config.get_setting('veo_api_settings', 'timeout_seconds') == 45
        
    except ImportError:
        pytest.fail("AISystemConfig model not fully implemented")


def test_ai_system_config_validation():
    """Test data validation for AISystemConfig"""
    try:
        from src.ai.models.ai_system_config import AISystemConfig
        
        # Test version validation
        config = AISystemConfig(
            config_id='test_002',
            config_name='Test Config',
            version='invalid version',  # Should be normalized
            is_active=True
        )
        
        # Test version format
        assert config.version is not None
        
        # Test default settings creation
        assert config.veo_api_settings is not None
        assert config.generation_settings is not None
        assert config.cost_settings is not None
        
        # Test active/default validation
        assert isinstance(config.is_active, bool)
        assert isinstance(config.is_default, bool)
        
    except ImportError:
        pytest.fail("AISystemConfig validation not implemented")


def test_ai_system_config_settings_management():
    """Test settings management operations"""
    try:
        from src.ai.models.ai_system_config import AISystemConfig
        
        config = AISystemConfig(
            config_id='settings_test_001',
            config_name='Settings Test',
            version='1.0.0'
        )
        
        # Test VEO API settings
        config.configure_veo_api(
            api_key='new_key',
            endpoint='https://new-api.veo.com',
            timeout_seconds=60
        )
        assert config.get_setting('veo_api_settings', 'api_key') == 'new_key'
        assert config.get_setting('veo_api_settings', 'timeout_seconds') == 60
        
        # Test generation settings
        config.configure_generation(
            default_resolution='1280x720',
            default_fps=24,
            max_duration_seconds=60
        )
        assert config.get_setting('generation_settings', 'default_resolution') == '1280x720'
        
        # Test cost settings
        config.configure_cost_limits(
            monthly_budget_usd=200.0,
            cost_per_generation=0.75,
            alert_threshold=0.9
        )
        assert config.get_setting('cost_settings', 'monthly_budget_usd') == 200.0
        
    except ImportError:
        pytest.fail("AISystemConfig settings management not implemented")


def test_ai_system_config_validation_rules():
    """Test configuration validation rules"""
    try:
        from src.ai.models.ai_system_config import AISystemConfig
        
        config = AISystemConfig(
            config_id='validation_test_001',
            config_name='Validation Test',
            version='1.0.0'
        )
        
        # Test VEO API validation
        is_valid_veo = config.validate_veo_api_settings()
        assert isinstance(is_valid_veo, bool)
        
        # Test generation validation
        is_valid_gen = config.validate_generation_settings()
        assert isinstance(is_valid_gen, bool)
        
        # Test cost validation
        is_valid_cost = config.validate_cost_settings()
        assert isinstance(is_valid_cost, bool)
        
        # Test overall validation
        is_valid_overall = config.validate_all_settings()
        assert isinstance(is_valid_overall, bool)
        
        # Test validation errors
        validation_errors = config.get_validation_errors()
        assert isinstance(validation_errors, list)
        
    except ImportError:
        pytest.fail("AISystemConfig validation rules not implemented")


def test_ai_system_config_defaults_and_templates():
    """Test default configurations and templates"""
    try:
        from src.ai.models.ai_system_config import AISystemConfig
        
        # Test development template
        dev_config = AISystemConfig.create_development_config()
        assert dev_config.config_name == 'Development Config'
        assert dev_config.get_setting('cost_settings', 'monthly_budget_usd') <= 50.0
        
        # Test production template
        prod_config = AISystemConfig.create_production_config()
        assert prod_config.config_name == 'Production Config'
        assert prod_config.get_setting('veo_api_settings', 'max_retries') >= 3
        
        # Test testing template
        test_config = AISystemConfig.create_testing_config()
        assert test_config.config_name == 'Testing Config'
        assert test_config.get_setting('generation_settings', 'max_duration_seconds') <= 30
        
    except ImportError:
        pytest.fail("AISystemConfig templates not implemented")


def test_ai_system_config_import_export():
    """Test configuration import/export functionality"""
    try:
        from src.ai.models.ai_system_config import AISystemConfig
        import json
        
        # Create a config
        config = AISystemConfig(
            config_id='export_test_001',
            config_name='Export Test',
            version='2.0.0',
            veo_api_settings={'api_key': 'export_key'},
            generation_settings={'default_fps': 60},
            cost_settings={'monthly_budget_usd': 150.0}
        )
        
        # Test export
        exported_data = config.export_config()
        assert isinstance(exported_data, dict)
        assert exported_data['config_id'] == 'export_test_001'
        assert exported_data['version'] == '2.0.0'
        
        # Test import
        imported_config = AISystemConfig.import_config(exported_data)
        assert imported_config.config_id == 'export_test_001'
        assert imported_config.version == '2.0.0'
        assert imported_config.get_setting('cost_settings', 'monthly_budget_usd') == 150.0
        
    except ImportError:
        pytest.fail("AISystemConfig import/export not implemented")


def test_ai_system_config_json_serialization():
    """Test JSON serialization/deserialization"""
    try:
        from src.ai.models.ai_system_config import AISystemConfig
        import json
        
        config = AISystemConfig(
            config_id='serialize_test_001',
            config_name='Serialization Test',
            version='1.5.0',
            is_active=True,
            is_default=False,
            veo_api_settings={
                'api_key': 'serialize_key',
                'endpoint': 'https://serialize.veo.com',
                'timeout_seconds': 90
            },
            generation_settings={
                'default_resolution': '2560x1440',
                'default_fps': 120,
                'quality': 'ultra'
            },
            metadata={'environment': 'staging', 'owner': 'test_user'}
        )
        
        # Test to_dict method
        config_dict = config.to_dict()
        assert isinstance(config_dict, dict)
        assert config_dict['config_id'] == 'serialize_test_001'
        assert config_dict['config_name'] == 'Serialization Test'
        assert config_dict['version'] == '1.5.0'
        
        # Test JSON serialization
        json_str = json.dumps(config_dict)
        assert isinstance(json_str, str)
        
        # Test deserialization
        loaded_dict = json.loads(json_str)
        assert loaded_dict['config_id'] == 'serialize_test_001'
        
    except ImportError:
        pytest.fail("AISystemConfig serialization not implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])