#!/bin/bash
# T062: Memory leak detection on Raspberry Pi
# AI Dynamic Painting System - Phase 1 Final Validation

set -euo pipefail

# Configuration
MONITOR_DURATION_HOURS=1  # Start with 1 hour, can extend to 24
LOG_FILE="/home/aipainting/ai-dynamic-painting/logs/memory-monitor-$(date +%Y%m%d-%H%M%S).log"
REPORT_FILE="/home/aipainting/ai-dynamic-painting/logs/memory-report-$(date +%Y%m%d-%H%M%S).json"
INTERVAL_SECONDS=60  # Check every minute

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

echo "🧠 Starting memory leak detection - $(date)" | tee -a "$LOG_FILE"
echo "Monitor duration: $MONITOR_DURATION_HOURS hours" | tee -a "$LOG_FILE"
echo "Check interval: $INTERVAL_SECONDS seconds" | tee -a "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo "===============================================" | tee -a "$LOG_FILE"

# Initialize tracking
START_TIME=$(date +%s)
END_TIME=$((START_TIME + MONITOR_DURATION_HOURS * 3600))
MEMORY_SAMPLES=()
CPU_SAMPLES=()
PROCESS_MEMORY_SAMPLES=()

# Function to get memory info
get_memory_info() {
    # System memory (MB)
    local mem_total mem_used mem_free mem_available
    read -r mem_total mem_used mem_free mem_available < <(free -m | awk 'NR==2{print $2, $3, $4, $7}')
    
    # Process-specific memory for backend
    local backend_memory=0
    if backend_pid=$(pgrep -f "uvicorn.*main:app"); then
        backend_memory=$(ps -p "$backend_pid" -o rss= 2>/dev/null | awk '{print $1/1024}' || echo "0")
    fi
    
    # Process-specific memory for frontend
    local frontend_memory=0
    if frontend_pid=$(pgrep -f "vite.*5173"); then
        frontend_memory=$(ps -p "$frontend_pid" -o rss= 2>/dev/null | awk '{print $1/1024}' || echo "0")
    fi
    
    echo "$mem_total,$mem_used,$mem_free,$mem_available,$backend_memory,$frontend_memory"
}

# Function to get CPU info
get_cpu_info() {
    # Overall CPU usage
    local cpu_usage
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    
    # Process-specific CPU for backend
    local backend_cpu=0
    if backend_pid=$(pgrep -f "uvicorn.*main:app"); then
        backend_cpu=$(ps -p "$backend_pid" -o %cpu= 2>/dev/null || echo "0")
    fi
    
    # Process-specific CPU for frontend  
    local frontend_cpu=0
    if frontend_pid=$(pgrep -f "vite.*5173"); then
        frontend_cpu=$(ps -p "$frontend_pid" -o %cpu= 2>/dev/null || echo "0")
    fi
    
    echo "$cpu_usage,$backend_cpu,$frontend_cpu"
}

# Function to analyze memory trend
analyze_memory_trend() {
    local samples=("$@")
    local length=${#samples[@]}
    
    if [ $length -lt 5 ]; then
        echo "INSUFFICIENT_DATA"
        return
    fi
    
    # Get first and last 3 samples for trend analysis
    local first_avg=0
    local last_avg=0
    
    # Calculate average of first 3 samples
    for i in {0..2}; do
        first_avg=$(echo "$first_avg + ${samples[i]}" | bc -l)
    done
    first_avg=$(echo "scale=2; $first_avg / 3" | bc -l)
    
    # Calculate average of last 3 samples
    for i in $(seq $((length-3)) $((length-1))); do
        last_avg=$(echo "$last_avg + ${samples[i]}" | bc -l)
    done
    last_avg=$(echo "scale=2; $last_avg / 3" | bc -l)
    
    # Calculate trend
    local trend_percent
    trend_percent=$(echo "scale=2; ($last_avg - $first_avg) * 100 / $first_avg" | bc -l)
    
    # Determine if it's a leak (>5% increase)
    if (( $(echo "$trend_percent > 5" | bc -l) )); then
        echo "LEAK_DETECTED:$trend_percent"
    elif (( $(echo "$trend_percent > 2" | bc -l) )); then
        echo "SLIGHT_INCREASE:$trend_percent"
    else
        echo "STABLE:$trend_percent"
    fi
}

# Header for CSV-style logging
echo "timestamp,mem_total,mem_used,mem_free,mem_available,backend_mem,frontend_mem,cpu_total,backend_cpu,frontend_cpu" | tee -a "$LOG_FILE"

# Main monitoring loop
CHECK_COUNT=0
while [ $(date +%s) -lt $END_TIME ]; do
    CURRENT_TIME=$(date +%s)
    CHECK_COUNT=$((CHECK_COUNT + 1))
    
    # Get memory and CPU info
    memory_info=$(get_memory_info)
    cpu_info=$(get_cpu_info)
    
    # Parse memory info
    IFS=',' read -r mem_total mem_used mem_free mem_available backend_mem frontend_mem <<< "$memory_info"
    IFS=',' read -r cpu_total backend_cpu frontend_cpu <<< "$cpu_info"
    
    # Store samples for analysis
    MEMORY_SAMPLES+=("$mem_used")
    CPU_SAMPLES+=("$cpu_total")
    PROCESS_MEMORY_SAMPLES+=("$backend_mem")
    
    # Log data
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$timestamp,$mem_total,$mem_used,$mem_free,$mem_available,$backend_mem,$frontend_mem,$cpu_total,$backend_cpu,$frontend_cpu" | tee -a "$LOG_FILE"
    
    # Progress indicator
    elapsed_minutes=$(( (CURRENT_TIME - START_TIME) / 60 ))
    total_minutes=$(( MONITOR_DURATION_HOURS * 60 ))
    echo "⏱️  Check $CHECK_COUNT - ${elapsed_minutes}/${total_minutes} minutes elapsed" | tee -a "$LOG_FILE"
    
    # Analyze trends every 10 checks
    if [ $((CHECK_COUNT % 10)) -eq 0 ] && [ $CHECK_COUNT -gt 5 ]; then
        mem_trend=$(analyze_memory_trend "${MEMORY_SAMPLES[@]}")
        echo "📊 Memory trend analysis: $mem_trend" | tee -a "$LOG_FILE"
        
        if [[ "$mem_trend" == LEAK_DETECTED:* ]]; then
            echo "⚠️  POTENTIAL MEMORY LEAK DETECTED!" | tee -a "$LOG_FILE"
        fi
    fi
    
    sleep $INTERVAL_SECONDS
done

# Final analysis
FINAL_TIME=$(date +%s)
ACTUAL_DURATION=$((FINAL_TIME - START_TIME))

echo "🧠 Memory leak detection completed!" | tee -a "$LOG_FILE"
echo "===============================================" | tee -a "$LOG_FILE"

# Calculate statistics
if [ ${#MEMORY_SAMPLES[@]} -gt 0 ]; then
    # Initial and final memory usage
    initial_memory=${MEMORY_SAMPLES[0]}
    final_memory=${MEMORY_SAMPLES[-1]}
    memory_change=$(echo "scale=2; $final_memory - $initial_memory" | bc -l)
    memory_change_percent=$(echo "scale=2; $memory_change * 100 / $initial_memory" | bc -l)
    
    # Max memory usage
    max_memory=$(printf '%s\n' "${MEMORY_SAMPLES[@]}" | sort -n | tail -1)
    
    # Average memory usage
    total_memory=0
    for mem in "${MEMORY_SAMPLES[@]}"; do
        total_memory=$(echo "$total_memory + $mem" | bc -l)
    done
    avg_memory=$(echo "scale=2; $total_memory / ${#MEMORY_SAMPLES[@]}" | bc -l)
    
    echo "📈 Memory Statistics:" | tee -a "$LOG_FILE"
    echo "  Initial: ${initial_memory} MB" | tee -a "$LOG_FILE"
    echo "  Final: ${final_memory} MB" | tee -a "$LOG_FILE"
    echo "  Change: ${memory_change} MB (${memory_change_percent}%)" | tee -a "$LOG_FILE"
    echo "  Maximum: ${max_memory} MB" | tee -a "$LOG_FILE"
    echo "  Average: ${avg_memory} MB" | tee -a "$LOG_FILE"
    
    # Final trend analysis
    final_trend=$(analyze_memory_trend "${MEMORY_SAMPLES[@]}")
    echo "🎯 Final trend: $final_trend" | tee -a "$LOG_FILE"
fi

# Generate JSON report
cat > "$REPORT_FILE" << EOF
{
  "test_type": "memory_leak_detection",
  "start_time": "$START_TIME",
  "end_time": "$FINAL_TIME",
  "duration_seconds": $ACTUAL_DURATION,
  "duration_minutes": $(echo "scale=0; $ACTUAL_DURATION / 60" | bc -l),
  "check_count": $CHECK_COUNT,
  "check_interval_seconds": $INTERVAL_SECONDS,
  "memory_statistics": {
    "initial_mb": ${initial_memory:-0},
    "final_mb": ${final_memory:-0},
    "change_mb": ${memory_change:-0},
    "change_percent": ${memory_change_percent:-0},
    "maximum_mb": ${max_memory:-0},
    "average_mb": ${avg_memory:-0}
  },
  "trend_analysis": "${final_trend:-UNKNOWN}",
  "log_file": "$LOG_FILE",
  "test_status": "$(if [[ "${final_trend:-}" == LEAK_DETECTED:* ]]; then echo "MEMORY_LEAK_DETECTED"; elif [[ "${final_trend:-}" == STABLE:* ]]; then echo "PASSED"; else echo "MONITORING_COMPLETED"; fi)"
}
EOF

echo "📊 Report generated: $REPORT_FILE" | tee -a "$LOG_FILE"

# Determine test result
if [[ "${final_trend:-}" == LEAK_DETECTED:* ]]; then
    echo "❌ T062 FAILED: Memory leak detected!" | tee -a "$LOG_FILE"
    exit 1
elif [[ "${final_trend:-}" == STABLE:* ]] || [[ "${memory_change_percent:-0}" < 3 ]]; then
    echo "✅ T062 PASSED: No memory leaks detected!" | tee -a "$LOG_FILE"
    exit 0
else
    echo "⚠️  T062 COMPLETED: Monitoring completed, manual review required" | tee -a "$LOG_FILE"
    exit 0
fi