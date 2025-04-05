from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.user import Task
from app import db
from app.tasks.automation_processor import process_automation_task
from app.routes.forms import TaskForm
from app.utils.task_logger import log_task_event

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    if current_user.is_authenticated:
        tasks = Task.query.filter_by(user_id=current_user.id).all()
    else:
        tasks = []
    return render_template('index.html', title='Home', tasks=tasks)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', title='Dashboard', tasks=tasks)

@main_bp.route('/task/new', methods=['GET', 'POST'])
@login_required
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            name=form.name.data,
            description=form.description.data,
            status='pending',
            priority=form.priority.data,
            task_type=form.task_type.data,
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        
        # Log task creation
        log_task_event(task.id, 'created', f"Task created by user {current_user.username}")
        
        # Schedule the task for automation
        process_automation_task.delay(task.id)
        
        flash('Task created successfully!')
        return redirect(url_for('main.dashboard'))
    return render_template('task_form.html', title='New Task', form=form)

@main_bp.route('/task/<int:task_id>')
@login_required
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to view this task.')
        return redirect(url_for('main.dashboard'))
    
    # Get task logs
    logs = task.logs.order_by(Task.logs.property.mapper.class_.timestamp.desc()).all()
    
    return render_template('task_detail.html', title=task.name, task=task, logs=logs)

@main_bp.route('/task/<int:task_id>/run', methods=['POST'])
@login_required
def run_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to run this task.')
        return redirect(url_for('main.dashboard'))
    
    # Only run tasks that are not already running or completed
    if task.status not in ['pending', 'failed']:
        flash(f'Task is already {task.status}')
        return redirect(url_for('main.task_detail', task_id=task.id))
    
    # Reset status to pending
    task.status = 'pending'
    db.session.commit()
    
    # Log task manual run
    log_task_event(task.id, 'manual_run', f"Task manually run by user {current_user.username}")
    
    # Schedule the task for processing
    process_automation_task.delay(task.id)
    
    flash('Task scheduled for processing')
    return redirect(url_for('main.task_detail', task_id=task.id))
