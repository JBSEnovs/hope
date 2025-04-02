import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.email_service import EmailService
from flask import Flask
from flask_mail import Mail, Message

class TestEmailService:
    """Tests for the EmailService class"""
    
    @pytest.fixture
    def app(self):
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
    def mail(self, app):
        """Create a Mail instance for testing"""
        return Mail(app)
    
    @pytest.fixture
    def email_service(self, app, mail):
        """Create an EmailService instance for testing"""
        # Mock the mail.send method to prevent actual emails
        mail.send = MagicMock()
        
        # Create and initialize the EmailService
        service = EmailService()
        service.init_app(app)
        service.mail = mail
        
        return service
    
    def test_initialization(self, email_service):
        """Test that the EmailService initializes correctly"""
        assert email_service is not None
        assert email_service.mail is not None
        assert email_service.default_sender == 'noreply@medicalai.com'
    
    @patch('agents.email_service.render_template_string')
    def test_send_email(self, mock_render, email_service):
        """Test sending an email"""
        # Mock the render_template_string function
        mock_render.return_value = "<p>HTML Content</p>"
        
        # Send an email
        result = email_service.send_email(
            recipient="user@example.com",
            subject="Test Email",
            html_body="<p>HTML Content</p>",
            text_body="Text Content"
        )
        
        # Verify the email was sent
        assert result is True
        email_service.mail.send.assert_called_once()
        
        # Verify the message details
        call_args = email_service.mail.send.call_args[0][0]
        assert isinstance(call_args, Message)
        assert call_args.subject == "Test Email"
        assert call_args.recipients == ["user@example.com"]
        assert call_args.html == "<p>HTML Content</p>"
        assert call_args.body == "Text Content"
    
    @patch('agents.email_service.render_template_string')
    def test_send_medication_reminder(self, mock_render, email_service):
        """Test sending a medication reminder"""
        # Mock the render_template_string function
        mock_render.return_value = "<p>Medication Reminder</p>"
        
        # Create a test medication
        medication = {
            "id": "med123",
            "name": "Test Medication",
            "dosage": "10mg",
            "frequency": "daily",
            "start_date": datetime.now().isoformat(),
            "end_date": None,
            "notes": "Take with food"
        }
        
        # Send a medication reminder
        result = email_service.send_medication_reminder(
            recipient="user@example.com",
            user_name="Test User",
            medication=medication
        )
        
        # Verify the reminder was sent
        assert result is True
        email_service.mail.send.assert_called_once()
        
        # Verify the message details
        call_args = email_service.mail.send.call_args[0][0]
        assert isinstance(call_args, Message)
        assert "Reminder" in call_args.subject
        assert call_args.recipients == ["user@example.com"]
    
    @patch('agents.email_service.render_template_string')
    def test_send_adherence_report(self, mock_render, email_service):
        """Test sending an adherence report"""
        # Mock the render_template_string function
        mock_render.return_value = "<p>Adherence Report</p>"
        
        # Create test medications
        medications = [
            {
                "id": "med123",
                "name": "Test Medication 1",
                "dosage": "10mg",
                "frequency": "daily",
                "adherence": {
                    "total_doses": 10,
                    "taken_doses": 8,
                    "missed_doses": 2,
                    "rate": 80.0
                }
            },
            {
                "id": "med456",
                "name": "Test Medication 2",
                "dosage": "20mg",
                "frequency": "weekly",
                "adherence": {
                    "total_doses": 5,
                    "taken_doses": 5,
                    "missed_doses": 0,
                    "rate": 100.0
                }
            }
        ]
        
        # Send an adherence report
        result = email_service.send_adherence_report(
            recipient="user@example.com",
            user_name="Test User",
            medications=medications,
            report_type="weekly"
        )
        
        # Verify the report was sent
        assert result is True
        email_service.mail.send.assert_called_once()
        
        # Verify the message details
        call_args = email_service.mail.send.call_args[0][0]
        assert isinstance(call_args, Message)
        assert "Weekly" in call_args.subject
        assert "Adherence" in call_args.subject
        assert call_args.recipients == ["user@example.com"]
    
    def test_generate_adherence_feedback(self, email_service):
        """Test generating adherence feedback based on rate"""
        # Test perfect adherence
        feedback = email_service._generate_adherence_feedback(100)
        assert "excellent" in feedback.lower()
        
        # Test good adherence
        feedback = email_service._generate_adherence_feedback(85)
        assert "good" in feedback.lower()
        
        # Test moderate adherence
        feedback = email_service._generate_adherence_feedback(70)
        assert "improve" in feedback.lower()
        
        # Test poor adherence
        feedback = email_service._generate_adherence_feedback(50)
        assert "concerned" in feedback.lower()
        
        # Test very poor adherence
        feedback = email_service._generate_adherence_feedback(30)
        assert "important" in feedback.lower() and "discuss" in feedback.lower() 