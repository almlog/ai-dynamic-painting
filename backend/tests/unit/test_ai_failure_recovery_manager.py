"""
Unit tests for AI Failure Recovery Manager - T270 AI unit tests comprehensive coverage
Tests the failure recovery and resilience system for AI services
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ai.services.failure_recovery_manager import (
    FailureRecoveryManager,
    FailureType,
    RecoveryStrategy,
    FailureEvent,
    RecoveryResult,
    CircuitBreakerState,
    RetryPolicy,
    FailureSeverity
)


class TestFailureRecoveryManager:
    """Test cases for FailureRecoveryManager"""
    
    @pytest.fixture
    def recovery_manager(self):
        """Create FailureRecoveryManager instance for testing"""
        config = {
            "max_retry_attempts": 3,
            "base_retry_delay": 1.0,
            "circuit_breaker_threshold": 5,
            "circuit_breaker_timeout": 60,
            "fallback_enabled": True
        }
        return FailureRecoveryManager(config)
    
    @pytest.fixture
    def sample_failure_event(self):
        """Sample failure event for testing"""
        return FailureEvent(
            failure_id="test_failure_001",
            failure_type=FailureType.API_TIMEOUT,
            component="veo_api_service",
            severity=FailureSeverity.MEDIUM,
            error_message="Request timeout after 30 seconds",
            context={
                "request_id": "req_123",
                "endpoint": "/generate_video",
                "timeout_duration": 30
            },
            timestamp=datetime.now()
        )
    
    def test_manager_initialization(self, recovery_manager):
        """Test FailureRecoveryManager initialization"""
        assert recovery_manager is not None
        assert recovery_manager.config["max_retry_attempts"] == 3
        assert recovery_manager.circuit_breakers == {}
        assert recovery_manager.failure_history == []
        
    def test_failure_event_recording(self, recovery_manager, sample_failure_event):
        """Test recording failure events"""
        result = recovery_manager.record_failure(sample_failure_event)
        
        assert result["status"] == "recorded"
        assert result["failure_id"] == sample_failure_event.failure_id
        assert len(recovery_manager.failure_history) == 1
        
    def test_automatic_retry_strategy(self, recovery_manager, sample_failure_event):
        """Test automatic retry recovery strategy"""
        # Mock the failed operation
        mock_operation = Mock()
        mock_operation.side_effect = [Exception("First failure"), Exception("Second failure"), "Success"]
        
        recovery_result = recovery_manager.attempt_recovery(
            sample_failure_event,
            recovery_strategy=RecoveryStrategy.RETRY,
            operation=mock_operation
        )
        
        assert recovery_result.success is True
        assert recovery_result.attempts_made == 3
        assert recovery_result.final_result == "Success"
        assert mock_operation.call_count == 3
        
    def test_exponential_backoff_retry(self, recovery_manager):
        """Test exponential backoff retry mechanism"""
        retry_policy = RetryPolicy(
            max_attempts=4,
            base_delay=0.1,
            backoff_multiplier=2.0,
            max_delay=1.0
        )
        
        delays = recovery_manager.calculate_retry_delays(retry_policy)
        
        assert len(delays) == 4
        assert delays[0] == 0.1
        assert delays[1] == 0.2
        assert delays[2] == 0.4
        assert delays[3] == 0.8  # Would be 0.8, not exceeding max_delay of 1.0
        
    def test_circuit_breaker_functionality(self, recovery_manager):
        """Test circuit breaker pattern implementation"""
        component = "test_service"
        
        # Initial state should be CLOSED
        assert recovery_manager.get_circuit_breaker_state(component) == CircuitBreakerState.CLOSED
        
        # Simulate multiple failures to trip circuit breaker
        for i in range(6):  # Threshold is 5
            failure = FailureEvent(
                failure_id=f"failure_{i}",
                failure_type=FailureType.API_ERROR,
                component=component,
                severity=FailureSeverity.HIGH,
                error_message=f"API error {i}",
                timestamp=datetime.now()
            )
            recovery_manager.record_failure(failure)
            
        # Circuit breaker should now be OPEN
        assert recovery_manager.get_circuit_breaker_state(component) == CircuitBreakerState.OPEN
        
        # Verify that operations are blocked
        assert recovery_manager.is_circuit_breaker_open(component) is True
        
    def test_circuit_breaker_half_open_state(self, recovery_manager):
        """Test circuit breaker half-open state and recovery"""
        component = "test_service"
        
        # Trip the circuit breaker
        for i in range(6):
            failure = FailureEvent(
                failure_id=f"failure_{i}",
                failure_type=FailureType.API_ERROR,
                component=component,
                severity=FailureSeverity.HIGH,
                error_message="API error",
                timestamp=datetime.now()
            )
            recovery_manager.record_failure(failure)
            
        # Simulate timeout passing
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime.now() + timedelta(seconds=61)
            
            # Circuit breaker should transition to HALF_OPEN
            recovery_manager.update_circuit_breaker_state(component)
            assert recovery_manager.get_circuit_breaker_state(component) == CircuitBreakerState.HALF_OPEN
            
    def test_fallback_strategy(self, recovery_manager, sample_failure_event):
        """Test fallback recovery strategy"""
        # Mock primary and fallback operations
        primary_operation = Mock(side_effect=Exception("Primary failed"))
        fallback_operation = Mock(return_value="Fallback success")
        
        recovery_result = recovery_manager.attempt_recovery(
            sample_failure_event,
            recovery_strategy=RecoveryStrategy.FALLBACK,
            operation=primary_operation,
            fallback_operation=fallback_operation
        )
        
        assert recovery_result.success is True
        assert recovery_result.final_result == "Fallback success"
        assert recovery_result.strategy_used == RecoveryStrategy.FALLBACK
        
    def test_graceful_degradation(self, recovery_manager):
        """Test graceful degradation strategy"""
        # Simulate system under stress
        stress_context = {
            "cpu_usage": 90,
            "memory_usage": 85,
            "active_requests": 50
        }
        
        degradation_plan = recovery_manager.plan_graceful_degradation(stress_context)
        
        assert "reduced_features" in degradation_plan
        assert "performance_limits" in degradation_plan
        assert "resource_allocation" in degradation_plan
        
        # Apply degradation
        result = recovery_manager.apply_graceful_degradation(degradation_plan)
        assert result["status"] == "applied"
        
    @pytest.mark.asyncio
    async def test_async_recovery_operations(self, recovery_manager, sample_failure_event):
        """Test asynchronous recovery operations"""
        # Mock async operation
        async def mock_async_operation():
            await asyncio.sleep(0.1)
            return "Async success"
            
        async def failing_async_operation():
            await asyncio.sleep(0.05)
            raise Exception("Async failure")
            
        # Test successful async recovery
        recovery_result = await recovery_manager.attempt_async_recovery(
            sample_failure_event,
            recovery_strategy=RecoveryStrategy.RETRY,
            async_operation=mock_async_operation
        )
        
        assert recovery_result.success is True
        assert recovery_result.final_result == "Async success"
        
    def test_failure_pattern_analysis(self, recovery_manager):
        """Test failure pattern analysis and detection"""
        # Create pattern of failures
        failures = []
        for i in range(10):
            failure = FailureEvent(
                failure_id=f"pattern_failure_{i}",
                failure_type=FailureType.API_TIMEOUT if i % 2 == 0 else FailureType.API_ERROR,
                component="api_service",
                severity=FailureSeverity.MEDIUM,
                error_message=f"Pattern failure {i}",
                timestamp=datetime.now() - timedelta(minutes=i),
                context={"hour": (datetime.now() - timedelta(minutes=i)).hour}
            )
            failures.append(failure)
            recovery_manager.record_failure(failure)
            
        patterns = recovery_manager.analyze_failure_patterns()
        
        assert "frequent_failure_types" in patterns
        assert "failure_frequency" in patterns
        assert "component_reliability" in patterns
        assert patterns["total_failures"] == 10
        
    def test_recovery_strategy_selection(self, recovery_manager):
        """Test automatic recovery strategy selection"""
        # Test different failure scenarios
        timeout_failure = FailureEvent(
            failure_id="timeout_001",
            failure_type=FailureType.API_TIMEOUT,
            component="api_service",
            severity=FailureSeverity.MEDIUM,
            error_message="Timeout error"
        )
        
        rate_limit_failure = FailureEvent(
            failure_id="rate_limit_001", 
            failure_type=FailureType.RATE_LIMIT,
            component="api_service",
            severity=FailureSeverity.LOW,
            error_message="Rate limit exceeded"
        )
        
        # Different failure types should suggest different strategies
        timeout_strategy = recovery_manager.select_recovery_strategy(timeout_failure)
        rate_limit_strategy = recovery_manager.select_recovery_strategy(rate_limit_failure)
        
        assert timeout_strategy in [RecoveryStrategy.RETRY, RecoveryStrategy.FALLBACK]
        assert rate_limit_strategy in [RecoveryStrategy.BACKOFF, RecoveryStrategy.CIRCUIT_BREAKER]
        
    def test_recovery_success_tracking(self, recovery_manager):
        """Test tracking recovery success rates"""
        # Simulate successful recoveries
        for i in range(8):
            failure = FailureEvent(
                failure_id=f"success_failure_{i}",
                failure_type=FailureType.API_ERROR,
                component="test_service",
                severity=FailureSeverity.MEDIUM,
                error_message="Test error"
            )
            
            recovery_result = RecoveryResult(
                recovery_id=f"recovery_{i}",
                failure_event=failure,
                strategy_used=RecoveryStrategy.RETRY,
                success=i < 6,  # 6 out of 8 successful
                attempts_made=1,
                recovery_time=timedelta(seconds=2)
            )
            
            recovery_manager.record_recovery_result(recovery_result)
            
        success_rate = recovery_manager.get_recovery_success_rate("test_service")
        assert success_rate == 0.75  # 6/8 = 75%
        
        overall_success_rate = recovery_manager.get_overall_recovery_success_rate()
        assert overall_success_rate == 0.75
        
    def test_component_health_monitoring(self, recovery_manager):
        """Test component health monitoring"""
        component = "health_test_service"
        
        # Record various failures and successes
        for i in range(10):
            if i < 7:  # 7 successes
                recovery_manager.record_component_success(component)
            else:  # 3 failures
                failure = FailureEvent(
                    failure_id=f"health_failure_{i}",
                    failure_type=FailureType.API_ERROR,
                    component=component,
                    severity=FailureSeverity.MEDIUM,
                    error_message="Health test error"
                )
                recovery_manager.record_failure(failure)
                
        health_status = recovery_manager.get_component_health(component)
        
        assert "success_rate" in health_status
        assert "failure_rate" in health_status
        assert "last_failure" in health_status
        assert "health_score" in health_status
        assert health_status["success_rate"] == 0.7
        
    def test_recovery_escalation(self, recovery_manager):
        """Test recovery escalation when simple strategies fail"""
        failure = FailureEvent(
            failure_id="escalation_test",
            failure_type=FailureType.SYSTEM_ERROR,
            component="critical_service",
            severity=FailureSeverity.CRITICAL,
            error_message="Critical system error"
        )
        
        # Mock failing operations for all strategies
        failing_operation = Mock(side_effect=Exception("Always fails"))
        
        # Attempt recovery with escalation
        recovery_result = recovery_manager.attempt_recovery_with_escalation(
            failure,
            operation=failing_operation,
            escalation_levels=[
                RecoveryStrategy.RETRY,
                RecoveryStrategy.FALLBACK,
                RecoveryStrategy.CIRCUIT_BREAKER
            ]
        )
        
        assert recovery_result.escalation_level > 0
        assert recovery_result.strategies_attempted > 1
        
    def test_failure_notification_system(self, recovery_manager, sample_failure_event):
        """Test failure notification and alerting"""
        # Mock notification handlers
        email_handler = Mock()
        slack_handler = Mock()
        
        recovery_manager.add_notification_handler("email", email_handler)
        recovery_manager.add_notification_handler("slack", slack_handler)
        
        # Record critical failure
        critical_failure = FailureEvent(
            failure_id="critical_001",
            failure_type=FailureType.SYSTEM_ERROR,
            component="critical_service",
            severity=FailureSeverity.CRITICAL,
            error_message="Critical system failure"
        )
        
        recovery_manager.record_failure(critical_failure)
        
        # Verify notifications were sent
        email_handler.assert_called_once()
        slack_handler.assert_called_once()
        
    def test_recovery_metrics_collection(self, recovery_manager):
        """Test collection of recovery-related metrics"""
        # Simulate various recovery scenarios
        scenarios = [
            (RecoveryStrategy.RETRY, True, 2),
            (RecoveryStrategy.FALLBACK, True, 1),
            (RecoveryStrategy.RETRY, False, 3),
            (RecoveryStrategy.CIRCUIT_BREAKER, True, 1)
        ]
        
        for strategy, success, attempts in scenarios:
            failure = FailureEvent(
                failure_id=f"metrics_failure_{strategy}_{success}",
                failure_type=FailureType.API_ERROR,
                component="metrics_test_service",
                severity=FailureSeverity.MEDIUM,
                error_message="Metrics test error"
            )
            
            result = RecoveryResult(
                recovery_id=f"recovery_{strategy}_{success}",
                failure_event=failure,
                strategy_used=strategy,
                success=success,
                attempts_made=attempts,
                recovery_time=timedelta(seconds=attempts * 2)
            )
            
            recovery_manager.record_recovery_result(result)
            
        metrics = recovery_manager.get_recovery_metrics()
        
        assert "total_recoveries" in metrics
        assert "success_rate_by_strategy" in metrics
        assert "average_attempts_by_strategy" in metrics
        assert "average_recovery_time" in metrics
        
    def test_configuration_validation(self):
        """Test configuration validation"""
        # Valid configuration
        valid_config = {
            "max_retry_attempts": 3,
            "base_retry_delay": 1.0,
            "circuit_breaker_threshold": 5
        }
        
        manager = FailureRecoveryManager(valid_config)
        assert manager.config["max_retry_attempts"] == 3
        
        # Invalid configuration
        with pytest.raises(ValueError):
            invalid_config = {
                "max_retry_attempts": -1,  # Invalid negative value
                "base_retry_delay": 0,     # Invalid zero delay
            }
            FailureRecoveryManager(invalid_config)
            
    def test_recovery_state_persistence(self, recovery_manager):
        """Test persistence of recovery state"""
        # Record some failures and recoveries
        failure = FailureEvent(
            failure_id="persistence_test",
            failure_type=FailureType.API_ERROR,
            component="persistence_service",
            severity=FailureSeverity.MEDIUM,
            error_message="Persistence test error"
        )
        
        recovery_manager.record_failure(failure)
        
        # Export state
        state = recovery_manager.export_state()
        
        assert "failure_history" in state
        assert "circuit_breakers" in state
        assert "recovery_metrics" in state
        
        # Create new manager and import state
        new_manager = FailureRecoveryManager({})
        new_manager.import_state(state)
        
        assert len(new_manager.failure_history) == len(recovery_manager.failure_history)
        
    def test_custom_recovery_strategies(self, recovery_manager):
        """Test custom recovery strategy registration"""
        # Define custom recovery strategy
        def custom_strategy(failure_event, operation, **kwargs):
            """Custom recovery strategy for testing"""
            try:
                result = operation()
                return RecoveryResult(
                    recovery_id="custom_recovery",
                    failure_event=failure_event,
                    strategy_used="CUSTOM",
                    success=True,
                    final_result=result
                )
            except Exception as e:
                return RecoveryResult(
                    recovery_id="custom_recovery",
                    failure_event=failure_event,
                    strategy_used="CUSTOM",
                    success=False,
                    error_message=str(e)
                )
                
        # Register custom strategy
        recovery_manager.register_custom_strategy("CUSTOM", custom_strategy)
        
        # Test custom strategy
        mock_operation = Mock(return_value="Custom success")
        failure = FailureEvent(
            failure_id="custom_test",
            failure_type=FailureType.API_ERROR,
            component="custom_service",
            severity=FailureSeverity.MEDIUM,
            error_message="Custom test error"
        )
        
        result = recovery_manager.attempt_recovery(
            failure,
            recovery_strategy="CUSTOM",
            operation=mock_operation
        )
        
        assert result.success is True
        assert result.strategy_used == "CUSTOM"
        assert result.final_result == "Custom success"


class TestFailureEventDataStructures:
    """Test failure event data structures"""
    
    def test_failure_event_creation(self):
        """Test FailureEvent creation and validation"""
        event = FailureEvent(
            failure_id="test_001",
            failure_type=FailureType.API_TIMEOUT,
            component="test_service",
            severity=FailureSeverity.HIGH,
            error_message="Test timeout error",
            context={"timeout": 30, "retries": 2},
            timestamp=datetime.now()
        )
        
        assert event.failure_id == "test_001"
        assert event.failure_type == FailureType.API_TIMEOUT
        assert event.severity == FailureSeverity.HIGH
        assert event.context["timeout"] == 30
        
    def test_recovery_result_creation(self):
        """Test RecoveryResult creation"""
        failure = FailureEvent(
            failure_id="recovery_test",
            failure_type=FailureType.API_ERROR,
            component="test_service",
            severity=FailureSeverity.MEDIUM,
            error_message="Test error"
        )
        
        result = RecoveryResult(
            recovery_id="recovery_001",
            failure_event=failure,
            strategy_used=RecoveryStrategy.RETRY,
            success=True,
            attempts_made=2,
            recovery_time=timedelta(seconds=5),
            final_result="Recovery successful"
        )
        
        assert result.recovery_id == "recovery_001"
        assert result.success is True
        assert result.attempts_made == 2
        assert result.strategy_used == RecoveryStrategy.RETRY
        
    def test_retry_policy_validation(self):
        """Test RetryPolicy validation"""
        # Valid policy
        policy = RetryPolicy(
            max_attempts=5,
            base_delay=1.0,
            backoff_multiplier=2.0,
            max_delay=60.0
        )
        
        assert policy.is_valid()
        
        # Invalid policy
        invalid_policy = RetryPolicy(
            max_attempts=0,  # Invalid
            base_delay=-1.0,  # Invalid
            backoff_multiplier=0.5  # Should be >= 1.0
        )
        
        assert not invalid_policy.is_valid()


class TestFailureRecoveryIntegration:
    """Integration tests for failure recovery system"""
    
    @pytest.fixture
    def integrated_manager(self):
        """Create manager with realistic configuration"""
        config = {
            "max_retry_attempts": 3,
            "base_retry_delay": 0.1,  # Fast for testing
            "backoff_multiplier": 2.0,
            "circuit_breaker_threshold": 3,
            "circuit_breaker_timeout": 1,  # Short for testing
            "fallback_enabled": True,
            "notification_enabled": True
        }
        return FailureRecoveryManager(config)
        
    @pytest.mark.asyncio
    async def test_end_to_end_recovery_flow(self, integrated_manager):
        """Test complete end-to-end recovery flow"""
        component = "e2e_test_service"
        
        # Mock a flaky operation that fails twice then succeeds
        call_count = 0
        async def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception(f"Failure attempt {call_count}")
            return f"Success after {call_count} attempts"
            
        # Create failure event
        failure = FailureEvent(
            failure_id="e2e_test",
            failure_type=FailureType.API_ERROR,
            component=component,
            severity=FailureSeverity.MEDIUM,
            error_message="E2E test error"
        )
        
        # Attempt recovery
        result = await integrated_manager.attempt_async_recovery(
            failure,
            recovery_strategy=RecoveryStrategy.RETRY,
            async_operation=flaky_operation
        )
        
        assert result.success is True
        assert result.attempts_made == 3
        assert "Success after 3 attempts" in result.final_result
        
        # Verify metrics were recorded
        metrics = integrated_manager.get_recovery_metrics()
        assert metrics["total_recoveries"] >= 1
        
    def test_multi_component_failure_handling(self, integrated_manager):
        """Test handling failures across multiple components"""
        components = ["service_a", "service_b", "service_c"]
        
        # Generate failures for each component
        for i, component in enumerate(components):
            for j in range(i + 1):  # Different failure counts per component
                failure = FailureEvent(
                    failure_id=f"{component}_failure_{j}",
                    failure_type=FailureType.API_ERROR,
                    component=component,
                    severity=FailureSeverity.MEDIUM,
                    error_message=f"Error in {component}"
                )
                integrated_manager.record_failure(failure)
                
        # Analyze patterns across components
        patterns = integrated_manager.analyze_failure_patterns()
        
        assert patterns["total_failures"] == 6  # 1 + 2 + 3
        assert len(patterns["component_reliability"]) == 3
        assert "service_c" in patterns["component_reliability"]  # Most failures
        
    def test_system_resilience_under_load(self, integrated_manager):
        """Test system resilience under high failure load"""
        # Simulate high failure rate
        for i in range(50):
            failure = FailureEvent(
                failure_id=f"load_test_failure_{i}",
                failure_type=FailureType.API_TIMEOUT,
                component="load_test_service",
                severity=FailureSeverity.MEDIUM,
                error_message=f"Load test failure {i}"
            )
            integrated_manager.record_failure(failure)
            
        # System should still be responsive
        health = integrated_manager.get_component_health("load_test_service")
        assert health is not None
        assert "failure_rate" in health
        
        # Circuit breaker should be triggered
        assert integrated_manager.is_circuit_breaker_open("load_test_service")
        
        # System should suggest appropriate actions
        recommendations = integrated_manager.get_recovery_recommendations("load_test_service")
        assert len(recommendations) > 0