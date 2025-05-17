# Automation Web App Documentation

## Overview

The Automation Web App is a powerful web application built with Flask and Celery that allows users to create, manage, and automate tasks. The application features a comprehensive user authentication system, task management with priority and type classification, automated task processing, and advanced features like data visualization, export/import functionality, webhook integration, and notification system.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Features](#features)
4. [API Reference](#api-reference)
5. [Development Guide](#development-guide)
6. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites

- Python 3.10 or higher
- Redis server (for Celery task queue)
- SQLite (default) or other database supported by SQLAlchemy

### Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd automation-web-app
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root with the following content:
   ```
   FLASK_APP=app
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-replace-in-production
   DATABASE_URL=sqlite:///app.db
   REDIS_URL=redis://localhost:6379/0
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

5. Initialize the database:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Create an admin user:
   ```
   flask create-admin
   ```

7. Start the application:
   ```
   flask run
   ```

8. In a separate terminal, start the Celery worker:
   ```
   celery -A app.celery worker --loglevel=info
   ```

## Configuration

The application can be configured using environment variables or by modifying the `config.py` file. The following configuration options are available:

- `SECRET_KEY`: Secret key for session security
- `SQLALCHEMY_DATABASE_URI`: Database connection URL
- `REDIS_URL`: Redis server URL
- `CELERY_BROKER_URL`: Celery broker URL
- `CELERY_RESULT_BACKEND`: Celery result backend URL

## Features

### User Authentication

- User registration and login
- Profile management
- Admin dashboard for user management
- Role-based access control

### Task Management

- Create, view, and manage tasks
- Task priority levels (Low, Medium, High)
- Task types (General, Email, File, API)
- Task status tracking (Pending, Processing, Completed, Failed)
- Task execution history and logs

### Automation

- Asynchronous task processing with Celery
- Scheduled tasks with periodic execution
- Task logging and monitoring
- Error handling and retry mechanisms

### Data Visualization

- Task status distribution charts
- Task type distribution charts
- Task priority distribution charts
- Task completion trend analysis
- Interactive dashboard with real-time updates

### Export/Import

- Export tasks to CSV format
- Export tasks to JSON format
- Import tasks from JSON format
- Data format documentation and examples

### Webhook Integration

- Register webhooks for task events
- Test webhook functionality
- Receive external events via webhooks
- Create tasks from external services

### Notification System

- Email notification preferences
- Notification events (Task Completed, Task Failed, Daily Summary)
- Test notification functionality

## API Reference

The application provides a RESTful API for programmatic access to its functionality.

### Authentication

All API endpoints except for authentication endpoints require authentication.

### Task Endpoints

- `GET /api/tasks`: Get all tasks for the current user
- `GET /api/tasks/<task_id>`: Get a specific task
- `POST /api/tasks`: Create a new task
- `POST /api/tasks/<task_id>/run`: Manually run a task
- `DELETE /api/tasks/<task_id>`: Delete a task

### Admin Endpoints

- `GET /api/admin/users`: Get all users (admin only)
- `GET /api/admin/users/<user_id>`: Get a specific user (admin only)
- `POST /api/admin/users/<user_id>/toggle_admin`: Toggle admin status for a user (admin only)

### Webhook Endpoints

- `POST /webhook/receive`: Receive webhook from external service

## Development Guide

### Project Structure

```
automation-web-app/
├── app/
│   ├── auth/
│   ├── models/
│   ├── routes/
│   ├── static/
│   ├── tasks/
│   ├── templates/
│   ├── utils/
│   └── __init__.py
├── migrations/
├── tests/
├── .env
├── app.py
├── config.py
├── manage.py
├── requirements.txt
├── run.py
└── wsgi.py
```

### Adding New Features

To add a new feature to the application:

1. Create a new module in the appropriate directory
2. Update the application factory in `app/__init__.py` to include the new module
3. Add routes, templates, and static files as needed
4. Update the documentation

### Running Tests

```
pytest
```

## Troubleshooting

### Common Issues

- **Celery worker not processing tasks**: Ensure Redis server is running and the Celery worker is started
- **Database migration errors**: Check the database connection and ensure the database is accessible
- **Authentication issues**: Clear browser cookies and try logging in again

### Logging

The application logs are stored in the `logs` directory. Check the logs for detailed error information.

### Support

For additional support, please contact the development team.
"# Automation-Web-Application" 

## Copyrights

@Yeswanth Soma All Copyrights Reserved


## Contact

Email:
