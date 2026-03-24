from typing import Dict, Any, Optional
import structlog
from datetime import datetime
from src.scheduler.tasks import create_content_task, publish_content_task, send_review_notification
from src.core.models import ContentInput, Platform, ContentType

logger = structlog.get_logger()


class ContentScheduler:
    """Scheduler for managing content creation and publishing"""
    
    def __init__(self):
        self.logger = structlog.get_logger()
    
    def schedule_content_creation(self, input_data: ContentInput, 
                                 scheduled_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Schedule content creation for a specific time"""
        try:
            if scheduled_time and scheduled_time <= datetime.utcnow():
                return {"success": False, "error": "Scheduled time must be in the future"}
            
            # Convert input data to dict for Celery
            input_dict = input_data.dict()
            
            if scheduled_time:
                # Schedule for specific time
                task = create_content_task.apply_async(
                    args=[input_dict],
                    eta=scheduled_time
                )
                self.logger.info(f"Content creation scheduled for {scheduled_time}: {task.id}")
            else:
                # Execute immediately
                task = create_content_task.delay(input_dict)
                self.logger.info(f"Content creation task started: {task.id}")
            
            return {
                "success": True,
                "task_id": task.id,
                "scheduled_time": scheduled_time.isoformat() if scheduled_time else None
            }
            
        except Exception as e:
            self.logger.error(f"Error scheduling content creation: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def schedule_content_publication(self, content_piece_id: str, 
                                   platform: Platform,
                                   scheduled_time: datetime) -> Dict[str, Any]:
        """Schedule content publication for a specific time"""
        try:
            if scheduled_time <= datetime.utcnow():
                return {"success": False, "error": "Scheduled time must be in the future"}
            
            # Schedule publication
            task = publish_content_task.apply_async(
                args=[content_piece_id, platform.value],
                eta=scheduled_time
            )
            
            self.logger.info(f"Content publication scheduled for {scheduled_time}: {task.id}")
            
            return {
                "success": True,
                "task_id": task.id,
                "scheduled_time": scheduled_time.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error scheduling content publication: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def schedule_review_notification(self, content_piece_id: str) -> Dict[str, Any]:
        """Schedule human review notification"""
        try:
            task = send_review_notification.delay(content_piece_id)
            
            self.logger.info(f"Review notification scheduled: {task.id}")
            
            return {
                "success": True,
                "task_id": task.id
            }
            
        except Exception as e:
            self.logger.error(f"Error scheduling review notification: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a scheduled task"""
        try:
            from celery.result import AsyncResult
            
            result = AsyncResult(task_id)
            
            return {
                "task_id": task_id,
                "status": result.status,
                "result": result.result if result.ready() else None,
                "date_done": str(result.date_done) if result.date_done else None
            }
            
        except Exception as e:
            self.logger.error(f"Error getting task status: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """Cancel a scheduled task"""
        try:
            from celery.result import AsyncResult
            
            result = AsyncResult(task_id)
            
            if result.revoke():
                self.logger.info(f"Task cancelled: {task_id}")
                return {"success": True, "task_id": task_id}
            else:
                return {"success": False, "error": "Task could not be cancelled"}
            
        except Exception as e:
            self.logger.error(f"Error cancelling task: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_scheduled_tasks(self) -> Dict[str, Any]:
        """Get list of scheduled tasks"""
        try:
            from celery import current_app
            
            # Get active tasks
            inspect = current_app.control.inspect()
            active_tasks = inspect.active()
            scheduled_tasks = inspect.scheduled()
            
            return {
                "active_tasks": active_tasks,
                "scheduled_tasks": scheduled_tasks
            }
            
        except Exception as e:
            self.logger.error(f"Error getting scheduled tasks: {str(e)}")
            return {"success": False, "error": str(e)}
