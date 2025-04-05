from flask.cli import FlaskGroup
from app import create_app, db
from app.models.user import User

app = create_app()
cli = FlaskGroup(create_app=lambda: app)

@cli.command("create-admin")
def create_admin():
    """Create an admin user"""
    username = input("Enter admin username (default: admin): ") or "admin"
    email = input("Enter admin email (default: admin@example.com): ") or "admin@example.com"
    password = input("Enter admin password (default: adminpassword): ") or "adminpassword"
    
    user = User(username=username, email=email, is_admin=True)
    user.set_password(password)
    
    with app.app_context():
        db.session.add(user)
        db.session.commit()
        print(f"Admin user '{username}' created successfully!")

if __name__ == "__main__":
    cli()
