from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from app.models.user import User, Task
from app import db
from app.tasks.automation_processor import process_automation_task
from app.utils.task_logger import log_task_event
from datetime import datetime

api_bp = Blueprint('api', __name__, url_prefix='/api')

# API Authentication decorator
def admin_required(f):
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@api_bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Get all tasks for the current user"""
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        'tasks': [task.to_dict() for task in tasks]
    })

@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    """Get a specific task"""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(task.to_dict())

@api_bp.route('/tasks', methods=['POST'])
@login_required
def create_task():
    """Create a new task"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('description'):
        return jsonify({'error': 'Name and description are required'}), 400
    
    task = Task(
        name=data['name'],
        description=data['description'],
        status='pending',
        priority=data.get('priority', 1),
        task_type=data.get('task_type', 'general'),
        user_id=current_user.id
    )
    
    db.session.add(task)
    db.session.commit()
    
    # Log task creation
    log_task_event(task.id, 'created', f"Task created via API by user {current_user.username}")
    
    # Schedule the task for processing
    process_automation_task.delay(task.id)
    
    return jsonify({
        'message': 'Task created successfully and scheduled for processing',
        'task': task.to_dict()
    }), 201

@api_bp.route('/tasks/<int:task_id>/run', methods=['POST'])
@login_required
def run_task(task_id):
    """Manually run a task"""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Only run tasks that are not already running or completed
    if task.status not in ['pending', 'failed']:
        return jsonify({'error': f'Task is already {task.status}'}), 400
    
    # Reset status to pending
    task.status = 'pending'
    db.session.commit()
    
    # Log task manual run
    log_task_event(task.id, 'manual_run', f"Task manually run via API by user {current_user.username}")
    
    # Schedule the task for processing
    process_automation_task.delay(task.id)
    
    return jsonify({
        'message': f'Task {task_id} scheduled for processing',
        'status': task.status
    })

@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """Delete a task"""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Log task deletion
    log_task_event(task.id, 'deleted', f"Task deleted by user {current_user.username}")
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({
        'message': f'Task {task_id} deleted successfully'
    })

# Admin API endpoints
@api_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users (admin only)"""
    users = User.query.all()
    return jsonify({
        'users': [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'is_admin': user.is_admin,
            'task_count': user.tasks.count()
        } for user in users]
    })

@api_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get a specific user (admin only)"""
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat() if user.created_at else None,
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'is_admin': user.is_admin,
        'tasks': [task.to_dict() for task in user.tasks]
    })

@api_bp.route('/admin/users/<int:user_id>/toggle_admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user (admin only)"""
    user = User.query.get_or_404(user_id)
    
    # Prevent removing admin status from yourself
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot change your own admin status'}), 400
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    return jsonify({
        'message': f'Admin status for user {user.username} set to {user.is_admin}',
        'is_admin': user.is_admin
    })
