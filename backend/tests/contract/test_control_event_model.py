"""
Contract test for ControlEvent model
T029: This test MUST FAIL initially (TDD Red phase)
"""
import pytest
from datetime import datetime
from uuid import uuid4

# Import existing ControlEvent model and EventType
from src.models.control_event import ControlEvent, EventType


class TestControlEventModelContract:
    """Contract tests for ControlEvent model functionality"""
    
    def setup_method(self):
        """Setup test data"""
        self.valid_event_data = {
            "id": str(uuid4()),
            "session_id": str(uuid4()),
            "device_id": str(uuid4()),
            "event_type": "play",
            "event_data": {"video_id": "test-123", "position": 0.0},
            "timestamp": datetime.now(),
            "success": True,
            "error_message": None
        }
    
    def test_control_event_model_creation(self):
        """
        ControlEvent should be created with all required fields
        """
        event = ControlEvent(**self.valid_event_data)
        
        # Contract: ControlEvent should be created successfully
        assert event is not None
        assert event.id == self.valid_event_data["id"]
        assert event.session_id == self.valid_event_data["session_id"]
        assert event.device_id == self.valid_event_data["device_id"]
        assert event.event_type == "play"
        assert event.event_data == {"video_id": "test-123", "position": 0.0}
        assert event.success == True
        assert event.error_message is None
    
    def test_event_type_validation(self):
        """
        EventType should have proper literal values
        """
        # Contract: EventType is Literal with specific values
        # Test by creating events with valid types
        valid_types = ["play", "pause", "stop", "next", "previous", "volume", "upload"]
        
        for event_type in valid_types:
            event_data = self.valid_event_data.copy()
            event_data["event_type"] = event_type
            event = ControlEvent(**event_data)
            assert event.event_type == event_type
        
        # Contract: Should reject invalid event types
        with pytest.raises((ValueError, TypeError)):
            invalid_data = self.valid_event_data.copy()
            invalid_data["event_type"] = "invalid_type"
            ControlEvent(**invalid_data)
    
    def test_event_data_json_handling(self):
        """
        ControlEvent should handle event_data as JSON/dict
        """
        # Contract: Should accept complex event data
        complex_event_data = {
            "video_id": "test-456",
            "position": 123.45,
            "volume": 0.8,
            "quality": "720p",
            "metadata": {
                "user_action": True,
                "retry_count": 0
            }
        }
        
        event_data = self.valid_event_data.copy()
        event_data["event_data"] = complex_event_data
        event = ControlEvent(**event_data)
        
        assert event.event_data == complex_event_data
        assert event.event_data["video_id"] == "test-456"
        assert event.event_data["position"] == 123.45
        assert event.event_data["metadata"]["user_action"] == True
    
    def test_session_id_optional(self):
        """
        ControlEvent should handle optional session_id
        """
        # Contract: session_id should be optional for some event types
        event_data = self.valid_event_data.copy()
        event_data["session_id"] = None
        event_data["event_type"] = "upload"  # Upload events may not have session
        
        event = ControlEvent(**event_data)
        assert event.session_id is None
        assert event.event_type == "upload"
    
    def test_success_and_error_handling(self):
        """
        ControlEvent should handle success/error states
        """
        # Contract: Should handle successful events
        success_event_data = self.valid_event_data.copy()
        success_event_data["success"] = True
        success_event_data["error_message"] = None
        
        success_event = ControlEvent(**success_event_data)
        assert success_event.success == True
        assert success_event.error_message is None
        
        # Contract: Should handle failed events with error messages
        error_event_data = self.valid_event_data.copy()
        error_event_data["success"] = False
        error_event_data["error_message"] = "Video file not found"
        
        error_event = ControlEvent(**error_event_data)
        assert error_event.success == False
        assert error_event.error_message == "Video file not found"
    
    def test_datetime_field_handling(self):
        """
        ControlEvent should handle timestamp field properly
        """
        now = datetime.now()
        event_data = self.valid_event_data.copy()
        event_data["timestamp"] = now
        
        event = ControlEvent(**event_data)
        
        # Contract: Should store datetime properly
        assert event.timestamp == now
        assert isinstance(event.timestamp, datetime)
    
    def test_control_event_required_fields(self):
        """
        ControlEvent should require essential fields
        """
        required_fields = ["device_id", "event_type", "timestamp"]
        
        for field in required_fields:
            # Contract: Should fail when required field is missing
            incomplete_data = self.valid_event_data.copy()
            del incomplete_data[field]
            
            with pytest.raises((ValueError, TypeError, KeyError)):
                ControlEvent(**incomplete_data)
    
    def test_control_event_optional_fields(self):
        """
        ControlEvent should handle optional fields with defaults
        """
        minimal_data = {
            "device_id": str(uuid4()),
            "event_type": "play",
            "timestamp": datetime.now()
        }
        
        event = ControlEvent(**minimal_data)
        
        # Contract: Should provide defaults for optional fields
        assert event.session_id is None  # Optional
        assert event.event_data is not None  # Default empty dict
        assert event.success == True  # Default
        assert event.error_message is None  # Default
    
    def test_control_event_to_dict_method(self):
        """
        ControlEvent should have to_dict() method for serialization
        """
        event = ControlEvent(**self.valid_event_data)
        
        # Contract: Should have to_dict method
        assert hasattr(event, 'to_dict')
        
        # Contract: to_dict should return dictionary
        event_dict = event.to_dict()
        assert isinstance(event_dict, dict)
        
        # Contract: Should contain all fields
        expected_fields = ["id", "session_id", "device_id", "event_type", 
                          "event_data", "timestamp", "success", "error_message"]
        for field in expected_fields:
            assert field in event_dict
    
    def test_control_event_from_dict_method(self):
        """
        ControlEvent should have from_dict() class method for deserialization
        """
        # Contract: Should have from_dict class method
        assert hasattr(ControlEvent, 'from_dict')
        
        event_dict = {
            "id": str(uuid4()),
            "session_id": str(uuid4()),
            "device_id": str(uuid4()),
            "event_type": "pause",
            "event_data": {"position": 67.5},
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "error_message": None
        }
        
        # Contract: Should create ControlEvent from dictionary
        event = ControlEvent.from_dict(event_dict)
        
        assert event.id == event_dict["id"]
        assert event.session_id == event_dict["session_id"]
        assert event.device_id == event_dict["device_id"]
        assert event.event_type == "pause"
        assert event.event_data == {"position": 67.5}
        assert event.success == True
        assert event.error_message is None
    
    def test_control_event_update_timestamp_method(self):
        """
        ControlEvent should have update_timestamp() method
        """
        event = ControlEvent(**self.valid_event_data)
        original_time = event.timestamp
        
        # Contract: Should have update_timestamp method
        assert hasattr(event, 'update_timestamp')
        
        # Wait a moment and update
        import time
        time.sleep(0.01)
        event.update_timestamp()
        
        # Contract: Should update to current time
        assert event.timestamp > original_time
    
    def test_control_event_mark_as_failed_method(self):
        """
        ControlEvent should have mark_as_failed() method
        """
        event = ControlEvent(**self.valid_event_data)
        
        # Contract: Should have mark_as_failed method
        assert hasattr(event, 'mark_as_failed')
        
        error_message = "Operation failed due to network error"
        event.mark_as_failed(error_message)
        
        # Contract: Should mark event as failed
        assert event.success == False
        assert event.error_message == error_message
    
    def test_control_event_mark_as_successful_method(self):
        """
        ControlEvent should have mark_as_successful() method
        """
        # Start with failed event
        event_data = self.valid_event_data.copy()
        event_data["success"] = False
        event_data["error_message"] = "Initial error"
        event = ControlEvent(**event_data)
        
        # Contract: Should have mark_as_successful method
        assert hasattr(event, 'mark_as_successful')
        
        event.mark_as_successful()
        
        # Contract: Should mark event as successful
        assert event.success == True
        assert event.error_message is None
    
    def test_control_event_add_data_method(self):
        """
        ControlEvent should have add_data() method to update event_data
        """
        event = ControlEvent(**self.valid_event_data)
        
        # Contract: Should have add_data method
        assert hasattr(event, 'add_data')
        
        additional_data = {"new_field": "new_value", "count": 42}
        event.add_data(additional_data)
        
        # Contract: Should merge data with existing event_data
        assert event.event_data["video_id"] == "test-123"  # Original data preserved
        assert event.event_data["new_field"] == "new_value"  # New data added
        assert event.event_data["count"] == 42
    
    def test_event_type_specific_validation(self):
        """
        ControlEvent should validate event types match expected data
        """
        # Contract: Play events should have video-related data
        play_event = ControlEvent(
            device_id=str(uuid4()),
            event_type="play",
            event_data={"video_id": "test-789"},
            timestamp=datetime.now()
        )
        assert play_event.event_type == "play"
        assert "video_id" in play_event.event_data
        
        # Contract: Volume events should have volume data
        volume_event = ControlEvent(
            device_id=str(uuid4()),
            event_type="volume",
            event_data={"volume": 0.7},
            timestamp=datetime.now()
        )
        assert volume_event.event_type == "volume"
        assert "volume" in volume_event.event_data
        
        # Contract: Upload events should work without session
        upload_event = ControlEvent(
            device_id=str(uuid4()),
            event_type="upload",
            session_id=None,
            event_data={"filename": "test.mp4", "size": 1024000},
            timestamp=datetime.now()
        )
        assert upload_event.event_type == "upload"
        assert upload_event.session_id is None
        assert "filename" in upload_event.event_data
    
    def test_control_event_validation_edge_cases(self):
        """
        ControlEvent should handle edge cases properly
        """
        # Contract: Should handle empty event_data
        event_data = self.valid_event_data.copy()
        event_data["event_data"] = {}
        event = ControlEvent(**event_data)
        assert event.event_data == {}
        
        # Contract: Should handle None values appropriately
        with pytest.raises((ValueError, TypeError)):
            invalid_data = self.valid_event_data.copy()
            invalid_data["device_id"] = None
            ControlEvent(**invalid_data)
        
        # Contract: Should handle very long error messages
        event_data = self.valid_event_data.copy()
        long_error = "x" * 1000
        event_data["error_message"] = long_error
        event = ControlEvent(**event_data)
        assert event.error_message == long_error