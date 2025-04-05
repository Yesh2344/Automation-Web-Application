# Automation Web App - Installation Guide

This guide will help you set up and run the Automation Web App on your local machine.

## Prerequisites

- Python 3.10 or higher
- Redis server (for Celery task queue)

## Installation Steps

1. **Clone the repository or extract the provided files**

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   The `.env` file is already included with default development settings.
   For production, you should modify the SECRET_KEY and other settings.

5. **Initialize the database**:
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Create an admin user**:
   ```bash
   flask create-admin
   ```
   This will create a user with:
   - Username: admin
   - Email: admin@example.com
   - Password: adminpassword

7. **Start the application**:
   ```bash
   flask run
   ```

8. **In a separate terminal, start the Celery worker**:
   ```bash
   celery -A app.celery worker --loglevel=info
   ```

9. **Access the application**:
   Open your browser and navigate to http://127.0.0.1:5000

## Features Overview

- **User Authentication**: Register, login, profile management
- **Task Management**: Create and manage automated tasks
- **Data Visualization**: Interactive dashboard with charts
- **Export/Import**: Export tasks to CSV/JSON and import from JSON
- **Webhook Integration**: Connect with external services
- **Notification System**: Configure email notifications

## Testing

Run the tests with:
```bash
pytest
```

## Additional Documentation

For more detailed information, please refer to the README.md file.
