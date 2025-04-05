import unittest
from app import create_app, db
from app.models.user import User, Task
from config import Config
import os
import tempfile

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost.localdomain'

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_password_hashing(self):
        u = User(username='test', email='test@example.com')
        u.set_password('password')
        self.assertTrue(u.check_password('password'))
        self.assertFalse(u.check_password('wrong_password'))
        
    def test_user_creation(self):
        u = User(username='test', email='test@example.com')
        u.set_password('password')
        db.session.add(u)
        db.session.commit()
        
        user = User.query.filter_by(username='test').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        
    def test_task_relationship(self):
        u = User(username='test', email='test@example.com')
        u.set_password('password')
        db.session.add(u)
        db.session.commit()
        
        t = Task(name='Test Task', description='Test Description', user_id=u.id)
        db.session.add(t)
        db.session.commit()
        
        self.assertEqual(u.tasks.count(), 1)
        self.assertEqual(u.tasks.first().name, 'Test Task')
        
class TaskModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        self.user = User(username='test', email='test@example.com')
        self.user.set_password('password')
        db.session.add(self.user)
        db.session.commit()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_task_creation(self):
        t = Task(
            name='Test Task', 
            description='Test Description',
            status='pending',
            priority=2,
            task_type='email',
            user_id=self.user.id
        )
        db.session.add(t)
        db.session.commit()
        
        task = Task.query.filter_by(name='Test Task').first()
        self.assertIsNotNone(task)
        self.assertEqual(task.description, 'Test Description')
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.priority, 2)
        self.assertEqual(task.task_type, 'email')
        
    def test_task_to_dict(self):
        t = Task(
            name='Test Task', 
            description='Test Description',
            status='pending',
            priority=2,
            task_type='email',
            user_id=self.user.id
        )
        db.session.add(t)
        db.session.commit()
        
        task_dict = t.to_dict()
        self.assertEqual(task_dict['name'], 'Test Task')
        self.assertEqual(task_dict['description'], 'Test Description')
        self.assertEqual(task_dict['status'], 'pending')
        self.assertEqual(task_dict['priority'], 2)
        self.assertEqual(task_dict['task_type'], 'email')
        self.assertEqual(task_dict['user_id'], self.user.id)

if __name__ == '__main__':
    unittest.main()
