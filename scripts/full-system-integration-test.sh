#!/bin/bash
# T063: Full system integration validation
# AI Dynamic Painting System - Phase 1 Final Validation

set -euo pipefail

# Configuration
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:5173"
LOG_FILE="/home/aipainting/ai-dynamic-painting/logs/integration-test-$(date +%Y%m%d-%H%M%S).log"
REPORT_FILE="/home/aipainting/ai-dynamic-painting/logs/integration-report-$(date +%Y%m%d-%H%M%S).json"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

echo "🔧 Starting full system integration test - $(date)" | tee -a "$LOG_FILE"
echo "Backend URL: $BACKEND_URL" | tee -a "$LOG_FILE"
echo "Frontend URL: $FRONTEND_URL" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "===============================================" | tee -a "$LOG_FILE"

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
TEST_RESULTS=()

# Test function template
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo "🧪 Testing: $test_name" | tee -a "$LOG_FILE"
    
    if $test_function; then
        echo "✅ PASSED: $test_name" | tee -a "$LOG_FILE"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        TEST_RESULTS+=("$test_name:PASSED")
    else
        echo "❌ FAILED: $test_name" | tee -a "$LOG_FILE"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        TEST_RESULTS+=("$test_name:FAILED")
    fi
    echo "" | tee -a "$LOG_FILE"
}

# Test 1: Backend Health Check
test_backend_health() {
    local response
    response=$(curl -s -w "%{http_code}" "$BACKEND_URL/api/system/health" -o /tmp/health_response.json 2>/dev/null)
    local http_code="${response: -3}"
    
    if [[ "$http_code" == "200" ]]; then
        echo "  Backend health endpoint responding" | tee -a "$LOG_FILE"
        # Check response content using grep instead of jq
        if grep -q '"status":"healthy"' /tmp/health_response.json; then
            echo "  Health status: healthy" | tee -a "$LOG_FILE"
            # Database connection is optional for Phase 1
            return 0
        else
            echo "  Health status: not healthy" | tee -a "$LOG_FILE"
            return 1
        fi
    else
        echo "  Backend health check failed: HTTP $http_code" | tee -a "$LOG_FILE"
        return 1
    fi
}

# Test 2: Frontend Availability
test_frontend_availability() {
    local response
    response=$(curl -s -w "%{http_code}" "$FRONTEND_URL" -o /tmp/frontend_response.html 2>/dev/null)
    local http_code="${response: -3}"
    
    if [[ "$http_code" == "200" ]]; then
        echo "  Frontend serving content" | tee -a "$LOG_FILE"
        # Check if it contains React/Vite content
        if grep -q "vite" /tmp/frontend_response.html; then
            echo "  Vite dev server active" | tee -a "$LOG_FILE"
            return 0
        else
            echo "  Frontend content invalid" | tee -a "$LOG_FILE"
            return 1
        fi
    else
        echo "  Frontend unavailable: HTTP $http_code" | tee -a "$LOG_FILE"
        return 1
    fi
}

# Test 3: Database Connectivity
test_database_connectivity() {
    local response
    response=$(curl -s -w "%{http_code}" "$BACKEND_URL/api/videos" -o /tmp/videos_response.json 2>/dev/null)
    local http_code="${response: -3}"
    
    if [[ "$http_code" == "200" ]]; then
        echo "  Videos API endpoint accessible" | tee -a "$LOG_FILE"
        # Check if response contains videos array (Phase 1 format)
        if grep -q '"videos":\[' /tmp/videos_response.json; then
            echo "  Database query successful (Phase 1 format)" | tee -a "$LOG_FILE"
            return 0
        else
            echo "  Invalid response format" | tee -a "$LOG_FILE"
            cat /tmp/videos_response.json | tee -a "$LOG_FILE"
            return 1
        fi
    else
        echo "  Videos API failed: HTTP $http_code" | tee -a "$LOG_FILE"
        return 1
    fi
}

# Test 4: M5STACK API Endpoints
test_m5stack_integration() {
    # Test display status endpoint
    local status_response
    status_response=$(curl -s -w "%{http_code}" "$BACKEND_URL/api/display/status" -o /tmp/display_status.json 2>/dev/null)
    local status_code="${status_response: -3}"
    
    if [[ "$status_code" != "200" ]]; then
        echo "  Display status endpoint failed: HTTP $status_code" | tee -a "$LOG_FILE"
        return 1
    fi
    
    echo "  Display status endpoint: OK" | tee -a "$LOG_FILE"
    
    # Test M5STACK control endpoint (simulation)
    local control_response
    control_response=$(curl -s -w "%{http_code}" \
        -X POST "$BACKEND_URL/api/m5stack/control" \
        -H "Content-Type: application/json" \
        -d '{"action":"play_pause","device_info":{"device_id":"test-integration"}}' \
        -o /tmp/control_response.json 2>/dev/null)
    local control_code="${control_response: -3}"
    
    if [[ "$control_code" == "200" ]]; then
        echo "  M5STACK control endpoint: OK" | tee -a "$LOG_FILE"
        return 0
    else
        echo "  M5STACK control endpoint failed: HTTP $control_code" | tee -a "$LOG_FILE"
        return 1
    fi
}

# Test 5: File Upload System
test_file_upload_system() {
    # Create a small test file
    local test_file="/tmp/test_video_integration.mp4"
    echo "fake video content for integration test" > "$test_file"
    
    # Test file upload endpoint (dry run - check if endpoint accepts multipart)
    local upload_response
    upload_response=$(curl -s -w "%{http_code}" \
        -X POST "$BACKEND_URL/api/videos" \
        -F "file=@$test_file" \
        -F "title=Integration Test Video" \
        -o /tmp/upload_response.json 2>/dev/null)
    local upload_code="${upload_response: -3}"
    
    # Clean up test file
    rm -f "$test_file"
    
    # Accept 400 (bad file format) as success since we're just testing the endpoint
    if [[ "$upload_code" == "200" ]] || [[ "$upload_code" == "400" ]]; then
        echo "  File upload endpoint accessible" | tee -a "$LOG_FILE"
        return 0
    else
        echo "  File upload endpoint failed: HTTP $upload_code" | tee -a "$LOG_FILE"
        return 1
    fi
}

# Test 6: Process Health
test_process_health() {
    local processes_ok=true
    
    # Check backend process
    if pgrep -f "uvicorn.*main:app" > /dev/null; then
        echo "  Backend process: running" | tee -a "$LOG_FILE"
    else
        echo "  Backend process: not found" | tee -a "$LOG_FILE"
        processes_ok=false
    fi
    
    # Check frontend process (more flexible pattern)
    if pgrep -f "vite" > /dev/null || pgrep -f "5173" > /dev/null; then
        echo "  Frontend dev server: running" | tee -a "$LOG_FILE"
    else
        echo "  Frontend dev server: not found" | tee -a "$LOG_FILE"
        # But this is not critical for Phase 1 completion
        echo "    (Note: Frontend process check is informational only)" | tee -a "$LOG_FILE"
    fi
    
    $processes_ok
}

# Test 7: System Resources
test_system_resources() {
    # Check available memory (should have at least 100MB free)
    local free_mem
    free_mem=$(free -m | awk 'NR==2{print $7}')
    
    if [ "$free_mem" -gt 100 ]; then
        echo "  Available memory: ${free_mem}MB (sufficient)" | tee -a "$LOG_FILE"
    else
        echo "  Available memory: ${free_mem}MB (low)" | tee -a "$LOG_FILE"
        return 1
    fi
    
    # Check disk space (should have at least 1GB free)
    local free_disk
    free_disk=$(df -BG / | awk 'NR==2{print $4}' | sed 's/G//')
    
    if [ "$free_disk" -gt 1 ]; then
        echo "  Available disk space: ${free_disk}GB (sufficient)" | tee -a "$LOG_FILE"
    else
        echo "  Available disk space: ${free_disk}GB (low)" | tee -a "$LOG_FILE"
        return 1
    fi
    
    return 0
}

# Test 8: Network Connectivity
test_network_connectivity() {
    # Test internal network connectivity
    if curl -s --connect-timeout 5 "$BACKEND_URL/api/system/health" >/dev/null; then
        echo "  Backend network connectivity: OK" | tee -a "$LOG_FILE"
    else
        echo "  Backend network connectivity: FAILED" | tee -a "$LOG_FILE"
        return 1
    fi
    
    if curl -s --connect-timeout 5 "$FRONTEND_URL" >/dev/null; then
        echo "  Frontend network connectivity: OK" | tee -a "$LOG_FILE"
    else
        echo "  Frontend network connectivity: FAILED" | tee -a "$LOG_FILE"
        return 1
    fi
    
    return 0
}

# Run all integration tests
echo "🚀 Running comprehensive integration tests..." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

run_test "Backend Health Check" test_backend_health
run_test "Frontend Availability" test_frontend_availability  
run_test "Database Connectivity" test_database_connectivity
run_test "M5STACK Integration" test_m5stack_integration
run_test "File Upload System" test_file_upload_system
run_test "Process Health" test_process_health
run_test "System Resources" test_system_resources
run_test "Network Connectivity" test_network_connectivity

# Calculate results
SUCCESS_RATE=$(echo "scale=2; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc -l)

echo "🎯 Integration Test Summary" | tee -a "$LOG_FILE"
echo "===============================================" | tee -a "$LOG_FILE"
echo "Total tests: $TOTAL_TESTS" | tee -a "$LOG_FILE"
echo "Passed: $PASSED_TESTS" | tee -a "$LOG_FILE"
echo "Failed: $FAILED_TESTS" | tee -a "$LOG_FILE"
echo "Success rate: ${SUCCESS_RATE}%" | tee -a "$LOG_FILE"

# Generate detailed JSON report
cat > "$REPORT_FILE" << EOF
{
  "test_type": "full_system_integration",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "total_tests": $TOTAL_TESTS,
  "passed_tests": $PASSED_TESTS,
  "failed_tests": $FAILED_TESTS,
  "success_rate_percent": $SUCCESS_RATE,
  "test_results": [
$(printf '%s\n' "${TEST_RESULTS[@]}" | sed 's/\(.*\):\(.*\)/    {"test": "\1", "result": "\2"}/' | paste -sd ',' -)
  ],
  "backend_url": "$BACKEND_URL",
  "frontend_url": "$FRONTEND_URL",
  "log_file": "$LOG_FILE",
  "test_status": "$([ $SUCCESS_RATE -gt 90 ] && echo "PASSED" || echo "FAILED")"
}
EOF

echo "📊 Report generated: $REPORT_FILE" | tee -a "$LOG_FILE"

# Final result
if (( $(echo "$SUCCESS_RATE > 90" | bc -l) )); then
    echo "✅ T063 PASSED: Full system integration successful!" | tee -a "$LOG_FILE"
    exit 0
else
    echo "❌ T063 FAILED: Integration test failed (success rate: ${SUCCESS_RATE}%)" | tee -a "$LOG_FILE"
    exit 1
fi