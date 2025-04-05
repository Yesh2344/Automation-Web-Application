from app.models.user import TaskLog
from app import db
import logging

logger = logging.getLogger(__name__)

def log_task_event(task_id, status, message):
    """
    Log a task event to the database.
    
    Args:
        task_id (int): ID of the task
        status (str): Status of the task (e.g., 'pending', 'processing', 'completed', 'failed')
        message (str): Log message
        
    Returns:
        TaskLog: The created log entry
    """
    try:
        log_entry = TaskLog(
            task_id=task_id,
            status=status,
            message=message
        )
        db.session.add(log_entry)
        db.session.commit()
        logger.info(f"Task {task_id} - {status}: {message}")
        return log_entry
    except Exception as e:
        logger.error(f"Failed to log task event: {str(e)}")
        db.session.rollback()
        return None
