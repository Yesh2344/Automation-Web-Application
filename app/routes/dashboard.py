from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models.user import Task
from app import db
import json
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard view"""
    return render_template('dashboard/index.html', title='Analytics Dashboard')

@dashboard_bp.route('/api/task-stats')
@login_required
def task_stats():
    """API endpoint for task statistics"""
    # Count tasks by status
    status_counts = db.session.query(
        Task.status, func.count(Task.id)
    ).filter(Task.user_id == current_user.id).group_by(Task.status).all()
    
    status_data = {status: count for status, count in status_counts}
    
    # Count tasks by type
    type_counts = db.session.query(
        Task.task_type, func.count(Task.id)
    ).filter(Task.user_id == current_user.id).group_by(Task.task_type).all()
    
    type_data = {task_type: count for task_type, count in type_counts}
    
    # Count tasks by priority
    priority_counts = db.session.query(
        Task.priority, func.count(Task.id)
    ).filter(Task.user_id == current_user.id).group_by(Task.priority).all()
    
    priority_labels = {1: 'Low', 2: 'Medium', 3: 'High'}
    priority_data = {priority_labels.get(priority, str(priority)): count 
                    for priority, count in priority_counts}
    
    # Get task completion trend (last 7 days)
    today = datetime.utcnow().date()
    date_labels = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]
    
    completion_trend = []
    for date_str in date_labels:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        next_day = date_obj + timedelta(days=1)
        
        # Count completed tasks for this day
        count = Task.query.filter(
            Task.user_id == current_user.id,
            Task.status == 'completed',
            Task.completed_at >= date_obj,
            Task.completed_at < next_day
        ).count()
        
        completion_trend.append(count)
    
    return jsonify({
        'status_data': status_data,
        'type_data': type_data,
        'priority_data': priority_data,
        'completion_trend': {
            'labels': date_labels,
            'data': completion_trend
        }
    })

@dashboard_bp.route('/api/recent-tasks')
@login_required
def recent_tasks():
    """API endpoint for recent tasks"""
    tasks = Task.query.filter_by(
        user_id=current_user.id
    ).order_by(Task.created_at.desc()).limit(5).all()
    
    return jsonify({
        'tasks': [task.to_dict() for task in tasks]
    })
