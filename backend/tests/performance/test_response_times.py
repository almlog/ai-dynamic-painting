"""
Performance tests - T059
Phase 1 手動動画管理システム - パフォーマンステスト (<3s Web UI, <1s M5STACK)
"""

import pytest
import time
import statistics
import concurrent.futures
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


class TestPerformanceRequirements:
    """Performance requirement validation tests"""

    def test_web_ui_response_time_under_3s(self, client):
        """Test Web UI API responses are under 3 seconds"""
        web_ui_endpoints = [
            "/api/videos",
            "/api/system/health", 
            "/api/display/status"
        ]
        
        response_times = []
        
        for endpoint in web_ui_endpoints:
            # Test each endpoint multiple times
            for _ in range(10):
                start_time = time.time()
                response = client.get(endpoint)
                elapsed_time = time.time() - start_time
                
                response_times.append(elapsed_time)
                
                # Individual request must be under 3 seconds
                assert elapsed_time < 3.0, \
                    f"Web UI endpoint {endpoint} took {elapsed_time:.3f}s (>3s limit)"
                assert response.status_code == 200
        
        # Average response time should be well under limit
        avg_response_time = statistics.mean(response_times)
        assert avg_response_time < 1.0, \
            f"Average Web UI response time {avg_response_time:.3f}s too high"

    def test_m5stack_response_time_under_1s(self, client):
        """Test M5STACK API responses are under 1 second"""
        m5stack_endpoints = [
            ("/api/m5stack/control", "POST", {"action": "ping", "device_id": "test"}),
            ("/api/m5stack/sensors", "GET", None)
        ]
        
        response_times = []
        
        for endpoint, method, data in m5stack_endpoints:
            # Test each endpoint multiple times
            for _ in range(15):
                start_time = time.time()
                
                if method == "GET":
                    response = client.get(endpoint)
                else:
                    response = client.post(endpoint, json=data)
                
                elapsed_time = time.time() - start_time
                response_times.append(elapsed_time)
                
                # M5STACK operations must be under 1 second
                assert elapsed_time < 1.0, \
                    f"M5STACK endpoint {endpoint} took {elapsed_time:.3f}s (>1s limit)"
                assert response.status_code in [200, 400, 503]  # Allow expected errors

        # Average M5STACK response time should be well under limit
        avg_response_time = statistics.mean(response_times)
        assert avg_response_time < 0.5, \
            f"Average M5STACK response time {avg_response_time:.3f}s too high"

    def test_concurrent_web_ui_performance(self, client):
        """Test Web UI performance under concurrent load"""
        def make_web_request():
            start_time = time.time()
            response = client.get("/api/videos")
            elapsed_time = time.time() - start_time
            return elapsed_time, response.status_code
        
        # 10 concurrent Web UI requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_web_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # All concurrent requests should meet performance requirements
        for elapsed_time, status_code in results:
            assert elapsed_time < 3.0, f"Concurrent Web UI request took {elapsed_time:.3f}s"
            assert status_code == 200

    def test_concurrent_m5stack_performance(self, client):
        """Test M5STACK performance under concurrent load"""
        def make_m5stack_request(device_id):
            start_time = time.time()
            response = client.post("/api/m5stack/control", json={
                "action": "ping",
                "device_id": f"device_{device_id}"
            })
            elapsed_time = time.time() - start_time
            return elapsed_time, response.status_code
        
        # 5 concurrent M5STACK requests (realistic IoT load)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_m5stack_request, i) for i in range(5)]
            results = [future.result() for future in futures]
        
        # All M5STACK requests should meet strict timing requirements
        for elapsed_time, status_code in results:
            assert elapsed_time < 1.0, f"Concurrent M5STACK request took {elapsed_time:.3f}s"
            assert status_code in [200, 400]

    def test_database_query_performance(self, client):
        """Test database query performance"""
        database_heavy_endpoints = [
            "/api/videos",  # Video list query
            "/api/system/health",  # System status query
        ]
        
        for endpoint in database_heavy_endpoints:
            query_times = []
            
            for _ in range(20):  # 20 database queries
                start_time = time.time()
                response = client.get(endpoint)
                elapsed_time = time.time() - start_time
                
                query_times.append(elapsed_time)
                assert response.status_code == 200
            
            # Database queries should be fast
            avg_query_time = statistics.mean(query_times)
            max_query_time = max(query_times)
            
            assert avg_query_time < 0.1, \
                f"Average database query time {avg_query_time:.3f}s too slow"
            assert max_query_time < 0.5, \
                f"Slowest database query {max_query_time:.3f}s too slow"

    def test_file_upload_performance(self, client):
        """Test file upload performance for large files"""
        # Simulate large file upload (5MB)
        large_file_data = b"0" * (5 * 1024 * 1024)  # 5MB of zeros
        
        files = {
            "file": ("large_video.mp4", large_file_data, "video/mp4")
        }
        
        start_time = time.time()
        response = client.post("/api/videos/upload", files=files)
        upload_time = time.time() - start_time
        
        # Large file uploads should complete within reasonable time (30s for 5MB)
        assert upload_time < 30.0, f"File upload took {upload_time:.3f}s (too slow)"
        
        # Calculate upload speed (MB/s)
        upload_speed = 5.0 / upload_time  # 5MB / time
        assert upload_speed > 0.5, f"Upload speed {upload_speed:.2f} MB/s too slow"

    def test_memory_usage_during_load(self, client):
        """Test memory usage under load doesn't grow excessively"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Generate load with many requests
        for i in range(200):
            response = client.get("/api/system/health")
            assert response.status_code == 200
            
            # Check memory every 50 requests
            if i % 50 == 0:
                current_memory = process.memory_info().rss
                memory_increase = current_memory - initial_memory
                
                # Memory increase should be reasonable (<100MB)
                assert memory_increase < 100 * 1024 * 1024, \
                    f"Memory increased by {memory_increase / 1024 / 1024:.1f}MB"

    def test_cpu_usage_under_load(self, client):
        """Test CPU usage remains reasonable under load"""
        import psutil
        
        # Monitor CPU during load test
        cpu_readings = []
        
        def monitor_cpu():
            for _ in range(10):  # 10 readings over 5 seconds
                cpu_readings.append(psutil.cpu_percent(interval=0.5))
        
        import threading
        cpu_monitor = threading.Thread(target=monitor_cpu)
        cpu_monitor.start()
        
        # Generate CPU load with requests
        for _ in range(100):
            client.get("/api/system/health")
            client.get("/api/videos")
        
        cpu_monitor.join()
        
        # CPU usage shouldn't spike excessively
        avg_cpu = statistics.mean(cpu_readings)
        max_cpu = max(cpu_readings)
        
        assert avg_cpu < 80.0, f"Average CPU usage {avg_cpu:.1f}% too high"
        assert max_cpu < 95.0, f"Peak CPU usage {max_cpu:.1f}% too high"

    def test_api_throughput(self, client):
        """Test API request throughput"""
        request_count = 100
        start_time = time.time()
        
        successful_requests = 0
        for _ in range(request_count):
            response = client.get("/api/system/health")
            if response.status_code == 200:
                successful_requests += 1
        
        total_time = time.time() - start_time
        throughput = successful_requests / total_time
        
        # Should handle at least 50 requests per second
        assert throughput >= 50.0, \
            f"API throughput {throughput:.1f} req/s too low (minimum 50 req/s)"

    def test_response_time_consistency(self, client):
        """Test response time consistency (low variance)"""
        response_times = []
        
        for _ in range(50):
            start_time = time.time()
            response = client.get("/api/display/status")
            elapsed_time = time.time() - start_time
            
            response_times.append(elapsed_time)
            assert response.status_code == 200
        
        # Check response time consistency
        avg_time = statistics.mean(response_times)
        std_dev = statistics.stdev(response_times)
        
        # Standard deviation should be small (consistent performance)
        coefficient_of_variation = std_dev / avg_time
        assert coefficient_of_variation < 0.5, \
            f"Response time inconsistent (CV: {coefficient_of_variation:.3f})"

    def test_error_rate_under_load(self, client):
        """Test error rate remains low under sustained load"""
        total_requests = 500
        errors = 0
        
        for _ in range(total_requests):
            response = client.get("/api/system/health")
            if response.status_code != 200:
                errors += 1
        
        error_rate = errors / total_requests
        
        # Error rate should be very low (<1%)
        assert error_rate < 0.01, f"Error rate {error_rate:.3%} too high under load"

    def test_display_control_latency(self, client):
        """Test display control operations have low latency"""
        display_operations = [
            ("POST", "/api/display/play", {"video_id": "test-video"}),
            ("POST", "/api/display/pause", None),
            ("POST", "/api/display/resume", None),
            ("POST", "/api/display/stop", None)
        ]
        
        for method, endpoint, data in display_operations:
            latencies = []
            
            for _ in range(10):
                start_time = time.time()
                
                if method == "GET":
                    response = client.get(endpoint)
                else:
                    response = client.post(endpoint, json=data)
                
                latency = time.time() - start_time
                latencies.append(latency)
                
                # Allow expected errors for some operations
                assert response.status_code in [200, 400, 404]
            
            # Display control should be very responsive
            avg_latency = statistics.mean(latencies)
            max_latency = max(latencies)
            
            assert avg_latency < 0.1, \
                f"Display control {endpoint} avg latency {avg_latency:.3f}s too high"
            assert max_latency < 0.5, \
                f"Display control {endpoint} max latency {max_latency:.3f}s too high"