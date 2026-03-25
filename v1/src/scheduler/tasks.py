from celery import Celery
from celery.schedules import crontab
from datetime import datetime, timedelta
import structlog
from src.core.config import settings
from src.core.pipeline import ContentPipeline
from src.core.models import ContentInput, Platform, ContentType

logger = structlog.get_logger()

# Initialize Celery
celery_app = Celery(
    "content_machine",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'publish-scheduled-content': {
        'task': 'src.scheduler.tasks.publish_scheduled_content',
        'schedule': crontab(minute='*'),  # Run every minute
    },
    'cleanup-old-tasks': {
        'task': 'src.scheduler.tasks.cleanup_old_tasks',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
}


@celery_app.task(bind=True, max_retries=3)
def create_content_task(self, input_data: dict):
    """Celery task for creating content"""
    try:
        logger.info(f"Starting content creation task: {self.request.id}")
        
        # Convert dict to ContentInput
        content_input = ContentInput(**input_data)
        
        # Create content using pipeline
        pipeline = ContentPipeline()
        content_pieces = pipeline.create_content(content_input)
        
        if content_pieces:
            logger.info(f"Content creation completed: {len(content_pieces)} pieces created")
            return {
                "success": True,
                "content_pieces": [piece.dict() for piece in content_pieces],
                "task_id": self.request.id
            }
        else:
            logger.error("No content pieces were created")
            return {"success": False, "error": "No content created"}
            
    except Exception as exc:
        logger.error(f"Content creation task failed: {str(exc)}")
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries
            logger.info(f"Retrying task in {countdown} seconds")
            raise self.retry(countdown=countdown, exc=exc)
        
        return {"success": False, "error": str(exc)}


@celery_app.task(bind=True, max_retries=3)
def publish_content_task(self, content_piece_id: str, platform: str):
    """Celery task for publishing content"""
    try:
        logger.info(f"Starting publish task: {self.request.id}")
        
        # Get platform enum
        platform_enum = Platform(platform)
        
        # In a real implementation, you would retrieve the content piece from database
        # For now, we'll use a placeholder
        pipeline = ContentPipeline()
        
        # This would normally fetch from database
        # content_piece = get_content_piece_from_db(content_piece_id)
        
        result = {"message": "Publish task completed - requires database integration"}
        
        logger.info(f"Publish task completed: {self.request.id}")
        return result
        
    except Exception as exc:
        logger.error(f"Publish task failed: {str(exc)}")
        
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries
            raise self.retry(countdown=countdown, exc=exc)
        
        return {"success": False, "error": str(exc)}


@celery_app.task
def publish_scheduled_content():
    """Task to publish scheduled content"""
    try:
        logger.info("Checking for scheduled content to publish")
        
        # In a real implementation, you would:
        # 1. Query database for content scheduled to publish now
        # 2. Publish each piece using the platform integrations
        # 3. Update status in database
        
        # Placeholder implementation
        scheduled_count = 0  # Would be actual count from database
        logger.info(f"Published {scheduled_count} scheduled pieces")
        
        return {"published_count": scheduled_count}
        
    except Exception as e:
        logger.error(f"Error in publish_scheduled_content: {str(e)}")
        return {"error": str(e)}


@celery_app.task
def cleanup_old_tasks():
    """Task to clean up old task results"""
    try:
        logger.info("Cleaning up old task results")
        
        # Clean up task results older than 7 days
        cleanup_date = datetime.utcnow() - timedelta(days=7)
        
        # In a real implementation, you would clean up database records
        
        logger.info("Task cleanup completed")
        return {"cleanup_date": cleanup_date.isoformat()}
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_tasks: {str(e)}")
        return {"error": str(e)}


@celery_app.task
def send_review_notification(content_piece_id: str):
    """Task to send notification for human review"""
    try:
        logger.info(f"Sending review notification for: {content_piece_id}")
        
        # In a real implementation, you would:
        # 1. Send email/notification
        # 2. Update notification status in database
        
        return {"notification_sent": True, "content_piece_id": content_piece_id}
        
    except Exception as e:
        logger.error(f"Error sending review notification: {str(e)}")
        return {"error": str(e)}
