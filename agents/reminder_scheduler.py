import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from .email_service import EmailService

class ReminderScheduler:
    """
    Schedules and sends medication reminders to users
    """
    
    def __init__(self, app=None, user_manager=None, medication_reminder=None, email_service=None):
        """Initialize the reminder scheduler"""
        self.logger = logging.getLogger(__name__)
        self.scheduler = BackgroundScheduler()
        self.user_manager = user_manager
        self.medication_reminder = medication_reminder
        self.email_service = email_service
        self.app = app
        
        if app and user_manager and medication_reminder and email_service:
            self.init_app(app, user_manager, medication_reminder, email_service)
    
    def init_app(self, app, user_manager, medication_reminder, email_service):
        """Configure with Flask app and required services"""
        self.app = app
        self.user_manager = user_manager
        self.medication_reminder = medication_reminder
        self.email_service = email_service
        
        # Start scheduler in application context
        with app.app_context():
            self._setup_scheduled_jobs()
            
            # Register to be started/stopped with Flask app
            @app.before_first_request
            def start_scheduler():
                if not self.scheduler.running:
                    self.scheduler.start()
                    self.logger.info("Reminder scheduler started")
            
            @app.teardown_appcontext
            def shutdown_scheduler(exception=None):
                if self.scheduler.running:
                    self.scheduler.shutdown()
                    self.logger.info("Reminder scheduler shut down")
    
    def start(self):
        """Start the scheduler if not already running"""
        if not self.scheduler.running:
            self.scheduler.start()
            self.logger.info("Reminder scheduler started")
    
    def shutdown(self):
        """Shut down the scheduler if running"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.logger.info("Reminder scheduler shut down")
    
    def _setup_scheduled_jobs(self):
        """Set up the scheduled reminder jobs"""
        # Schedule daily medication reminders
        self.scheduler.add_job(
            func=self.send_daily_medication_reminders,
            trigger=CronTrigger(hour=8, minute=0),  # 8:00 AM
            id='daily_medication_reminders_morning',
            replace_existing=True
        )
        
        # Add another reminder in the evening
        self.scheduler.add_job(
            func=self.send_daily_medication_reminders,
            trigger=CronTrigger(hour=18, minute=0),  # 6:00 PM
            id='daily_medication_reminders_evening',
            replace_existing=True
        )
        
        # Schedule weekly adherence reports
        self.scheduler.add_job(
            func=self.send_weekly_adherence_reports,
            trigger=CronTrigger(day_of_week='mon', hour=9, minute=0),  # Monday at 9:00 AM
            id='weekly_adherence_reports',
            replace_existing=True
        )
        
        # Schedule monthly adherence reports
        self.scheduler.add_job(
            func=self.send_monthly_adherence_reports,
            trigger=CronTrigger(day=1, hour=10, minute=0),  # 1st day of month at 10:00 AM
            id='monthly_adherence_reports',
            replace_existing=True
        )
        
        # Check for missed doses
        self.scheduler.add_job(
            func=self.check_for_missed_doses,
            trigger=IntervalTrigger(hours=6),  # Every 6 hours
            id='check_missed_doses',
            replace_existing=True
        )
        
        self.logger.info("Scheduled medication reminder jobs")
    
    def send_daily_medication_reminders(self):
        """Send daily medication reminders to users"""
        self.logger.info("Running job: send_daily_medication_reminders")
        
        # Initialize counts for logging
        total_users = 0
        total_reminders_sent = 0
        
        try:
            # Get all users
            users = self.user_manager.get_all_users()
            
            for user in users:
                user_id = user.get_id()
                
                # Skip if user has no email or has notifications disabled
                if not user.email:
                    continue
                    
                # Get medications due in the next 24 hours
                due_medications = self.medication_reminder.get_due_medications(user_id, hours_window=24)
                
                if due_medications:
                    # Format medications for the email
                    email_medications = []
                    for med in due_medications:
                        email_medications.append({
                            'name': med['name'],
                            'dosage': med['dosage'],
                            'frequency': med['frequency']
                        })
                    
                    # Send reminder email
                    success = self.email_service.send_medication_reminder(
                        user_email=user.email,
                        user_name=user.name or user.username,
                        medications=email_medications
                    )
                    
                    if success:
                        total_reminders_sent += 1
                        
                total_users += 1
                
            self.logger.info(f"Sent {total_reminders_sent} medication reminders to {total_users} users")
            
        except Exception as e:
            self.logger.error(f"Error sending daily medication reminders: {str(e)}")
    
    def send_weekly_adherence_reports(self):
        """Send weekly adherence reports to users"""
        self.logger.info("Running job: send_weekly_adherence_reports")
        
        # Initialize counts for logging
        total_users = 0
        total_reports_sent = 0
        
        try:
            # Get all users
            users = self.user_manager.get_all_users()
            
            for user in users:
                user_id = user.get_id()
                
                # Skip if user has no email
                if not user.email:
                    continue
                    
                # Get user's adherence rate
                adherence_rate = self.medication_reminder.get_adherence_rate(user_id)
                
                # Skip if user has no medications
                if adherence_rate is None:
                    continue
                
                # Send adherence report
                success = self.email_service.send_adherence_report(
                    user_email=user.email,
                    user_name=user.name or user.username,
                    adherence_rate=adherence_rate,
                    report_period="weekly"
                )
                
                if success:
                    total_reports_sent += 1
                    
                total_users += 1
                
            self.logger.info(f"Sent {total_reports_sent} weekly adherence reports to {total_users} users")
            
        except Exception as e:
            self.logger.error(f"Error sending weekly adherence reports: {str(e)}")
    
    def send_monthly_adherence_reports(self):
        """Send monthly adherence reports to users"""
        self.logger.info("Running job: send_monthly_adherence_reports")
        
        # Initialize counts for logging
        total_users = 0
        total_reports_sent = 0
        
        try:
            # Get all users
            users = self.user_manager.get_all_users()
            
            for user in users:
                user_id = user.get_id()
                
                # Skip if user has no email
                if not user.email:
                    continue
                    
                # Get user's adherence rate
                adherence_rate = self.medication_reminder.get_adherence_rate(user_id)
                
                # Skip if user has no medications
                if adherence_rate is None:
                    continue
                
                # Send adherence report
                success = self.email_service.send_adherence_report(
                    user_email=user.email,
                    user_name=user.name or user.username,
                    adherence_rate=adherence_rate,
                    report_period="monthly"
                )
                
                if success:
                    total_reports_sent += 1
                    
                total_users += 1
                
            self.logger.info(f"Sent {total_reports_sent} monthly adherence reports to {total_users} users")
            
        except Exception as e:
            self.logger.error(f"Error sending monthly adherence reports: {str(e)}")
    
    def check_for_missed_doses(self):
        """Check for any missed medication doses and record them"""
        self.logger.info("Running job: check_for_missed_doses")
        
        try:
            # Get all users
            users = self.user_manager.get_all_users()
            total_missed_doses = 0
            
            for user in users:
                user_id = user.get_id()
                
                # Get all user medications
                medications = self.medication_reminder.get_user_medications(user_id)
                
                for med in medications:
                    # Skip medications that haven't started yet or have ended
                    now = datetime.now()
                    start_date = datetime.fromisoformat(med["start_date"].replace('Z', '+00:00'))
                    
                    if now < start_date:
                        continue
                        
                    if med["end_date"]:
                        end_date = datetime.fromisoformat(med["end_date"].replace('Z', '+00:00'))
                        if now > end_date:
                            continue
                    
                    # Check for missed doses based on frequency
                    # This is a simplified check - a real implementation would be more sophisticated
                    frequency = med["frequency"].lower()
                    
                    # Get the last history entry if any
                    history = med["adherence"]["history"]
                    last_taken = None
                    
                    if history:
                        # Sort history by date (newest first)
                        sorted_history = sorted(
                            history, 
                            key=lambda x: datetime.fromisoformat(x["date"].replace('Z', '+00:00')),
                            reverse=True
                        )
                        last_entry = sorted_history[0]
                        last_taken = datetime.fromisoformat(last_entry["date"].replace('Z', '+00:00'))
                    
                    # If no history or the last action was a long time ago
                    if not last_taken or (now - last_taken).total_seconds() > self._get_frequency_seconds(frequency):
                        # Record as missed
                        self.medication_reminder.record_medication_missed(user_id, med["id"])
                        total_missed_doses += 1
            
            self.logger.info(f"Recorded {total_missed_doses} missed medication doses")
            
        except Exception as e:
            self.logger.error(f"Error checking for missed doses: {str(e)}")
    
    def _get_frequency_seconds(self, frequency):
        """Convert a frequency string to seconds"""
        frequency = frequency.lower()
        
        if "every" in frequency and "hour" in frequency:
            try:
                hours = int(''.join(filter(str.isdigit, frequency)))
                return hours * 3600  # Convert hours to seconds
            except:
                return 86400  # Default to 24 hours if parsing fails
        elif "daily" in frequency:
            return 86400  # 24 hours in seconds
        elif "twice daily" in frequency:
            return 43200  # 12 hours in seconds
        elif "weekly" in frequency:
            return 604800  # 7 days in seconds
        elif "monthly" in frequency:
            return 2592000  # 30 days in seconds
        else:
            return 86400  # Default to 24 hours for unknown frequencies 