import os
import json
import uuid
from datetime import datetime, timedelta
import base64
from io import BytesIO
from fpdf import FPDF
import matplotlib.pyplot as plt

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
    
    def generate_medication_report(self, user_id):
        """
        Generate a comprehensive PDF report of a user's medications
        
        Args:
            user_id (str): User ID
            
        Returns:
            bytes: PDF report as bytes or None if failed
        """
        if user_id not in self.reminders or not self.reminders[user_id]:
            return None
        
        try:
            # Create PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Set up formatting
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_fill_color(66, 135, 245)  # Primary blue color
            pdf.set_text_color(255, 255, 255)  # White text
            
            # Header
            pdf.cell(0, 16, "Medication Report", 0, 1, "C", True)
            pdf.ln(5)
            
            # Report metadata
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(0, 0, 0)  # Black text
            pdf.cell(0, 8, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
            pdf.cell(0, 8, f"Patient ID: {user_id}", 0, 1)
            pdf.ln(5)
            
            # Overall adherence
            adherence_rate = self.get_adherence_rate(user_id)
            
            # Generate adherence pie chart
            adherence_img = self._generate_adherence_chart(adherence_rate)
            if adherence_img:
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 10, "Medication Adherence", 0, 1)
                
                # Add adherence summary
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(100, 8, f"Overall adherence rate: {adherence_rate}%", 0, 1)
                
                # Convert PIL image to temp file to pass to PDF
                img_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp_chart.png')
                adherence_img.save(img_path, format='PNG')
                
                # Add the image
                pdf.image(img_path, x=55, y=pdf.get_y(), w=100)
                pdf.ln(90)  # Space for the chart
                
                # Remove temporary file
                os.remove(img_path)
            
            # Medications table
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 12, "Current Medications", 0, 1)
            
            # Table header
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_fill_color(240, 240, 240)  # Light gray background
            pdf.set_text_color(0, 0, 0)  # Black text
            
            # Define column widths (total = 190)
            col_widths = [60, 25, 40, 30, 35]
            
            # Create header row
            pdf.cell(col_widths[0], 10, "Medication", 1, 0, "C", True)
            pdf.cell(col_widths[1], 10, "Dosage", 1, 0, "C", True)
            pdf.cell(col_widths[2], 10, "Frequency", 1, 0, "C", True)
            pdf.cell(col_widths[3], 10, "Start Date", 1, 0, "C", True)
            pdf.cell(col_widths[4], 10, "End Date", 1, 1, "C", True)
            
            # Add medication rows
            pdf.set_font("Helvetica", "", 10)
            for medication in self.reminders[user_id]:
                # First row - basic info
                pdf.cell(col_widths[0], 10, medication["name"], 1, 0, "L")
                pdf.cell(col_widths[1], 10, medication["dosage"], 1, 0, "L")
                pdf.cell(col_widths[2], 10, medication["frequency"], 1, 0, "L")
                
                start_date = datetime.fromisoformat(medication["start_date"].replace('Z', '+00:00')).strftime('%Y-%m-%d')
                pdf.cell(col_widths[3], 10, start_date, 1, 0, "C")
                
                end_date = "Ongoing"
                if medication["end_date"]:
                    end_date = datetime.fromisoformat(medication["end_date"].replace('Z', '+00:00')).strftime('%Y-%m-%d')
                pdf.cell(col_widths[4], 10, end_date, 1, 1, "C")
            
            pdf.ln(5)
            
            # Detailed statistics for each medication
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 12, "Medication Details", 0, 1)
            
            for medication in self.reminders[user_id]:
                # Medication header
                pdf.set_font("Helvetica", "B", 12)
                pdf.set_fill_color(200, 220, 255)  # Light blue
                pdf.cell(0, 10, f"{medication['name']} - {medication['dosage']}", 0, 1, "L", True)
                
                # Medication details
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(90, 8, f"Frequency: {medication['frequency']}", 0, 0)
                
                # Adherence for this medication
                adherence = medication["adherence"]
                
                taken = adherence["taken_doses"]
                total = adherence["total_doses"]
                
                if total > 0:
                    rate = round((taken / total) * 100, 1)
                    pdf.cell(100, 8, f"Adherence Rate: {rate}%", 0, 1)
                    pdf.cell(90, 8, f"Doses Taken: {taken}/{total}", 0, 0)
                    pdf.cell(100, 8, f"Doses Missed: {adherence['missed_doses']}", 0, 1)
                else:
                    pdf.cell(100, 8, "No doses recorded yet", 0, 1)
                
                # Notes
                if medication["notes"]:
                    pdf.ln(3)
                    pdf.set_font("Helvetica", "I", 10)
                    pdf.multi_cell(0, 8, f"Notes: {medication['notes']}")
                
                # Recent history if available
                if adherence["history"]:
                    pdf.ln(3)
                    pdf.set_font("Helvetica", "B", 10)
                    pdf.cell(0, 8, "Recent History (Last 5 Entries):", 0, 1)
                    
                    pdf.set_font("Helvetica", "", 10)
                    recent_history = sorted(
                        adherence["history"], 
                        key=lambda x: datetime.fromisoformat(x["date"].replace('Z', '+00:00')),
                        reverse=True
                    )[:5]
                    
                    for entry in recent_history:
                        entry_date = datetime.fromisoformat(entry["date"].replace('Z', '+00:00'))
                        date_str = entry_date.strftime('%Y-%m-%d %H:%M')
                        status = "✓ Taken" if entry["status"] == "taken" else "✗ Missed"
                        status_color = (0, 150, 0) if entry["status"] == "taken" else (200, 0, 0)
                        
                        pdf.set_text_color(0, 0, 0)  # Reset to black for date
                        pdf.cell(50, 8, date_str, 0, 0)
                        
                        pdf.set_text_color(*status_color)
                        pdf.cell(40, 8, status, 0, 1)
                    
                    # Reset text color
                    pdf.set_text_color(0, 0, 0)
                
                pdf.ln(5)
            
            # Health Provider Information
            pdf.ln(10)
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_fill_color(220, 220, 220)  # Light gray
            pdf.cell(0, 10, "For Healthcare Providers", 0, 1, "L", True)
            
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(0, 8, (
                "This report provides a summary of the patient's current medications and adherence patterns. "
                "It is generated directly from the patient's self-reported medication tracking data. "
                "Please verify all information with the patient during consultation."
            ))
            
            # Disclaimer
            pdf.ln(10)
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(100, 100, 100)  # Gray text
            pdf.multi_cell(0, 5, (
                "Disclaimer: This report is generated by the MedicalAI Assistant application based on user-entered data. "
                "It is intended for informational purposes only and should not be used as the sole basis for medical decisions. "
                "Always consult with qualified healthcare providers for medical concerns."
            ))
            
            # Export to bytes
            return pdf.output(dest='S').encode('latin1')
            
        except Exception as e:
            print(f"Error generating medication report: {e}")
            return None
    
    def _generate_adherence_chart(self, adherence_rate):
        """Generate a pie chart showing medication adherence"""
        try:
            from PIL import Image
            
            # Create figure
            plt.figure(figsize=(6, 4))
            
            # Create pie chart
            labels = ['Taken', 'Missed']
            sizes = [adherence_rate, 100 - adherence_rate]
            colors = ['#28a745', '#dc3545']  # Green and red
            
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                   shadow=False, startangle=90, wedgeprops={'linewidth': 1, 'edgecolor': 'white'})
            
            # Equal aspect ratio ensures that pie is drawn as a circle
            plt.axis('equal')
            plt.title('Medication Adherence Rate')
            
            # Convert to image
            buf = BytesIO()
            plt.savefig(buf, format='png')
            plt.close()
            buf.seek(0)
            
            # Convert to PIL Image
            img = Image.open(buf)
            return img
            
        except Exception as e:
            print(f"Error generating adherence chart: {e}")
            return None 