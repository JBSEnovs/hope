import os
import json
import uuid
from datetime import datetime, timedelta

class MedicationReminder:
    """
    Manages medication schedules and reminders for users.
    """
    
    def __init__(self):
        """Initialize the medication reminder system"""
        self.data_dir = os.path.join('data', 'medications')
        os.makedirs(self.data_dir, exist_ok=True)
        self.reminders = {}
        self.load_reminders()
    
    def load_reminders(self):
        """Load all user medication reminders from storage"""
        try:
            # Get all user medication files
            user_files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
            
            for file in user_files:
                user_id = file.replace('.json', '')
                file_path = os.path.join(self.data_dir, file)
                
                with open(file_path, 'r') as f:
                    self.reminders[user_id] = json.load(f)
        except Exception as e:
            print(f"Error loading medication reminders: {e}")
    
    def save_reminders(self, user_id):
        """Save a user's medication reminders to storage"""
        try:
            if user_id in self.reminders:
                file_path = os.path.join(self.data_dir, f"{user_id}.json")
                
                with open(file_path, 'w') as f:
                    json.dump(self.reminders[user_id], f, indent=2)
                return True
            return False
        except Exception as e:
            print(f"Error saving medication reminders: {e}")
            return False
    
    def get_user_medications(self, user_id):
        """
        Get all medications for a user
        
        Args:
            user_id (str): User ID
            
        Returns:
            list: List of medication objects
        """
        if user_id not in self.reminders:
            self.reminders[user_id] = []
            self.save_reminders(user_id)
        
        return self.reminders[user_id]
    
    def add_medication(self, user_id, name, dosage, frequency, start_date, end_date=None, notes=None):
        """
        Add a new medication reminder
        
        Args:
            user_id (str): User ID
            name (str): Medication name
            dosage (str): Dosage information
            frequency (str): How often to take (e.g., "every 8 hours", "daily", "weekly")
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            notes (str, optional): Additional notes
            
        Returns:
            dict: The created medication reminder
        """
        # Ensure user exists in reminders
        if user_id not in self.reminders:
            self.reminders[user_id] = []
        
        # Create new medication reminder
        medication = {
            "id": str(uuid.uuid4()),
            "name": name,
            "dosage": dosage,
            "frequency": frequency,
            "start_date": start_date,
            "end_date": end_date,
            "notes": notes,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "adherence": {
                "total_doses": 0,
                "taken_doses": 0,
                "missed_doses": 0,
                "history": []
            }
        }
        
        self.reminders[user_id].append(medication)
        self.save_reminders(user_id)
        
        return medication
    
    def update_medication(self, user_id, medication_id, updates):
        """
        Update an existing medication reminder
        
        Args:
            user_id (str): User ID
            medication_id (str): Medication ID
            updates (dict): Fields to update
            
        Returns:
            dict: Updated medication or None if not found
        """
        if user_id not in self.reminders:
            return None
        
        for i, medication in enumerate(self.reminders[user_id]):
            if medication["id"] == medication_id:
                # Update fields
                for key, value in updates.items():
                    if key in medication and key not in ["id", "created_at", "adherence"]:
                        medication[key] = value
                
                medication["updated_at"] = datetime.now().isoformat()
                self.reminders[user_id][i] = medication
                self.save_reminders(user_id)
                
                return medication
        
        return None
    
    def delete_medication(self, user_id, medication_id):
        """
        Delete a medication reminder
        
        Args:
            user_id (str): User ID
            medication_id (str): Medication ID
            
        Returns:
            bool: Success status
        """
        if user_id not in self.reminders:
            return False
        
        for i, medication in enumerate(self.reminders[user_id]):
            if medication["id"] == medication_id:
                self.reminders[user_id].pop(i)
                self.save_reminders(user_id)
                return True
        
        return False
    
    def record_medication_taken(self, user_id, medication_id, taken_at=None):
        """
        Record that a medication dose was taken
        
        Args:
            user_id (str): User ID
            medication_id (str): Medication ID
            taken_at (str, optional): Timestamp when taken (ISO format)
            
        Returns:
            bool: Success status
        """
        if not taken_at:
            taken_at = datetime.now().isoformat()
        
        if user_id not in self.reminders:
            return False
        
        for i, medication in enumerate(self.reminders[user_id]):
            if medication["id"] == medication_id:
                # Update adherence stats
                medication["adherence"]["total_doses"] += 1
                medication["adherence"]["taken_doses"] += 1
                
                # Add to history
                medication["adherence"]["history"].append({
                    "date": taken_at,
                    "status": "taken"
                })
                
                self.reminders[user_id][i] = medication
                self.save_reminders(user_id)
                
                return True
        
        return False
    
    def record_medication_missed(self, user_id, medication_id, missed_at=None):
        """
        Record that a medication dose was missed
        
        Args:
            user_id (str): User ID
            medication_id (str): Medication ID
            missed_at (str, optional): Timestamp when missed (ISO format)
            
        Returns:
            bool: Success status
        """
        if not missed_at:
            missed_at = datetime.now().isoformat()
        
        if user_id not in self.reminders:
            return False
        
        for i, medication in enumerate(self.reminders[user_id]):
            if medication["id"] == medication_id:
                # Update adherence stats
                medication["adherence"]["total_doses"] += 1
                medication["adherence"]["missed_doses"] += 1
                
                # Add to history
                medication["adherence"]["history"].append({
                    "date": missed_at,
                    "status": "missed"
                })
                
                self.reminders[user_id][i] = medication
                self.save_reminders(user_id)
                
                return True
        
        return False
    
    def get_adherence_rate(self, user_id, medication_id=None):
        """
        Calculate medication adherence rate
        
        Args:
            user_id (str): User ID
            medication_id (str, optional): Specific medication or all if None
            
        Returns:
            float: Adherence rate as percentage (0-100)
        """
        if user_id not in self.reminders:
            return 0.0
        
        if medication_id:
            # Calculate for specific medication
            for medication in self.reminders[user_id]:
                if medication["id"] == medication_id:
                    adherence = medication["adherence"]
                    if adherence["total_doses"] == 0:
                        return 100.0  # No doses yet
                    
                    return round((adherence["taken_doses"] / adherence["total_doses"]) * 100, 1)
            
            return 0.0  # Medication not found
        else:
            # Calculate overall adherence
            total_doses = 0
            taken_doses = 0
            
            for medication in self.reminders[user_id]:
                adherence = medication["adherence"]
                total_doses += adherence["total_doses"]
                taken_doses += adherence["taken_doses"]
            
            if total_doses == 0:
                return 100.0  # No doses yet
            
            return round((taken_doses / total_doses) * 100, 1)
    
    def get_due_medications(self, user_id, hours_window=24):
        """
        Get medications due within the specified time window
        
        Args:
            user_id (str): User ID
            hours_window (int): Number of hours to look ahead
            
        Returns:
            list: Medications due soon
        """
        if user_id not in self.reminders:
            return []
        
        due_medications = []
        now = datetime.now()
        cutoff = now + timedelta(hours=hours_window)
        
        for medication in self.reminders[user_id]:
            # Check if medication is active (within start/end dates)
            start_date = datetime.fromisoformat(medication["start_date"].replace('Z', '+00:00'))
            
            if medication["end_date"]:
                end_date = datetime.fromisoformat(medication["end_date"].replace('Z', '+00:00'))
                if now > end_date:
                    continue  # Medication period has ended
            
            if now < start_date:
                continue  # Medication period hasn't started
            
            # Parse frequency to determine if due within window
            frequency = medication["frequency"].lower()
            
            # Basic frequency parsing (could be expanded for more complex schedules)
            if "every" in frequency and "hour" in frequency:
                try:
                    hours = int(''.join(filter(str.isdigit, frequency)))
                    # If multiple doses per day, check if any fall within window
                    if now.hour % hours <= hours_window:
                        due_medications.append(medication)
                except:
                    # If parsing fails, include it to be safe
                    due_medications.append(medication)
            elif "daily" in frequency:
                due_medications.append(medication)
            elif "weekly" in frequency and (cutoff - now).days >= 7:
                # Only include if the weekly dose would fall within window
                due_medications.append(medication)
            elif "monthly" in frequency and (cutoff - now).days >= 30:
                # Only include if the monthly dose would fall within window
                due_medications.append(medication)
            else:
                # For other frequencies, include to be safe
                due_medications.append(medication)
        
        return due_medications 