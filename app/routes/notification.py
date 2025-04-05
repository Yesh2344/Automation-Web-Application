from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.user import Task
from app import db
from app.utils.task_logger import log_task_event
import json
from datetime import datetime, timedelta

notification_bp = Blueprint('notification', __name__, url_prefix='/notification')

@notification_bp.route('/')
@login_required
def index():
    """Notification settings view"""
    return render_template('notification/index.html', title='Notification Settings')

@notification_bp.route('/settings', methods=['GET'])
@login_required
def get_settings():
    """Get notification settings for the current user"""
    # In a real application, this would be stored in the database
    # For this demo, we'll store it in the app config
    if 'notifications' not in current_app.config:
        current_app.config['notifications'] = {}
    
    if current_user.id not in current_app.config['notifications']:
        # Default settings
        current_app.config['notifications'][current_user.id] = {
            'email_notifications': True,
            'task_completed': True,
            'task_failed': True,
            'daily_summary': False,
            'email': current_user.email
        }
    
    return jsonify(current_app.config['notifications'][current_user.id])

@notification_bp.route('/settings', methods=['POST'])
@login_required
def update_settings():
    """Update notification settings for the current user"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'notifications' not in current_app.config:
        current_app.config['notifications'] = {}
    
    # Update settings
    current_app.config['notifications'][current_user.id] = {
        'email_notifications': data.get('email_notifications', True),
        'task_completed': data.get('task_completed', True),
        'task_failed': data.get('task_failed', True),
        'daily_summary': data.get('daily_summary', False),
        'email': data.get('email', current_user.email)
    }
    
    return jsonify({
        'message': 'Notification settings updated successfully',
        'settings': current_app.config['notifications'][current_user.id]
    })

@notification_bp.route('/test', methods=['POST'])
@login_required
def test_notification():
    """Send a test notification"""
    # In a real application, this would send an actual email
    # For this demo, we'll just return a success message
    
    return jsonify({
        'message': 'Test notification sent successfully',
        'email': current_user.email,
        'timestamp': datetime.utcnow().isoformat()
    })

# Function to check if notifications should be sent (would be called from other parts of the application)
def should_notify(user_id, event_type):
    """
    Check if a notification should be sent for a specific user and event type
    
    Args:
        user_id (int): User ID
        event_type (str): Event type (e.g., 'task_completed', 'task_failed')
        
    Returns:
        bool: True if notification should be sent, False otherwise
    """
    if 'notifications' not in current_app.config or user_id not in current_app.config['notifications']:
        return False
    
    settings = current_app.config['notifications'][user_id]
    
    # Check if email notifications are enabled
    if not settings.get('email_notifications', True):
        return False
    
    # Check if this specific event type is enabled
    return settings.get(event_type, False)

# Function to send notification (would be called from other parts of the application)
def send_notification(user_id, subject, message, event_type=None):
    """
    Send a notification to a user
    
    Args:
        user_id (int): User ID
        subject (str): Notification subject
        message (str): Notification message
        event_type (str, optional): Event type for filtering
        
    Returns:
        bool: True if notification was sent, False otherwise
    """
    # Check if notification should be sent
    if event_type and not should_notify(user_id, event_type):
        return False
    
    # In a real application, this would send an actual email
    # For this demo, we'll just log it
    current_app.logger.info(f"Notification to user {user_id}: {subject} - {message}")
    
    # Return success
    return True
