import os
import sys
import pytest
import json
from datetime import datetime, timedelta
import tempfile
import shutil

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.medication_reminder import MedicationReminder

class TestMedicationReminder:
    """Tests for the MedicationReminder class"""
    
    @pytest.fixture
    def medication_reminder(self):
        """Create a MedicationReminder instance with a temporary data directory"""
        # Create a temporary directory for test data
        temp_dir = tempfile.mkdtemp()
        temp_data_dir = os.path.join(temp_dir, 'medications')
        os.makedirs(temp_data_dir, exist_ok=True)
        
        # Create the MedicationReminder instance
        reminder = MedicationReminder()
        reminder.data_dir = temp_data_dir
        
        # Return the instance
        yield reminder
        
        # Cleanup after the test
        shutil.rmtree(temp_dir)
    
    def test_initialization(self, medication_reminder):
        """Test that the MedicationReminder initializes correctly"""
        assert medication_reminder is not None
        assert medication_reminder.reminders == {}
        assert os.path.exists(medication_reminder.data_dir)
    
    def test_add_medication(self, medication_reminder):
        """Test adding a new medication"""
        user_id = "test_user_1"
        medication = medication_reminder.add_medication(
            user_id=user_id,
            name="Test Medication",
            dosage="10mg",
            frequency="daily",
            start_date=datetime.now().isoformat(),
            end_date=None,
            notes="Test notes"
        )
        
        # Verify medication was added to the reminders dict
        assert user_id in medication_reminder.reminders
        assert len(medication_reminder.reminders[user_id]) == 1
        assert medication_reminder.reminders[user_id][0]["name"] == "Test Medication"
        assert medication_reminder.reminders[user_id][0]["dosage"] == "10mg"
        assert medication_reminder.reminders[user_id][0]["frequency"] == "daily"
        assert medication_reminder.reminders[user_id][0]["notes"] == "Test notes"
        
        # Verify the medication file was created
        file_path = os.path.join(medication_reminder.data_dir, f"{user_id}.json")
        assert os.path.exists(file_path)
        
        # Verify the file contains the medication data
        with open(file_path, 'r') as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]["name"] == "Test Medication"
    
    def test_get_user_medications(self, medication_reminder):
        """Test retrieving user medications"""
        user_id = "test_user_2"
        
        # Add a medication
        medication_reminder.add_medication(
            user_id=user_id,
            name="Test Medication 1",
            dosage="10mg",
            frequency="daily",
            start_date=datetime.now().isoformat()
        )
        
        # Add another medication
        medication_reminder.add_medication(
            user_id=user_id,
            name="Test Medication 2",
            dosage="20mg",
            frequency="weekly",
            start_date=datetime.now().isoformat()
        )
        
        # Get medications
        medications = medication_reminder.get_user_medications(user_id)
        
        # Verify both medications are retrieved
        assert len(medications) == 2
        assert medications[0]["name"] == "Test Medication 1"
        assert medications[1]["name"] == "Test Medication 2"
    
    def test_delete_medication(self, medication_reminder):
        """Test deleting a medication"""
        user_id = "test_user_3"
        
        # Add a medication
        medication = medication_reminder.add_medication(
            user_id=user_id,
            name="Test Medication",
            dosage="10mg",
            frequency="daily",
            start_date=datetime.now().isoformat()
        )
        
        # Verify medication was added
        assert len(medication_reminder.get_user_medications(user_id)) == 1
        
        # Delete the medication
        result = medication_reminder.delete_medication(user_id, medication["id"])
        
        # Verify deletion was successful
        assert result is True
        assert len(medication_reminder.get_user_medications(user_id)) == 0
    
    def test_record_medication_taken(self, medication_reminder):
        """Test recording a medication as taken"""
        user_id = "test_user_4"
        
        # Add a medication
        medication = medication_reminder.add_medication(
            user_id=user_id,
            name="Test Medication",
            dosage="10mg",
            frequency="daily",
            start_date=datetime.now().isoformat()
        )
        
        # Record as taken
        result = medication_reminder.record_medication_taken(user_id, medication["id"])
        
        # Verify recording was successful
        assert result is True
        
        # Verify adherence stats were updated
        medications = medication_reminder.get_user_medications(user_id)
        assert medications[0]["adherence"]["total_doses"] == 1
        assert medications[0]["adherence"]["taken_doses"] == 1
        assert medications[0]["adherence"]["missed_doses"] == 0
        assert len(medications[0]["adherence"]["history"]) == 1
        assert medications[0]["adherence"]["history"][0]["status"] == "taken"
    
    def test_record_medication_missed(self, medication_reminder):
        """Test recording a medication as missed"""
        user_id = "test_user_5"
        
        # Add a medication
        medication = medication_reminder.add_medication(
            user_id=user_id,
            name="Test Medication",
            dosage="10mg",
            frequency="daily",
            start_date=datetime.now().isoformat()
        )
        
        # Record as missed
        result = medication_reminder.record_medication_missed(user_id, medication["id"])
        
        # Verify recording was successful
        assert result is True
        
        # Verify adherence stats were updated
        medications = medication_reminder.get_user_medications(user_id)
        assert medications[0]["adherence"]["total_doses"] == 1
        assert medications[0]["adherence"]["taken_doses"] == 0
        assert medications[0]["adherence"]["missed_doses"] == 1
        assert len(medications[0]["adherence"]["history"]) == 1
        assert medications[0]["adherence"]["history"][0]["status"] == "missed"
    
    def test_get_adherence_rate(self, medication_reminder):
        """Test calculating adherence rate"""
        user_id = "test_user_6"
        
        # Add a medication
        medication = medication_reminder.add_medication(
            user_id=user_id,
            name="Test Medication",
            dosage="10mg",
            frequency="daily",
            start_date=datetime.now().isoformat()
        )
        
        # Record as taken twice and missed once
        medication_reminder.record_medication_taken(user_id, medication["id"])
        medication_reminder.record_medication_taken(user_id, medication["id"])
        medication_reminder.record_medication_missed(user_id, medication["id"])
        
        # Get adherence rate
        adherence_rate = medication_reminder.get_adherence_rate(user_id)
        
        # Verify adherence rate calculation
        assert adherence_rate == 66.7  # (2/3) * 100 = 66.67, rounded to 66.7
    
    def test_get_due_medications(self, medication_reminder):
        """Test getting medications due in the next window"""
        user_id = "test_user_7"
        
        # Add a medication with a start date in the past
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        current_med = medication_reminder.add_medication(
            user_id=user_id,
            name="Current Medication",
            dosage="10mg",
            frequency="daily",
            start_date=past_date
        )
        
        # Add a medication with a start date in the future
        future_date = (datetime.now() + timedelta(days=7)).isoformat()
        future_med = medication_reminder.add_medication(
            user_id=user_id,
            name="Future Medication",
            dosage="20mg",
            frequency="weekly",
            start_date=future_date
        )
        
        # Get due medications in the next 24 hours
        due_medications = medication_reminder.get_due_medications(user_id, hours_window=24)
        
        # Verify only the current medication is returned
        assert len(due_medications) == 1
        assert due_medications[0]["name"] == "Current Medication"
    
    def test_generate_medication_report(self, medication_reminder):
        """Test generating a medication report"""
        user_id = "test_user_8"
        
        # Add a medication
        medication = medication_reminder.add_medication(
            user_id=user_id,
            name="Test Medication",
            dosage="10mg",
            frequency="daily",
            start_date=datetime.now().isoformat()
        )
        
        # Record some doses
        medication_reminder.record_medication_taken(user_id, medication["id"])
        medication_reminder.record_medication_taken(user_id, medication["id"])
        
        # Generate the report
        report_bytes = medication_reminder.generate_medication_report(user_id)
        
        # Verify report was generated
        assert report_bytes is not None
        assert isinstance(report_bytes, bytes)
        assert len(report_bytes) > 0 