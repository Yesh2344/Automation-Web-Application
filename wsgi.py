from app import create_app, db, celery
from app.models.user import User, Task

app = create_app()
celery_app = celery

@app.cli.command("init-db")
def init_db():
    """Initialize the database with tables."""
    db.create_all()
    print("Database initialized.")

@app.cli.command("create-admin")
def create_admin():
    """Create an admin user."""
    admin = User(username="admin", email="admin@example.com")
    admin.set_password("adminpassword")
    db.session.add(admin)
    db.session.commit()
    print("Admin user created.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
