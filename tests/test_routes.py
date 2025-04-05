import unittest
from flask import url_for
from app import create_app, db
from app.models.user import User, Task
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost.localdomain'

class AuthRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_register(self):
        with self.app.test_request_context():
            response = self.client.post(
                url_for('auth.register'),
                data={
                    'username': 'testuser',
                    'email': 'test@example.com',
                    'password': 'password123',
                    'password2': 'password123'
                },
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@example.com')
            
    def test_login_logout(self):
        # Create a user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        with self.app.test_request_context():
            # Test login
            response = self.client.post(
                url_for('auth.login'),
                data={
                    'username': 'testuser',
                    'password': 'password123',
                    'remember_me': False
                },
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            
            # Test logout
            response = self.client.get(
                url_for('auth.logout'),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            
    def test_invalid_login(self):
        with self.app.test_request_context():
            response = self.client.post(
                url_for('auth.login'),
                data={
                    'username': 'nonexistent',
                    'password': 'wrongpassword',
                    'remember_me': False
                },
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Invalid username or password', response.data)

class TaskRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Create test user
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()
        
        # Log in
        with self.app.test_request_context():
            self.client.post(
                url_for('auth.login'),
                data={
                    'username': 'testuser',
                    'password': 'password123',
                    'remember_me': False
                }
            )
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_create_task(self):
        with self.app.test_request_context():
            response = self.client.post(
                url_for('main.new_task'),
                data={
                    'name': 'Test Task',
                    'description': 'Test Description',
                    'priority': 2,
                    'task_type': 'email'
                },
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            task = Task.query.filter_by(name='Test Task').first()
            self.assertIsNotNone(task)
            self.assertEqual(task.description, 'Test Description')
            self.assertEqual(task.priority, 2)
            self.assertEqual(task.task_type, 'email')
            
    def test_view_task(self):
        # Create a task
        task = Task(
            name='Test Task',
            description='Test Description',
            status='pending',
            priority=2,
            task_type='email',
            user_id=self.user.id
        )
        db.session.add(task)
        db.session.commit()
        
        with self.app.test_request_context():
            response = self.client.get(
                url_for('main.task_detail', task_id=task.id),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Test Task', response.data)
            self.assertIn(b'Test Description', response.data)

class APIRoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Create test user
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()
        
        # Log in
        with self.app.test_request_context():
            self.client.post(
                url_for('auth.login'),
                data={
                    'username': 'testuser',
                    'password': 'password123',
                    'remember_me': False
                }
            )
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_get_tasks_api(self):
        # Create a task
        task = Task(
            name='API Test Task',
            description='API Test Description',
            status='pending',
            priority=2,
            task_type='api',
            user_id=self.user.id
        )
        db.session.add(task)
        db.session.commit()
        
        with self.app.test_request_context():
            response = self.client.get(
                url_for('api.get_tasks'),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            json_data = response.get_json()
            self.assertIn('tasks', json_data)
            self.assertEqual(len(json_data['tasks']), 1)
            self.assertEqual(json_data['tasks'][0]['name'], 'API Test Task')
            
    def test_create_task_api(self):
        with self.app.test_request_context():
            response = self.client.post(
                url_for('api.create_task'),
                json={
                    'name': 'API Created Task',
                    'description': 'Created via API',
                    'priority': 3,
                    'task_type': 'api'
                },
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 201)
            json_data = response.get_json()
            self.assertIn('task', json_data)
            self.assertEqual(json_data['task']['name'], 'API Created Task')
            
            # Verify task was created in database
            task = Task.query.filter_by(name='API Created Task').first()
            self.assertIsNotNone(task)
            self.assertEqual(task.description, 'Created via API')
            self.assertEqual(task.priority, 3)
            self.assertEqual(task.task_type, 'api')

if __name__ == '__main__':
    unittest.main()
