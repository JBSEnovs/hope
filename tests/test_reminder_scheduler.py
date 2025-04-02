import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.reminder_scheduler import ReminderScheduler
from agents.email_service import EmailService
from agents.medication_reminder import MedicationReminder

class TestReminderScheduler:
    """Tests for the ReminderScheduler class"""
    
    @pytest.fixture
    def email_service_mock(self):
        """Create a mock EmailService instance"""
        email_service = MagicMock(spec=EmailService)
        email_service.send_medication_reminder.return_value = True
        email_service.send_adherence_report.return_value = True
        return email_service
    
    @pytest.fixture
    def medication_reminder_mock(self):
        """Create a mock MedicationReminder instance"""
        medication_reminder = MagicMock(spec=MedicationReminder)
        # Sample user data for testing
        medication_reminder.get_all_users.return_value = [
            "user1", "user2"
        ]
        # Sample medication data for testing
        medication_reminder.get_due_medications.return_value = [
            {
                "id": "med123",
                "name": "Test Medication",
                "dosage": "10mg",
                "frequency": "daily",
                "start_date": datetime.now().isoformat(),
                "end_date": None,
                "notes": "Take with food"
            }
        ]
        medication_reminder.get_user_medications.return_value = [
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
            }
        ]
        medication_reminder.get_adherence_rate.return_value = 80.0
        medication_reminder.get_user_info.return_value = {
            "name": "Test User",
            "email": "user@example.com",
        }
        return medication_reminder
    
    @pytest.fixture
    def user_manager_mock(self):
        """Create a mock UserManager instance"""
        user_manager = MagicMock()
        user_manager.get_user_info.return_value = {
            "name": "Test User",
            "email": "user@example.com",
        }
        return user_manager
    
    @pytest.fixture
    def scheduler(self, email_service_mock, medication_reminder_mock, user_manager_mock):
        """Create a ReminderScheduler instance for testing"""
        scheduler = ReminderScheduler()
        scheduler.email_service = email_service_mock
        scheduler.medication_reminder = medication_reminder_mock
        scheduler.user_manager = user_manager_mock
        # Mock the scheduler to prevent it from actually running
        scheduler.scheduler = MagicMock()
        return scheduler
    
    def test_initialization(self, scheduler):
        """Test that the ReminderScheduler initializes correctly"""
        assert scheduler is not None
        assert scheduler.email_service is not None
        assert scheduler.medication_reminder is not None
        assert scheduler.user_manager is not None
        assert scheduler.scheduler is not None
    
    def test_start(self, scheduler):
        """Test starting the scheduler"""
        scheduler.start()
        # Verify the scheduler was started
        scheduler.scheduler.start.assert_called_once()
    
    def test_shutdown(self, scheduler):
        """Test shutting down the scheduler"""
        scheduler.shutdown()
        # Verify the scheduler was shut down
        scheduler.scheduler.shutdown.assert_called_once()
    
    def test_setup_scheduled_jobs(self, scheduler):
        """Test setting up scheduled jobs"""
        scheduler._setup_scheduled_jobs()
        # Verify jobs were added to the scheduler
        assert scheduler.scheduler.add_job.call_count >= 4
    
    def test_send_daily_reminders(self, scheduler):
        """Test sending daily medication reminders"""
        # Call the method
        scheduler._send_daily_reminders()
        
        # Verify the medication reminder was called to get all users
        scheduler.medication_reminder.get_all_users.assert_called_once()
        
        # Verify due medications were fetched for each user
        expected_calls = len(scheduler.medication_reminder.get_all_users())
        assert scheduler.medication_reminder.get_due_medications.call_count == expected_calls
        
        # Verify user info was retrieved
        assert scheduler.user_manager.get_user_info.call_count > 0
        
        # Verify email reminders were sent
        assert scheduler.email_service.send_medication_reminder.call_count > 0
    
    def test_send_weekly_adherence_reports(self, scheduler):
        """Test sending weekly adherence reports"""
        # Call the method
        scheduler._send_weekly_adherence_reports()
        
        # Verify the medication reminder was called to get all users
        scheduler.medication_reminder.get_all_users.assert_called_once()
        
        # Verify medications were fetched for each user
        expected_calls = len(scheduler.medication_reminder.get_all_users())
        assert scheduler.medication_reminder.get_user_medications.call_count == expected_calls
        
        # Verify user info was retrieved
        assert scheduler.user_manager.get_user_info.call_count > 0
        
        # Verify adherence reports were sent
        assert scheduler.email_service.send_adherence_report.call_count > 0
        
        # Verify correct report type was used
        report_type_arg = scheduler.email_service.send_adherence_report.call_args[1]['report_type']
        assert report_type_arg == "weekly"
    
    def test_send_monthly_adherence_reports(self, scheduler):
        """Test sending monthly adherence reports"""
        # Call the method
        scheduler._send_monthly_adherence_reports()
        
        # Verify the medication reminder was called to get all users
        scheduler.medication_reminder.get_all_users.assert_called_once()
        
        # Verify medications were fetched for each user
        expected_calls = len(scheduler.medication_reminder.get_all_users())
        assert scheduler.medication_reminder.get_user_medications.call_count == expected_calls
        
        # Verify user info was retrieved
        assert scheduler.user_manager.get_user_info.call_count > 0
        
        # Verify adherence reports were sent
        assert scheduler.email_service.send_adherence_report.call_count > 0
        
        # Verify correct report type was used
        report_type_arg = scheduler.email_service.send_adherence_report.call_args[1]['report_type']
        assert report_type_arg == "monthly"
    
    def test_check_missed_doses(self, scheduler):
        """Test checking for missed medication doses"""
        # Mock some missed medications
        scheduler.medication_reminder.get_missed_doses.return_value = [
            {
                "user_id": "user1",
                "medication_id": "med123",
                "name": "Test Medication",
                "scheduled_time": "2023-04-01T10:00:00"
            }
        ]
        
        # Call the method
        scheduler._check_missed_doses()
        
        # Verify missed doses were checked
        scheduler.medication_reminder.get_missed_doses.assert_called_once()
        
        # Verify each missed dose was recorded
        expected_calls = len(scheduler.medication_reminder.get_missed_doses())
        assert scheduler.medication_reminder.record_medication_missed.call_count == expected_calls 