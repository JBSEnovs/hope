import os
from datetime import datetime, timedelta
from flask_mail import Mail, Message
from jinja2 import Template
import logging

mail = Mail()  # Initialize, will be configured with the app in app.py

class EmailService:
    """
    Service for handling all email-related functionality
    """
    
    def __init__(self, app=None):
        """Initialize the email service"""
        self.logger = logging.getLogger(__name__)
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Configure with Flask app"""
        mail.init_app(app)
        self.sender = app.config.get('MAIL_DEFAULT_SENDER', 'no-reply@medicalai.example.com')
        self.app = app
    
    def send_email(self, recipient, subject, body_html, body_text=None):
        """
        Send an email to a recipient
        
        Args:
            recipient (str): Email address of recipient
            subject (str): Email subject
            body_html (str): HTML content of email
            body_text (str, optional): Plain text version of email
            
        Returns:
            bool: Success status
        """
        try:
            msg = Message(
                subject=subject,
                recipients=[recipient],
                sender=self.sender
            )
            
            msg.html = body_html
            if body_text:
                msg.body = body_text
                
            mail.send(msg)
            self.logger.info(f"Email sent to {recipient}: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return False
    
    def send_medication_reminder(self, user_email, user_name, medications):
        """
        Send medication reminder email
        
        Args:
            user_email (str): User's email address
            user_name (str): User's name or username
            medications (list): List of medication dicts with name, dosage, frequency
            
        Returns:
            bool: Success status
        """
        subject = "Medication Reminder - MedicalAI Assistant"
        
        # Load email template
        template_html = self._get_medication_reminder_template()
        
        # Prepare template data
        template_data = {
            'user_name': user_name,
            'medications': medications,
            'current_date': datetime.now().strftime("%A, %B %d, %Y"),
            'app_url': os.environ.get('APP_URL', 'http://localhost:5000')
        }
        
        # Render template
        html_content = Template(template_html).render(**template_data)
        
        # Create plain text version
        text_content = f"Hello {user_name},\n\nThis is a reminder to take your medications for today, {template_data['current_date']}.\n\n"
        for med in medications:
            text_content += f"- {med['name']} ({med['dosage']}): {med['frequency']}\n"
        text_content += f"\nVisit {template_data['app_url']} to mark these medications as taken.\n\nThank you,\nMedicalAI Assistant"
        
        # Send email
        return self.send_email(user_email, subject, html_content, text_content)
    
    def send_adherence_report(self, user_email, user_name, adherence_rate, report_period="weekly"):
        """
        Send a medication adherence report
        
        Args:
            user_email (str): User's email address
            user_name (str): User's name
            adherence_rate (float): User's medication adherence rate
            report_period (str): Period of report (weekly, monthly)
        
        Returns:
            bool: Success status
        """
        period_text = "Weekly" if report_period == "weekly" else "Monthly"
        subject = f"{period_text} Medication Adherence Report"
        
        # Determine date range for the report
        today = datetime.now()
        if report_period == "weekly":
            start_date = (today - timedelta(days=7)).strftime("%B %d")
        else:
            start_date = (today - timedelta(days=30)).strftime("%B %d")
        end_date = today.strftime("%B %d, %Y")
        
        # Create email content
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                    <h2 style="color: #0066cc; margin-top: 0;">{period_text} Medication Adherence Report</h2>
                    <p>Hello {user_name},</p>
                    <p>Here is your medication adherence report for {start_date} to {end_date}:</p>
                </div>
                
                <div style="background-color: #fff; border: 1px solid #dee2e6; border-radius: 5px; padding: 20px; margin-bottom: 20px;">
                    <div style="text-align: center; margin-bottom: 20px;">
                        <div style="width: 150px; height: 150px; border-radius: 50%; margin: 0 auto; position: relative; 
                            background: conic-gradient(#28a745 {adherence_rate}%, #dc3545 0%); display: flex; align-items: center; justify-content: center;">
                            <div style="width: 120px; height: 120px; border-radius: 50%; background: white; position: absolute;"></div>
                            <div style="position: relative; z-index: 2; font-size: 24px; font-weight: bold;">{adherence_rate}%</div>
                        </div>
                        <p style="margin-top: 10px; font-weight: bold;">Overall Adherence Rate</p>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <h3>What This Means:</h3>
                        <p>
                            {self._get_adherence_feedback(adherence_rate)}
                        </p>
                    </div>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
                    <p style="margin-bottom: 15px;">You can view your complete medication details and adherence statistics in your MedicalAI Assistant dashboard:</p>
                    <div style="text-align: center;">
                        <a href="{os.environ.get('APP_URL', 'http://localhost:5000')}/medications" 
                           style="background-color: #0066cc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            View Medications Dashboard
                        </a>
                    </div>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; font-size: 12px; color: #6c757d;">
                    <p>This is an automated message from MedicalAI Assistant. Please do not reply to this email.</p>
                    <p>If you no longer wish to receive these reports, you can adjust your notification settings in your account preferences.</p>
                </div>
            </body>
        </html>
        """
        
        text_content = f"""Hello {user_name},

This is your {report_period} medication adherence report for {start_date} to {end_date}.

Your overall adherence rate is: {adherence_rate}%

{self._get_adherence_feedback(adherence_rate, plain_text=True)}

Visit {os.environ.get('APP_URL', 'http://localhost:5000')}/medications to view your complete medication details.

This is an automated message from MedicalAI Assistant. Please do not reply to this email.
If you no longer wish to receive these reports, you can adjust your notification settings in your account preferences.
"""
        
        # Send email
        return self.send_email(user_email, subject, html_content, text_content)
    
    def _get_medication_reminder_template(self):
        """Get the HTML template for medication reminders"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Medication Reminder</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
                <h2 style="color: #0066cc; margin-top: 0;">Medication Reminder</h2>
                <p>Hello {{ user_name }},</p>
                <p>This is a reminder to take your medications for today, {{ current_date }}.</p>
            </div>
            
            <div style="background-color: #fff; border: 1px solid #dee2e6; border-radius: 5px; padding: 20px; margin-bottom: 20px;">
                <h3>Your Medications</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="padding: 10px; border: 1px solid #dee2e6; text-align: left;">Medication</th>
                            <th style="padding: 10px; border: 1px solid #dee2e6; text-align: left;">Dosage</th>
                            <th style="padding: 10px; border: 1px solid #dee2e6; text-align: left;">Schedule</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for med in medications %}
                        <tr>
                            <td style="padding: 10px; border: 1px solid #dee2e6;">{{ med.name }}</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6;">{{ med.dosage }}</td>
                            <td style="padding: 10px; border: 1px solid #dee2e6;">{{ med.frequency }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <div style="text-align: center; margin-bottom: 20px;">
                <a href="{{ app_url }}/medications" 
                   style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    Mark as Taken
                </a>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; font-size: 14px;">
                <p style="margin-top: 0;">
                    <strong>Why is medication adherence important?</strong><br>
                    Taking your medications as prescribed helps ensure they work effectively and can prevent complications.
                </p>
                
                <p style="margin-bottom: 0;">
                    <strong>Tips for remembering your medications:</strong><br>
                    - Take medications at the same time each day<br>
                    - Use a pill organizer<br>
                    - Set alarms on your phone<br>
                    - Keep medications in a visible location (but away from children)
                </p>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; font-size: 12px; color: #6c757d;">
                <p>This is an automated message from MedicalAI Assistant. Please do not reply to this email.</p>
                <p>If you no longer wish to receive these reminders, you can adjust your notification settings in your account preferences.</p>
            </div>
        </body>
        </html>
        """
    
    def _get_adherence_feedback(self, adherence_rate, plain_text=False):
        """Get personalized feedback based on adherence rate"""
        if adherence_rate >= 90:
            feedback = "Excellent job! You're taking your medications very consistently, which is optimal for your health."
            tips = "Keep up the good work and maintain your current routine."
        elif adherence_rate >= 80:
            feedback = "Good job! Your medication adherence is good, but there's a little room for improvement."
            tips = "Try setting additional reminders or using a pill organizer to help remember your doses."
        elif adherence_rate >= 70:
            feedback = "Your adherence is fair. Missing doses can reduce the effectiveness of your medications."
            tips = "Consider setting up daily alarms or placing your medications in a visible location to help remember."
        elif adherence_rate >= 50:
            feedback = "Your adherence needs improvement. Missing doses frequently can impact your health outcomes."
            tips = "Talk to your healthcare provider about simplifying your medication regimen if possible, and use reminder tools like pill organizers and alarms."
        else:
            feedback = "Your adherence is low, which may be affecting your health. It's important to take your medications as prescribed."
            tips = "Please discuss any concerns or side effects with your healthcare provider, and consider using medication reminders and tracking tools to help improve adherence."
            
        if plain_text:
            return f"{feedback}\n\nTips to improve: {tips}"
        else:
            return f"<p>{feedback}</p><p><strong>Tips to improve:</strong> {tips}</p>" 