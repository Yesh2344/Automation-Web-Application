import unittest
from app import create_app, db
from app.models.user import User, Task, TaskLog
from app.utils.task_logger import log_task_event
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost.localdomain'

class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.commit()
        
        # Create test task
        self.task = Task(
            name='Test Task',
            description='Test Description',
            status='pending',
            priority=2,
            task_type='email',
            user_id=self.user.id
        )
        db.session.add(self.task)
        db.session.commit()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_task_logger(self):
        # Test logging a task event
        log_entry = log_task_event(self.task.id, 'test_status', 'Test message')
        
        # Verify log entry was created
        self.assertIsNotNone(log_entry)
        self.assertEqual(log_entry.task_id, self.task.id)
        self.assertEqual(log_entry.status, 'test_status')
        self.assertEqual(log_entry.message, 'Test message')
        
        # Verify log entry is in database
        log_from_db = TaskLog.query.filter_by(task_id=self.task.id).first()
        self.assertIsNotNone(log_from_db)
        self.assertEqual(log_from_db.status, 'test_status')
        self.assertEqual(log_from_db.message, 'Test message')
        
    def test_task_relationship_with_logs(self):
        # Create multiple log entries
        log_task_event(self.task.id, 'status1', 'Message 1')
        log_task_event(self.task.id, 'status2', 'Message 2')
        log_task_event(self.task.id, 'status3', 'Message 3')
        
        # Verify task has logs
        self.assertEqual(self.task.logs.count(), 3)
        
        # Verify logs are ordered correctly (assuming default ordering)
        logs = self.task.logs.all()
        self.assertEqual(logs[0].message, 'Message 1')
        self.assertEqual(logs[1].message, 'Message 2')
        self.assertEqual(logs[2].message, 'Message 3')

if __name__ == '__main__':
    unittest.main()
