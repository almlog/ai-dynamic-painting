#!/bin/bash
# T061: 24-hour stability test with real hardware
# AI Dynamic Painting System - Phase 1 Final Validation

set -euo pipefail

# Configuration
BACKEND_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:5173"
TEST_DURATION_HOURS=24
LOG_FILE="/home/aipainting/ai-dynamic-painting/logs/stability-test-$(date +%Y%m%d-%H%M%S).log"
REPORT_FILE="/home/aipainting/ai-dynamic-painting/logs/stability-report-$(date +%Y%m%d-%H%M%S).json"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

echo "🚀 Starting 24-hour stability test - $(date)" | tee -a "$LOG_FILE"
echo "Test duration: $TEST_DURATION_HOURS hours" | tee -a "$LOG_FILE"
echo "Backend URL: $BACKEND_URL" | tee -a "$LOG_FILE"
echo "Frontend URL: $FRONTEND_URL" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "===============================================" | tee -a "$LOG_FILE"

# Initialize counters
TOTAL_REQUESTS=0
SUCCESSFUL_REQUESTS=0
FAILED_REQUESTS=0
START_TIME=$(date +%s)
END_TIME=$((START_TIME + TEST_DURATION_HOURS * 3600))

# Test functions
test_backend_health() {
    local response
    if response=$(curl -s -w "%{http_code}" "$BACKEND_URL/api/system/health" -o /tmp/health_response.json 2>/dev/null); then
        local http_code="${response: -3}"
        if [[ "$http_code" == "200" ]]; then
            return 0
        else
            echo "Backend health check failed: HTTP $http_code" | tee -a "$LOG_FILE"
            return 1
        fi
    else
        echo "Backend health check failed: Connection error" | tee -a "$LOG_FILE"
        return 1
    fi
}

test_frontend_availability() {
    local response
    if response=$(curl -s -w "%{http_code}" "$FRONTEND_URL" -o /dev/null 2>/dev/null); then
        local http_code="${response: -3}"
        if [[ "$http_code" == "200" ]]; then
            return 0
        else
            echo "Frontend availability check failed: HTTP $http_code" | tee -a "$LOG_FILE"
            return 1
        fi
    else
        echo "Frontend availability check failed: Connection error" | tee -a "$LOG_FILE"
        return 1
    fi
}

test_m5stack_api() {
    local response
    if response=$(curl -s -w "%{http_code}" "$BACKEND_URL/api/display/status" -o /tmp/m5stack_response.json 2>/dev/null); then
        local http_code="${response: -3}"
        if [[ "$http_code" == "200" ]]; then
            return 0
        else
            echo "M5STACK API check failed: HTTP $http_code" | tee -a "$LOG_FILE"
            return 1
        fi
    else
        echo "M5STACK API check failed: Connection error" | tee -a "$LOG_FILE"
        return 1
    fi
}

collect_system_metrics() {
    # CPU usage
    local cpu_usage
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    
    # Memory usage
    local memory_info
    memory_info=$(free -m | awk 'NR==2{printf "%.2f", $3*100/$2}')
    
    # Disk usage
    local disk_usage
    disk_usage=$(df -h / | awk 'NR==2{print $5}' | cut -d'%' -f1)
    
    # Network connections
    local network_connections
    network_connections=$(netstat -tn 2>/dev/null | grep :8000 | wc -l)
    
    echo "$(date): CPU: ${cpu_usage}%, Memory: ${memory_info}%, Disk: ${disk_usage}%, Connections: ${network_connections}" | tee -a "$LOG_FILE"
}

check_process_health() {
    # Check if backend process is running
    if ! pgrep -f "uvicorn.*main:app" > /dev/null; then
        echo "❌ Backend process not running!" | tee -a "$LOG_FILE"
        return 1
    fi
    
    # Check if frontend dev server is running
    if ! pgrep -f "vite.*5173" > /dev/null; then
        echo "❌ Frontend dev server not running!" | tee -a "$LOG_FILE"
        return 1
    fi
    
    return 0
}

# Main test loop
echo "Starting stability test loop..." | tee -a "$LOG_FILE"

while [ $(date +%s) -lt $END_TIME ]; do
    CURRENT_TIME=$(date +%s)
    ELAPSED_HOURS=$(( (CURRENT_TIME - START_TIME) / 3600 ))
    ELAPSED_MINUTES=$(( ((CURRENT_TIME - START_TIME) % 3600) / 60 ))
    
    echo "⏰ Test running: ${ELAPSED_HOURS}h ${ELAPSED_MINUTES}m" | tee -a "$LOG_FILE"
    
    # Test all components
    TOTAL_REQUESTS=$((TOTAL_REQUESTS + 3))
    
    # Backend health
    if test_backend_health; then
        echo "✅ Backend health: OK" | tee -a "$LOG_FILE"
        SUCCESSFUL_REQUESTS=$((SUCCESSFUL_REQUESTS + 1))
    else
        echo "❌ Backend health: FAILED" | tee -a "$LOG_FILE"
        FAILED_REQUESTS=$((FAILED_REQUESTS + 1))
    fi
    
    # Frontend availability
    if test_frontend_availability; then
        echo "✅ Frontend: OK" | tee -a "$LOG_FILE"
        SUCCESSFUL_REQUESTS=$((SUCCESSFUL_REQUESTS + 1))
    else
        echo "❌ Frontend: FAILED" | tee -a "$LOG_FILE"
        FAILED_REQUESTS=$((FAILED_REQUESTS + 1))
    fi
    
    # M5STACK API
    if test_m5stack_api; then
        echo "✅ M5STACK API: OK" | tee -a "$LOG_FILE"
        SUCCESSFUL_REQUESTS=$((SUCCESSFUL_REQUESTS + 1))
    else
        echo "❌ M5STACK API: FAILED" | tee -a "$LOG_FILE"
        FAILED_REQUESTS=$((FAILED_REQUESTS + 1))
    fi
    
    # System metrics
    collect_system_metrics
    
    # Process health
    if ! check_process_health; then
        echo "❌ Process health check failed!" | tee -a "$LOG_FILE"
        FAILED_REQUESTS=$((FAILED_REQUESTS + 1))
    fi
    
    # Sleep for 5 minutes before next check
    echo "💤 Waiting 5 minutes for next check..." | tee -a "$LOG_FILE"
    echo "---" | tee -a "$LOG_FILE"
    
    sleep 300
done

# Generate final report
FINAL_TIME=$(date +%s)
ACTUAL_DURATION=$((FINAL_TIME - START_TIME))
SUCCESS_RATE=$(echo "scale=2; $SUCCESSFUL_REQUESTS * 100 / $TOTAL_REQUESTS" | bc -l)

echo "🎉 24-hour stability test completed!" | tee -a "$LOG_FILE"
echo "===============================================" | tee -a "$LOG_FILE"
echo "Test duration: $((ACTUAL_DURATION / 3600))h $((ACTUAL_DURATION % 3600 / 60))m" | tee -a "$LOG_FILE"
echo "Total requests: $TOTAL_REQUESTS" | tee -a "$LOG_FILE"
echo "Successful requests: $SUCCESSFUL_REQUESTS" | tee -a "$LOG_FILE"
echo "Failed requests: $FAILED_REQUESTS" | tee -a "$LOG_FILE"
echo "Success rate: ${SUCCESS_RATE}%" | tee -a "$LOG_FILE"

# Generate JSON report
cat > "$REPORT_FILE" << EOF
{
  "test_type": "24hour_stability_test",
  "start_time": "$START_TIME",
  "end_time": "$FINAL_TIME",
  "duration_seconds": $ACTUAL_DURATION,
  "duration_hours": $(echo "scale=2; $ACTUAL_DURATION / 3600" | bc -l),
  "total_requests": $TOTAL_REQUESTS,
  "successful_requests": $SUCCESSFUL_REQUESTS,
  "failed_requests": $FAILED_REQUESTS,
  "success_rate_percent": $SUCCESS_RATE,
  "backend_url": "$BACKEND_URL",
  "frontend_url": "$FRONTEND_URL",
  "log_file": "$LOG_FILE",
  "test_status": "$([ $SUCCESS_RATE -gt 95 ] && echo "PASSED" || echo "FAILED")"
}
EOF

echo "📊 Report generated: $REPORT_FILE" | tee -a "$LOG_FILE"

# Check if test passed (>95% success rate)
if (( $(echo "$SUCCESS_RATE > 95" | bc -l) )); then
    echo "✅ T061 PASSED: 24-hour stability test successful!" | tee -a "$LOG_FILE"
    exit 0
else
    echo "❌ T061 FAILED: Stability test failed (success rate: ${SUCCESS_RATE}%)" | tee -a "$LOG_FILE"
    exit 1
fi