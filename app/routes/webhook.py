from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models.user import Task
from app import db
from app.utils.task_logger import log_task_event
from app.tasks.automation_processor import process_automation_task
import json
from datetime import datetime, timedelta
import requests

webhook_bp = Blueprint('webhook', __name__, url_prefix='/webhook')

@webhook_bp.route('/')
@login_required
def index():
    """Webhook configuration view"""
    return render_template('webhook/index.html', title='Webhook Integration')

@webhook_bp.route('/register', methods=['POST'])
@login_required
def register_webhook():
    """Register a new webhook"""
    data = request.get_json()
    
    if not data or not data.get('url') or not data.get('event_type'):
        return jsonify({'error': 'URL and event type are required'}), 400
    
    # In a real application, this would be stored in the database
    # For this demo, we'll store it in the app config
    if 'webhooks' not in current_app.config:
        current_app.config['webhooks'] = {}
    
    if current_user.id not in current_app.config['webhooks']:
        current_app.config['webhooks'][current_user.id] = []
    
    webhook_id = len(current_app.config['webhooks'][current_user.id]) + 1
    
    webhook = {
        'id': webhook_id,
        'url': data['url'],
        'event_type': data['event_type'],
        'created_at': datetime.utcnow().isoformat(),
        'active': True
    }
    
    current_app.config['webhooks'][current_user.id].append(webhook)
    
    return jsonify({
        'message': 'Webhook registered successfully',
        'webhook': webhook
    })

@webhook_bp.route('/list', methods=['GET'])
@login_required
def list_webhooks():
    """List all webhooks for the current user"""
    if 'webhooks' not in current_app.config or current_user.id not in current_app.config['webhooks']:
        return jsonify({'webhooks': []})
    
    return jsonify({
        'webhooks': current_app.config['webhooks'][current_user.id]
    })

@webhook_bp.route('/delete/<int:webhook_id>', methods=['DELETE'])
@login_required
def delete_webhook(webhook_id):
    """Delete a webhook"""
    if 'webhooks' not in current_app.config or current_user.id not in current_app.config['webhooks']:
        return jsonify({'error': 'Webhook not found'}), 404
    
    webhooks = current_app.config['webhooks'][current_user.id]
    for i, webhook in enumerate(webhooks):
        if webhook['id'] == webhook_id:
            del webhooks[i]
            return jsonify({'message': 'Webhook deleted successfully'})
    
    return jsonify({'error': 'Webhook not found'}), 404

@webhook_bp.route('/test/<int:webhook_id>', methods=['POST'])
@login_required
def test_webhook(webhook_id):
    """Test a webhook by sending a test event"""
    if 'webhooks' not in current_app.config or current_user.id not in current_app.config['webhooks']:
        return jsonify({'error': 'Webhook not found'}), 404
    
    webhook = None
    for w in current_app.config['webhooks'][current_user.id]:
        if w['id'] == webhook_id:
            webhook = w
            break
    
    if not webhook:
        return jsonify({'error': 'Webhook not found'}), 404
    
    # Prepare test payload
    payload = {
        'event_type': webhook['event_type'],
        'test': True,
        'timestamp': datetime.utcnow().isoformat(),
        'user_id': current_user.id,
        'message': 'This is a test webhook event'
    }
    
    # Send webhook
    try:
        response = requests.post(
            webhook['url'],
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        return jsonify({
            'message': 'Test webhook sent',
            'status_code': response.status_code,
            'response': response.text
        })
    except Exception as e:
        return jsonify({
            'error': f'Failed to send test webhook: {str(e)}'
        }), 500

# Function to trigger webhooks (would be called from other parts of the application)
def trigger_webhook(user_id, event_type, payload):
    """
    Trigger webhooks for a specific user and event type
    
    Args:
        user_id (int): User ID
        event_type (str): Event type (e.g., 'task.created', 'task.completed')
        payload (dict): Event payload
    """
    if 'webhooks' not in current_app.config or user_id not in current_app.config['webhooks']:
        return
    
    for webhook in current_app.config['webhooks'][user_id]:
        if webhook['event_type'] == event_type and webhook['active']:
            try:
                # Add timestamp and event type to payload
                full_payload = {
                    'event_type': event_type,
                    'timestamp': datetime.utcnow().isoformat(),
                    **payload
                }
                
                # Send webhook asynchronously (in a real app, this would be a Celery task)
                requests.post(
                    webhook['url'],
                    json=full_payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
            except Exception as e:
                current_app.logger.error(f"Failed to send webhook: {str(e)}")

# Webhook endpoint for receiving external events
@webhook_bp.route('/receive', methods=['POST'])
def receive_webhook():
    """Receive webhook from external service"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate webhook signature (in a real app)
    # This is a simplified example
    
    # Process the webhook data
    event_type = data.get('event_type')
    
    if event_type == 'create_task':
        # Create a task from the webhook
        if 'task' not in data:
            return jsonify({'error': 'Task data not provided'}), 400
        
        task_data = data['task']
        user_id = task_data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID not provided'}), 400
        
        # Create the task
        task = Task(
            name=task_data.get('name', 'Webhook Task'),
            description=task_data.get('description', 'Created via webhook'),
            status='pending',
            priority=task_data.get('priority', 1),
            task_type=task_data.get('task_type', 'api'),
            user_id=user_id
        )
        
        db.session.add(task)
        db.session.commit()
        
        # Log task creation
        log_task_event(task.id, 'created', f"Task created via webhook")
        
        # Schedule the task for processing
        process_automation_task.delay(task.id)
        
        return jsonify({
            'message': 'Task created successfully',
            'task_id': task.id
        })
    
    # Default response for unhandled event types
    return jsonify({
        'message': f'Webhook received: {event_type}',
        'status': 'acknowledged'
    })
