"""System health monitoring including git sync status"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Optional
import os

from .git_monitor import GitSyncMonitor

logger = logging.getLogger(__name__)


class SystemHealthMonitor:
    """Monitor overall system health including git sync"""
    
    def __init__(self, shared_memory=None, log_dir: Optional[str] = None):
        self.shared_memory = shared_memory
        self.log_dir = log_dir or "logs"
        self.git_monitor = GitSyncMonitor()
        self.last_health_check = None
        self.health_issues = []
        
    def check_system_health(self) -> Dict:
        """Comprehensive system health check"""
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "components": {}
        }
        
        # Check git sync health
        git_health = self._check_git_health()
        health_report["components"]["git_sync"] = git_health
        
        # Check shared memory health
        memory_health = self._check_memory_health()
        health_report["components"]["shared_memory"] = memory_health
        
        # Check log directory health
        log_health = self._check_log_health()
        health_report["components"]["logging"] = log_health
        
        # Determine overall status
        if any(component["status"] == "critical" for component in health_report["components"].values()):
            health_report["overall_status"] = "critical"
        elif any(component["status"] == "warning" for component in health_report["components"].values()):
            health_report["overall_status"] = "warning"
        
        self.last_health_check = datetime.now()
        return health_report
    
    def _check_git_health(self) -> Dict:
        """Check git synchronization health"""
        try:
            git_status = self.git_monitor.get_sync_health_status()
            
            health = {
                "status": "healthy",
                "message": git_status["status_message"],
                "details": git_status
            }
            
            # Determine health level
            if git_status["commits_ahead"] > 10:
                health["status"] = "critical"
                health["message"] = f"CRITICAL: {git_status['commits_ahead']} commits not pushed!"
            elif git_status["commits_ahead"] > 5:
                health["status"] = "warning"
                health["message"] = f"WARNING: {git_status['commits_ahead']} commits pending push"
            elif not git_status["healthy"]:
                health["status"] = "warning"
            
            return health
            
        except Exception as e:
            logger.error(f"Git health check failed: {e}")
            return {
                "status": "error",
                "message": f"Failed to check git health: {str(e)}",
                "details": {}
            }
    
    def _check_memory_health(self) -> Dict:
        """Check shared memory health"""
        if not self.shared_memory:
            return {
                "status": "unknown",
                "message": "Shared memory not configured",
                "details": {}
            }
        
        try:
            # Get current state to verify database is accessible
            state = self.shared_memory.get_current_state()
            
            health = {
                "status": "healthy",
                "message": "Shared memory operational",
                "details": {
                    "religion_name": state.get("religion_name", "Not set"),
                    "total_cycles": state.get("total_cycles", 0),
                    "last_updated": state.get("last_updated", "Unknown")
                }
            }
            
            return health
            
        except Exception as e:
            logger.error(f"Memory health check failed: {e}")
            return {
                "status": "error",
                "message": f"Shared memory error: {str(e)}",
                "details": {}
            }
    
    def _check_log_health(self) -> Dict:
        """Check logging system health"""
        try:
            # Check if log directory exists and is writable
            if not os.path.exists(self.log_dir):
                return {
                    "status": "error",
                    "message": "Log directory does not exist",
                    "details": {"log_dir": self.log_dir}
                }
            
            # Check available space (simple check)
            stat = os.statvfs(self.log_dir)
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            
            health = {
                "status": "healthy",
                "message": f"Logging operational ({free_gb:.1f}GB free)",
                "details": {
                    "log_directory": self.log_dir,
                    "free_space_gb": round(free_gb, 2)
                }
            }
            
            if free_gb < 0.1:  # Less than 100MB
                health["status"] = "critical"
                health["message"] = "Critical: Low disk space for logs"
            elif free_gb < 1:  # Less than 1GB
                health["status"] = "warning"
                health["message"] = "Warning: Low disk space for logs"
            
            return health
            
        except Exception as e:
            logger.error(f"Log health check failed: {e}")
            return {
                "status": "error",
                "message": f"Log system error: {str(e)}",
                "details": {}
            }
    
    async def periodic_health_check(self, interval_seconds: int = 300):
        """Run health checks periodically"""
        while True:
            try:
                health_report = self.check_system_health()
                
                # Log health status
                if health_report["overall_status"] == "critical":
                    logger.critical(f"System health CRITICAL: {health_report}")
                elif health_report["overall_status"] == "warning":
                    logger.warning(f"System health WARNING: {health_report}")
                else:
                    logger.info("System health check: All systems operational")
                
                # Take action on critical git sync issues
                git_health = health_report["components"].get("git_sync", {})
                if git_health.get("status") == "critical":
                    logger.critical("Git sync is critically behind. Attempting automatic recovery...")
                    
                    # Try to force sync
                    success = self.git_monitor.sync_repository(
                        ['public/data/', 'logs/'],
                        f"Emergency sync: {datetime.now().isoformat()}\n\n🚨 Automated recovery attempt"
                    )
                    
                    if success:
                        logger.info("✅ Automatic git sync recovery successful")
                    else:
                        logger.error("❌ Automatic git sync recovery failed. Manual intervention required!")
                
            except Exception as e:
                logger.error(f"Health check error: {e}", exc_info=True)
            
            await asyncio.sleep(interval_seconds)


def run_health_monitor(shared_memory=None, log_dir: Optional[str] = None):
    """Run the health monitor as a background task"""
    monitor = SystemHealthMonitor(shared_memory, log_dir)
    asyncio.create_task(monitor.periodic_health_check())