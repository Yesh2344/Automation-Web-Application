from app.tasks.task_scheduler import run_scheduled_tasks
from app.utils.task_logger import log_task_event
from app import celery
from celery.schedules import crontab
from app.models.user import Task
from app import db
import datetime
import logging

logger = logging.getLogger(__name__)

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run every 10 minutes
    sender.add_periodic_task(600.0, check_pending_tasks.s(), name='check pending tasks')
    
    # Run at midnight every day
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        cleanup_completed_tasks.s(),
        name='cleanup completed tasks'
    )

@celery.task
def check_pending_tasks():
    """
    Periodic task to check for pending tasks and process them.
    This is a scheduled task that runs automatically.
    """
    logger.info("Checking for pending tasks")
    pending_tasks = Task.query.filter_by(status='pending').all()
    
    for task in pending_tasks:
        # Log that we're scheduling this task
        log_task_event(task.id, 'scheduled', f"Task scheduled for processing: {task.name}")
    
    # Call the actual task scheduler
    result = run_scheduled_tasks()
    logger.info(f"Task scheduling result: {result}")
    
    return result

@celery.task
def cleanup_completed_tasks():
    """
    Archive or clean up tasks that have been completed for more than 30 days.
    This is a maintenance task that runs daily.
    """
    logger.info("Running cleanup of old completed tasks")
    
    # In a real application, this might archive tasks to another storage
    # or perform other cleanup operations
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=30)
    old_tasks = Task.query.filter(
        Task.status == 'completed',
        Task.completed_at <= cutoff_date
    ).all()
    
    for task in old_tasks:
        # Log that we're archiving this task
        log_task_event(task.id, 'archived', f"Task archived after 30 days: {task.name}")
        
        # In a real application, you might archive these instead of just logging
        logger.info(f"Would archive task: {task.id} - {task.name}")
    
    return f"Processed {len(old_tasks)} old completed tasks"
