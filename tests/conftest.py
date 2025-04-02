import os
import sys
import pytest
from unittest.mock import MagicMock
import tempfile
import shutil

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_mail import Mail

@pytest.fixture
def app():
    """Create a Flask app for testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['MAIL_SERVER'] = 'smtp.example.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'test@example.com'
    app.config['MAIL_PASSWORD'] = 'password'
    app.config['MAIL_DEFAULT_SENDER'] = 'noreply@medicalai.com'
    return app

@pytest.fixture
def mail(app):
    """Create a Mail instance for testing"""
    mail = Mail(app)
    # Mock the send method to prevent actual emails
    mail.send = MagicMock()
    return mail

@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data"""
    # Create a temporary directory for test data
    temp_dir = tempfile.mkdtemp()
    
    # Create subdirectories
    os.makedirs(os.path.join(temp_dir, 'medications'), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, 'users'), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, 'reports'), exist_ok=True)
    
    # Return the temporary directory path
    yield temp_dir
    
    # Cleanup after the test
    shutil.rmtree(temp_dir)

@pytest.fixture
def user_manager_mock():
    """Create a mock UserManager instance"""
    user_manager = MagicMock()
    user_manager.get_user_info.return_value = {
        "name": "Test User",
        "email": "user@example.com",
    }
    user_manager.get_all_users.return_value = ["user1", "user2"]
    return user_manager 