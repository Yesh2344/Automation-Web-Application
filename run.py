from app import create_app, db
from app.models.user import User, Task

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Task': Task}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
