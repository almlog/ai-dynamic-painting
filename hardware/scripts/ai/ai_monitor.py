#!/usr/bin/env python3
"""
AI Dynamic Painting System - Phase 2
Hardware AI Generation Status Monitoring

T269: Hardware AI generation status monitoring implementation
Comprehensive monitoring system for AI generation processes, learning system, and hardware integration.

Features:
- Real-time AI generation status monitoring
- Hardware resource monitoring (CPU, memory, temperature)
- Learning system progress tracking  
- Automatic alerting and notifications
- Performance metrics collection
- System health checks
- Integration with M5STACK displays
"""

import asyncio
import aiohttp
import json
import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import subprocess
import sys
import signal
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIMonitor:
    """Hardware AI Generation Status Monitor"""
    
    def __init__(self, config_file: str = "ai_monitor_config.json"):
        self.config = self.load_config(config_file)
        self.api_base_url = self.config.get("api_base_url", "http://localhost:8000")
        self.monitor_interval = self.config.get("monitor_interval", 10)  # seconds
        self.alert_thresholds = self.config.get("alert_thresholds", {})
        self.running = False
        self.session = None
        
        # Monitoring data
        self.ai_status = {}
        self.hardware_stats = {}
        self.learning_progress = {}
        self.alerts = []
        self.performance_history = []
        
        # Performance tracking
        self.start_time = datetime.now()
        self.total_monitoring_cycles = 0
        self.last_successful_update = None
        
        logger.info("AI Monitor initialized")
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        default_config = {
            "api_base_url": "http://192.168.10.7:8000",
            "monitor_interval": 10,
            "alert_thresholds": {
                "cpu_usage": 85.0,
                "memory_usage": 90.0,
                "disk_usage": 95.0,
                "temperature": 75.0,
                "generation_failure_rate": 20.0,
                "api_response_time": 5.0
            },
            "m5stack_endpoints": [
                "http://192.168.10.8",  # M5STACK display device
                "http://192.168.10.9"   # M5STACK control device
            ],
            "notification_channels": {
                "console": True,
                "log_file": True,
                "m5stack_display": True,
                "api_webhook": False
            },
            "data_retention_hours": 24,
            "performance_metrics": {
                "collect_detailed": True,
                "save_to_file": True,
                "upload_to_api": False
            }
        }
        
        try:
            if Path(config_file).exists():
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
                    logger.info(f"Configuration loaded from {config_file}")
            else:
                # Create default config file
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"Default configuration created: {config_file}")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
        
        return default_config
    
    async def start_monitoring(self):
        """Start the monitoring loop"""
        self.running = True
        self.session = aiohttp.ClientSession()
        
        logger.info("AI Monitor started")
        
        try:
            while self.running:
                start_cycle = time.time()
                
                # Perform monitoring tasks
                await self.update_ai_status()
                await self.update_hardware_stats()
                await self.update_learning_progress()
                await self.check_alerts()
                await self.notify_m5stack_devices()
                await self.save_performance_data()
                
                self.total_monitoring_cycles += 1
                cycle_time = time.time() - start_cycle
                
                if cycle_time < self.monitor_interval:
                    await asyncio.sleep(self.monitor_interval - cycle_time)
                
                # Log monitoring status every 10 cycles
                if self.total_monitoring_cycles % 10 == 0:
                    logger.info(f"Monitoring cycle {self.total_monitoring_cycles} completed in {cycle_time:.2f}s")
                    
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
        finally:
            await self.cleanup()
    
    async def update_ai_status(self):
        """Update AI generation status from API"""
        try:
            async with self.session.get(f"{self.api_base_url}/api/m5stack/ai-status", timeout=5) as response:
                if response.status == 200:
                    self.ai_status = await response.json()
                    self.last_successful_update = datetime.now()
                    
                    # Extract key metrics
                    gen_status = self.ai_status.get("ai_generation_status", {})
                    learning_status = self.ai_status.get("learning_progress", {})
                    
                    # Log important status changes
                    if gen_status.get("status") == "generating":
                        progress = gen_status.get("progress_percentage", 0)
                        task = gen_status.get("current_task", "Unknown")
                        logger.info(f"AI Generation: {progress}% - {task}")
                    
                    # Track learning progress
                    if learning_status.get("learning_active"):
                        interactions = learning_status.get("total_interactions", 0)
                        confidence = learning_status.get("confidence_score", 0)
                        logger.debug(f"Learning: {interactions} interactions, {confidence:.2%} confidence")
                        
                else:
                    logger.warning(f"Failed to get AI status: HTTP {response.status}")
                    self.ai_status = {}
        except Exception as e:
            logger.error(f"Error updating AI status: {e}")
            self.ai_status = {}
    
    async def update_hardware_stats(self):
        """Update hardware resource statistics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network statistics
            network = psutil.net_io_counters()
            
            # Process count
            process_count = len(psutil.pids())
            
            # Temperature (if available)
            temperature = None
            try:
                # Try to get CPU temperature on Raspberry Pi
                result = subprocess.run(
                    ['vcgencmd', 'measure_temp'], 
                    capture_output=True, 
                    text=True, 
                    timeout=2
                )
                if result.returncode == 0:
                    temp_str = result.stdout.strip()
                    if 'temp=' in temp_str:
                        temperature = float(temp_str.split('=')[1].replace("'C", ""))
            except:
                pass  # Temperature monitoring not available
            
            self.hardware_stats = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk_percent,
                "disk_free_gb": disk.free / (1024**3),
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv,
                "process_count": process_count,
                "temperature_celsius": temperature,
                "uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600
            }
            
            logger.debug(f"Hardware: CPU {cpu_percent:.1f}%, Memory {memory_percent:.1f}%, Disk {disk_percent:.1f}%")
            
        except Exception as e:
            logger.error(f"Error updating hardware stats: {e}")
            self.hardware_stats = {}
    
    async def update_learning_progress(self):
        """Update learning system progress"""
        try:
            # Extract learning data from AI status
            learning_data = self.ai_status.get("learning_progress", {})
            
            if learning_data:
                self.learning_progress = {
                    "timestamp": datetime.now().isoformat(),
                    "total_interactions": learning_data.get("total_interactions", 0),
                    "preferences_learned": learning_data.get("preferences_learned", 0),
                    "confidence_score": learning_data.get("confidence_score", 0.0),
                    "learning_active": learning_data.get("learning_active", False),
                    "learning_rate": self.calculate_learning_rate(),
                    "improvement_trend": self.calculate_improvement_trend()
                }
            
        except Exception as e:
            logger.error(f"Error updating learning progress: {e}")
            self.learning_progress = {}
    
    def calculate_learning_rate(self) -> float:
        """Calculate learning rate based on recent interactions"""
        # Simple implementation - could be enhanced
        interactions = self.learning_progress.get("total_interactions", 0)
        uptime_hours = self.hardware_stats.get("uptime_hours", 1)
        return interactions / max(uptime_hours, 0.1)
    
    def calculate_improvement_trend(self) -> str:
        """Calculate improvement trend based on confidence scores"""
        # Simple implementation - could track historical data
        confidence = self.learning_progress.get("confidence_score", 0.0)
        
        if confidence > 0.8:
            return "excellent"
        elif confidence > 0.6:
            return "good"
        elif confidence > 0.4:
            return "improving"
        elif confidence > 0.2:
            return "learning"
        else:
            return "initial"
    
    async def check_alerts(self):
        """Check for alert conditions and generate notifications"""
        new_alerts = []
        
        try:
            # Check hardware thresholds
            if self.hardware_stats:
                if self.hardware_stats.get("cpu_percent", 0) > self.alert_thresholds.get("cpu_usage", 85):
                    new_alerts.append({
                        "type": "hardware",
                        "severity": "warning",
                        "message": f"High CPU usage: {self.hardware_stats['cpu_percent']:.1f}%",
                        "timestamp": datetime.now().isoformat()
                    })
                
                if self.hardware_stats.get("memory_percent", 0) > self.alert_thresholds.get("memory_usage", 90):
                    new_alerts.append({
                        "type": "hardware", 
                        "severity": "warning",
                        "message": f"High memory usage: {self.hardware_stats['memory_percent']:.1f}%",
                        "timestamp": datetime.now().isoformat()
                    })
                
                if self.hardware_stats.get("temperature_celsius"):
                    temp = self.hardware_stats["temperature_celsius"]
                    if temp > self.alert_thresholds.get("temperature", 75):
                        new_alerts.append({
                            "type": "hardware",
                            "severity": "critical" if temp > 80 else "warning",
                            "message": f"High temperature: {temp:.1f}°C",
                            "timestamp": datetime.now().isoformat()
                        })
            
            # Check AI generation issues
            if self.ai_status:
                gen_status = self.ai_status.get("ai_generation_status", {})
                if gen_status.get("status") == "error":
                    new_alerts.append({
                        "type": "ai_generation",
                        "severity": "error",
                        "message": "AI generation error detected",
                        "timestamp": datetime.now().isoformat()
                    })
            
            # Check API connectivity
            if not self.last_successful_update or \
               (datetime.now() - self.last_successful_update).total_seconds() > 60:
                new_alerts.append({
                    "type": "connectivity",
                    "severity": "error", 
                    "message": "API connectivity lost",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Add new alerts and notify
            for alert in new_alerts:
                self.alerts.append(alert)
                await self.send_alert_notification(alert)
            
            # Clean up old alerts (keep last 24 hours)
            cutoff_time = datetime.now() - timedelta(hours=24)
            self.alerts = [
                alert for alert in self.alerts 
                if datetime.fromisoformat(alert["timestamp"]) > cutoff_time
            ]
            
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    async def send_alert_notification(self, alert: Dict[str, Any]):
        """Send alert notification through configured channels"""
        try:
            # Console/log notification
            if self.config["notification_channels"].get("console"):
                severity = alert["severity"].upper()
                message = alert["message"]
                logger.warning(f"[{severity}] {message}")
            
            # M5STACK display notification
            if self.config["notification_channels"].get("m5stack_display"):
                await self.send_m5stack_alert(alert)
            
        except Exception as e:
            logger.error(f"Error sending alert notification: {e}")
    
    async def send_m5stack_alert(self, alert: Dict[str, Any]):
        """Send alert to M5STACK devices"""
        try:
            alert_data = {
                "type": "alert",
                "severity": alert["severity"],
                "message": alert["message"][:50],  # Truncate for display
                "timestamp": alert["timestamp"]
            }
            
            for endpoint in self.config.get("m5stack_endpoints", []):
                try:
                    async with self.session.post(
                        f"{endpoint}/alert",
                        json=alert_data,
                        timeout=3
                    ) as response:
                        if response.status == 200:
                            logger.debug(f"Alert sent to M5STACK: {endpoint}")
                except:
                    pass  # M5STACK device may not be available
                    
        except Exception as e:
            logger.error(f"Error sending M5STACK alert: {e}")
    
    async def notify_m5stack_devices(self):
        """Send status updates to M5STACK devices"""
        try:
            if not self.config["notification_channels"].get("m5stack_display"):
                return
            
            # Prepare status summary for M5STACK
            status_summary = {
                "timestamp": datetime.now().isoformat(),
                "ai_status": self.ai_status.get("ai_generation_status", {}),
                "hardware": {
                    "cpu": self.hardware_stats.get("cpu_percent", 0),
                    "memory": self.hardware_stats.get("memory_percent", 0),
                    "temperature": self.hardware_stats.get("temperature_celsius")
                },
                "learning": self.learning_progress,
                "alerts": len([a for a in self.alerts if a["severity"] in ["warning", "critical", "error"]]),
                "uptime": self.hardware_stats.get("uptime_hours", 0)
            }
            
            # Send to M5STACK devices
            for endpoint in self.config.get("m5stack_endpoints", []):
                try:
                    async with self.session.post(
                        f"{endpoint}/status-update",
                        json=status_summary,
                        timeout=3
                    ) as response:
                        if response.status == 200:
                            logger.debug(f"Status sent to M5STACK: {endpoint}")
                except:
                    pass  # Device may not be available
                    
        except Exception as e:
            logger.error(f"Error notifying M5STACK devices: {e}")
    
    async def save_performance_data(self):
        """Save performance data to file"""
        try:
            if not self.config["performance_metrics"].get("save_to_file"):
                return
            
            performance_record = {
                "timestamp": datetime.now().isoformat(),
                "cycle": self.total_monitoring_cycles,
                "ai_status": self.ai_status,
                "hardware_stats": self.hardware_stats,
                "learning_progress": self.learning_progress,
                "active_alerts": len(self.alerts)
            }
            
            self.performance_history.append(performance_record)
            
            # Save to file every 10 cycles
            if self.total_monitoring_cycles % 10 == 0:
                filename = f"ai_monitor_data_{datetime.now().strftime('%Y%m%d')}.json"
                with open(filename, 'w') as f:
                    json.dump(self.performance_history, f, indent=2)
                
                # Keep only recent data in memory
                cutoff_time = datetime.now() - timedelta(hours=self.config.get("data_retention_hours", 24))
                self.performance_history = [
                    record for record in self.performance_history
                    if datetime.fromisoformat(record["timestamp"]) > cutoff_time
                ]
                
        except Exception as e:
            logger.error(f"Error saving performance data: {e}")
    
    async def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary"""
        return {
            "monitor_info": {
                "running": self.running,
                "uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600,
                "total_cycles": self.total_monitoring_cycles,
                "last_update": self.last_successful_update.isoformat() if self.last_successful_update else None
            },
            "ai_status": self.ai_status,
            "hardware_stats": self.hardware_stats,
            "learning_progress": self.learning_progress,
            "alerts": {
                "total": len(self.alerts),
                "critical": len([a for a in self.alerts if a["severity"] == "critical"]),
                "warnings": len([a for a in self.alerts if a["severity"] == "warning"]),
                "errors": len([a for a in self.alerts if a["severity"] == "error"])
            },
            "recent_alerts": self.alerts[-5:] if len(self.alerts) > 5 else self.alerts
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        self.running = False
        if self.session:
            await self.session.close()
        logger.info("AI Monitor cleanup completed")
    
    def stop(self):
        """Stop monitoring"""
        self.running = False


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Dynamic Painting Hardware Monitor")
    parser.add_argument("--config", default="ai_monitor_config.json", help="Configuration file path")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--status", action="store_true", help="Show current status and exit")
    args = parser.parse_args()
    
    monitor = AIMonitor(args.config)
    
    if args.status:
        # Quick status check
        try:
            await monitor.update_ai_status()
            await monitor.update_hardware_stats()
            status = await monitor.get_status_summary()
            print(json.dumps(status, indent=2))
        except Exception as e:
            print(f"Error getting status: {e}")
        return
    
    # Handle signals for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, stopping monitor...")
        monitor.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if args.daemon:
            logger.info("Starting AI Monitor in daemon mode")
        
        await monitor.start_monitoring()
        
    except Exception as e:
        logger.error(f"Monitor failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())