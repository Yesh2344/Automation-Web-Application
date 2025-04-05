from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from app.models.user import Task
from app import db
import csv
import io
import json
from datetime import datetime
import os

export_bp = Blueprint('export', __name__, url_prefix='/export')

@export_bp.route('/')
@login_required
def index():
    """Export dashboard view"""
    return render_template('export/index.html', title='Export Data')

@export_bp.route('/tasks/csv')
@login_required
def export_tasks_csv():
    """Export tasks as CSV"""
    # Get tasks for current user
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    
    # Create in-memory file
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'Name', 'Description', 'Status', 'Type', 'Priority', 
                    'Created', 'Updated', 'Completed'])
    
    # Write data
    for task in tasks:
        writer.writerow([
            task.id,
            task.name,
            task.description,
            task.status,
            task.task_type,
            task.priority,
            task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else '',
            task.updated_at.strftime('%Y-%m-%d %H:%M:%S') if task.updated_at else '',
            task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task.completed_at else ''
        ])
    
    # Prepare response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'tasks_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@export_bp.route('/tasks/json')
@login_required
def export_tasks_json():
    """Export tasks as JSON"""
    # Get tasks for current user
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    
    # Convert to dict
    tasks_data = [task.to_dict() for task in tasks]
    
    # Prepare response
    return jsonify({
        'tasks': tasks_data,
        'exported_at': datetime.now().isoformat(),
        'user': current_user.username
    })

@export_bp.route('/import', methods=['POST'])
@login_required
def import_tasks():
    """Import tasks from JSON"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not file.filename.endswith('.json'):
        return jsonify({'error': 'Only JSON files are supported'}), 400
    
    try:
        # Read and parse JSON
        content = file.read().decode('utf-8')
        data = json.loads(content)
        
        if 'tasks' not in data:
            return jsonify({'error': 'Invalid JSON format: missing tasks array'}), 400
        
        # Import tasks
        imported_count = 0
        for task_data in data['tasks']:
            # Create new task
            task = Task(
                name=task_data.get('name', 'Imported Task'),
                description=task_data.get('description', ''),
                status='pending',  # Always start as pending
                priority=task_data.get('priority', 1),
                task_type=task_data.get('task_type', 'general'),
                user_id=current_user.id
            )
            db.session.add(task)
            imported_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully imported {imported_count} tasks',
            'imported_count': imported_count
        })
        
    except Exception as e:
        return jsonify({'error': f'Error importing tasks: {str(e)}'}), 400
