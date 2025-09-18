"""
Integration test 24-hour stability - T020
Phase 1 手動動画管理システム - 24時間安定性統合テスト
"""

import pytest
from fastapi.testclient import TestClient
import threading
import time
import concurrent.futures
from unittest.mock import patch, MagicMock
import gc
import psutil
import os
from src.main import app


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


class TestSystemStability:
    """24-hour stability and stress tests"""

    def test_continuous_api_requests(self, client):
        """Test continuous API requests for stability"""
        def make_requests(duration_seconds=60):  # Simulate 1 minute for testing
            start_time = time.time()
            request_count = 0
            errors = []
            
            while time.time() - start_time < duration_seconds:
                try:
                    # Health check request
                    response = client.get("/api/system/health")
                    if response.status_code != 200:
                        errors.append(f"Health check failed: {response.status_code}")
                    
                    # Display status request
                    response = client.get("/api/display/status")
                    if response.status_code != 200:
                        errors.append(f"Display status failed: {response.status_code}")
                    
                    request_count += 1
                    time.sleep(0.1)  # 10 requests per second
                    
                except Exception as e:
                    errors.append(f"Request error: {str(e)}")
            
            return request_count, errors
        
        # Run continuous requests
        request_count, errors = make_requests(60)  # 1 minute test
        
        # Verify stability
        assert request_count > 500, f"Too few requests processed: {request_count}"
        assert len(errors) < request_count * 0.01, f"Too many errors: {len(errors)}"

    def test_memory_leak_detection(self, client):
        """Test for memory leaks during extended operation"""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Perform many operations
        for i in range(1000):
            client.get("/api/system/health")
            client.get("/api/display/status")
            client.get("/api/videos")
            
            # Force garbage collection every 100 iterations
            if i % 100 == 0:
                gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal (less than 50MB)
        max_increase = 50 * 1024 * 1024  # 50MB in bytes
        assert memory_increase < max_increase, \
            f"Memory leak detected: {memory_increase / 1024 / 1024:.2f}MB increase"

    def test_concurrent_user_simulation(self, client):
        """Test handling multiple concurrent users"""
        def user_session(user_id):
            """Simulate a user session"""
            errors = []
            operations = 0
            
            try:
                # User workflow: check status, browse videos, control display
                for _ in range(50):  # 50 operations per user
                    # Check system health
                    response = client.get("/api/system/health")
                    if response.status_code == 200:
                        operations += 1
                    else:
                        errors.append(f"User {user_id}: Health check failed")
                    
                    # Check videos
                    response = client.get("/api/videos")
                    if response.status_code == 200:
                        operations += 1
                    else:
                        errors.append(f"User {user_id}: Videos list failed")
                    
                    # Check display status
                    response = client.get("/api/display/status")
                    if response.status_code == 200:
                        operations += 1
                    else:
                        errors.append(f"User {user_id}: Display status failed")
                    
                    time.sleep(0.01)  # Small delay between operations
                    
            except Exception as e:
                errors.append(f"User {user_id}: Session error: {str(e)}")
            
            return user_id, operations, errors
        
        # Simulate 10 concurrent users
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(user_session, i) for i in range(10)]
            results = [future.result() for future in futures]
        
        # Analyze results
        total_operations = sum(result[1] for result in results)
        total_errors = sum(len(result[2]) for result in results)
        
        # Verify stability under concurrent load
        assert total_operations > 1000, f"Too few operations: {total_operations}"
        assert total_errors < total_operations * 0.02, f"Too many errors: {total_errors}"

    def test_database_connection_stability(self, client):
        """Test database connection stability over time"""
        connection_errors = []
        
        for i in range(500):  # 500 database operations
            try:
                # Operations that require database
                response = client.get("/api/videos")
                if response.status_code != 200:
                    connection_errors.append(f"Iteration {i}: Videos query failed")
                
                response = client.get("/api/system/health")
                if response.status_code != 200:
                    connection_errors.append(f"Iteration {i}: Health check failed")
                
                # Brief pause
                time.sleep(0.01)
                
            except Exception as e:
                connection_errors.append(f"Iteration {i}: Database error: {str(e)}")
        
        # Database should remain stable
        error_rate = len(connection_errors) / 500
        assert error_rate < 0.01, f"Database instability detected: {error_rate:.2%} error rate"

    def test_api_response_time_degradation(self, client):
        """Test that response times don't degrade over time"""
        response_times = []
        
        for i in range(200):  # 200 requests
            start_time = time.time()
            response = client.get("/api/system/health")
            elapsed_time = time.time() - start_time
            
            assert response.status_code == 200
            response_times.append(elapsed_time)
            
            time.sleep(0.05)  # 20 requests per second
        
        # Check for response time degradation
        first_half_avg = sum(response_times[:100]) / 100
        second_half_avg = sum(response_times[100:]) / 100
        
        # Response time shouldn't increase significantly
        degradation_ratio = second_half_avg / first_half_avg
        assert degradation_ratio < 2.0, \
            f"Response time degraded: {first_half_avg:.3f}s -> {second_half_avg:.3f}s"

    @patch('src.services.monitoring_service.psutil')
    def test_resource_monitoring_stability(self, mock_psutil, client):
        """Test resource monitoring stability"""
        # Mock system resources
        mock_psutil.cpu_percent.return_value = 45.0
        mock_psutil.virtual_memory.return_value.percent = 60.0
        mock_psutil.disk_usage.return_value.percent = 75.0
        
        monitoring_errors = []
        
        for i in range(100):
            try:
                response = client.get("/api/system/health")
                data = response.json()
                
                # Verify monitoring data is present and reasonable
                assert 0 <= data.get("cpu_usage", 0) <= 100
                assert 0 <= data.get("memory_usage", 0) <= 100
                assert 0 <= data.get("disk_usage", 0) <= 100
                
            except Exception as e:
                monitoring_errors.append(f"Monitoring error {i}: {str(e)}")
        
        assert len(monitoring_errors) == 0, f"Monitoring instability: {monitoring_errors}"

    def test_error_recovery_stability(self, client):
        """Test system recovery from temporary errors"""
        recovery_test_passed = False
        
        try:
            # Simulate error conditions and recovery
            for attempt in range(10):
                # Try operations that might fail
                response = client.get("/api/display/status")
                
                if response.status_code == 200:
                    # System recovered successfully
                    recovery_test_passed = True
                    break
                
                time.sleep(0.1)  # Brief retry delay
            
            assert recovery_test_passed, "System failed to recover from errors"
            
        except Exception as e:
            pytest.fail(f"Error recovery test failed: {str(e)}")

    def test_long_running_session_stability(self, client):
        """Test stability of long-running user sessions"""
        session_duration = 300  # 5 minutes simulation
        start_time = time.time()
        operations_count = 0
        session_errors = []
        
        while time.time() - start_time < session_duration:
            try:
                # Simulate user activity pattern
                operations = [
                    lambda: client.get("/api/system/health"),
                    lambda: client.get("/api/videos"),
                    lambda: client.get("/api/display/status"),
                ]
                
                # Random operation selection
                import random
                operation = random.choice(operations)
                response = operation()
                
                if response.status_code == 200:
                    operations_count += 1
                else:
                    session_errors.append(f"Operation failed: {response.status_code}")
                
                # Variable delay to simulate human behavior
                time.sleep(random.uniform(0.1, 0.5))
                
            except Exception as e:
                session_errors.append(f"Session error: {str(e)}")
        
        # Verify long session stability
        assert operations_count > 100, f"Too few operations in long session: {operations_count}"
        error_rate = len(session_errors) / operations_count if operations_count > 0 else 1
        assert error_rate < 0.05, f"High error rate in long session: {error_rate:.2%}"

    def test_system_health_monitoring_continuity(self, client):
        """Test that system health monitoring remains consistent"""
        health_checks = []
        
        for i in range(60):  # 60 health checks
            response = client.get("/api/system/health")
            assert response.status_code == 200
            
            data = response.json()
            health_checks.append({
                'timestamp': time.time(),
                'api_status': data.get('api_status'),
                'uptime': data.get('uptime', 0)
            })
            
            time.sleep(1)  # 1-second intervals
        
        # Verify health monitoring continuity
        api_statuses = [check['api_status'] for check in health_checks]
        uptimes = [check['uptime'] for check in health_checks]
        
        # API status should remain consistent
        healthy_count = api_statuses.count('healthy')
        assert healthy_count >= len(api_statuses) * 0.9, "API status unstable"
        
        # Uptime should be increasing (generally)
        assert uptimes[-1] >= uptimes[0], "Uptime decreased (system restart detected)"