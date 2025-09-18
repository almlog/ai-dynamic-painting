"""
Contract test for PromptTemplate model
Test File: backend/tests/contract/test_prompt_template.py

This test MUST FAIL initially (RED phase of TDD)
"""

import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

def test_prompt_template_model_exists():
    """Test that PromptTemplate model exists and has required fields"""
    # This should initially FAIL until we implement the model
    try:
        from src.ai.models.prompt_template import PromptTemplate
        
        # Test model can be instantiated
        template = PromptTemplate()
        assert template is not None
        
        # Test required fields exist
        required_fields = [
            'template_id', 'name', 'prompt_text', 'category', 'variables',
            'description', 'creation_time', 'usage_count', 'effectiveness_score',
            'is_active', 'creator_user_id', 'last_updated', 'tags'
        ]
        
        for field in required_fields:
            assert hasattr(template, field), f"Missing required field: {field}"
            
    except ImportError:
        pytest.fail("PromptTemplate model not implemented yet")


def test_prompt_template_category_enum():
    """Test that prompt category enum is properly defined"""
    try:
        from src.ai.models.prompt_template import PromptCategory
        
        # Test enum values exist
        expected_categories = ['scenic', 'artistic', 'weather', 'seasonal', 'mood', 'abstract', 'custom']
        
        for category in expected_categories:
            assert hasattr(PromptCategory, category.upper()), f"Missing category: {category}"
            
    except ImportError:
        pytest.fail("PromptCategory enum not implemented yet")


def test_prompt_template_crud_operations():
    """Test basic CRUD operations for PromptTemplate"""
    try:
        from src.ai.models.prompt_template import PromptTemplate, PromptCategory
        
        # Test creation with required fields
        template_data = {
            'template_id': 'tpl_001',
            'name': 'Sunset Template',
            'prompt_text': 'Beautiful sunset over {location} with {mood} lighting',
            'category': PromptCategory.SCENIC,
            'variables': ['location', 'mood'],
            'description': 'Template for generating sunset scenes',
            'effectiveness_score': 0.85
        }
        
        template = PromptTemplate(**template_data)
        assert template.template_id == 'tpl_001'
        assert template.name == 'Sunset Template'
        assert template.category == PromptCategory.SCENIC
        assert template.effectiveness_score == 0.85
        
        # Test variable substitution
        rendered = template.render_prompt({'location': 'mountains', 'mood': 'warm'})
        assert 'mountains' in rendered
        assert 'warm' in rendered
        
    except ImportError:
        pytest.fail("PromptTemplate model not fully implemented")


def test_prompt_template_validation():
    """Test data validation for PromptTemplate"""
    try:
        from src.ai.models.prompt_template import PromptTemplate, PromptCategory
        
        # Test prompt text validation
        template = PromptTemplate(
            template_id='test_002',
            name='Test Template',
            prompt_text='',  # Empty prompt should be handled
            category=PromptCategory.CUSTOM,
            variables=[]
        )
        
        # Should have valid prompt text
        assert template.prompt_text is not None
        
        # Test effectiveness score validation (0.0 to 1.0)
        template.effectiveness_score = 0.5
        assert 0.0 <= template.effectiveness_score <= 1.0
        
        # Test usage count validation
        template.usage_count = 10
        assert template.usage_count >= 0
        
    except ImportError:
        pytest.fail("PromptTemplate validation not implemented")


def test_prompt_template_variable_handling():
    """Test variable extraction and substitution"""
    try:
        from src.ai.models.prompt_template import PromptTemplate, PromptCategory
        
        template = PromptTemplate(
            template_id='var_test_001',
            name='Variable Test',
            prompt_text='A {style} painting of {subject} in {environment} during {time_of_day}',
            category=PromptCategory.ARTISTIC,
            variables=['style', 'subject', 'environment', 'time_of_day'],
            description='Template for testing variable substitution'
        )
        
        # Test variable extraction
        extracted_vars = template.extract_variables()
        expected_vars = ['style', 'subject', 'environment', 'time_of_day']
        assert set(extracted_vars) == set(expected_vars)
        
        # Test prompt rendering
        values = {
            'style': 'impressionist',
            'subject': 'flowers',
            'environment': 'garden',
            'time_of_day': 'sunset'
        }
        rendered = template.render_prompt(values)
        assert 'impressionist' in rendered
        assert 'flowers' in rendered
        assert 'garden' in rendered
        assert 'sunset' in rendered
        assert '{' not in rendered  # No unresolved variables
        
    except ImportError:
        pytest.fail("PromptTemplate variable handling not implemented")


def test_prompt_template_effectiveness_tracking():
    """Test effectiveness scoring and usage tracking"""
    try:
        from src.ai.models.prompt_template import PromptTemplate, PromptCategory
        
        template = PromptTemplate(
            template_id='track_test_001',
            name='Tracking Test',
            prompt_text='Tracking template for {subject}',
            category=PromptCategory.CUSTOM,
            variables=['subject'],
            usage_count=0,
            effectiveness_score=0.0
        )
        
        # Test usage increment
        initial_count = template.usage_count
        template.increment_usage()
        assert template.usage_count == initial_count + 1
        
        # Test effectiveness update
        template.update_effectiveness(0.92)
        assert template.effectiveness_score == 0.92
        
        # Test popularity calculation
        template.usage_count = 100
        popularity = template.calculate_popularity()
        assert isinstance(popularity, float)
        assert popularity >= 0.0
        
    except ImportError:
        pytest.fail("PromptTemplate effectiveness tracking not implemented")


def test_prompt_template_json_serialization():
    """Test JSON serialization/deserialization"""
    try:
        from src.ai.models.prompt_template import PromptTemplate, PromptCategory
        import json
        
        template = PromptTemplate(
            template_id='serialize_test_001',
            name='Serialization Test',
            prompt_text='Test template for {item} serialization',
            category=PromptCategory.CUSTOM,
            variables=['item'],
            description='Testing JSON serialization',
            effectiveness_score=0.88,
            usage_count=50,
            tags=['test', 'serialization']
        )
        
        # Test to_dict method
        template_dict = template.to_dict()
        assert isinstance(template_dict, dict)
        assert template_dict['template_id'] == 'serialize_test_001'
        assert template_dict['name'] == 'Serialization Test'
        assert template_dict['effectiveness_score'] == 0.88
        
        # Test JSON serialization
        json_str = json.dumps(template_dict)
        assert isinstance(json_str, str)
        
        # Test deserialization
        loaded_dict = json.loads(json_str)
        assert loaded_dict['template_id'] == 'serialize_test_001'
        
    except ImportError:
        pytest.fail("PromptTemplate serialization not implemented")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])