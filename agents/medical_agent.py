import os
import requests
import json
import openai
from .document_processor import DocumentProcessor
from .data_visualizer import DataVisualizer
from .image_analyzer import MedicalImageAnalyzer
from .voice_interface import VoiceInterface
from .collaboration import CollaborationManager
from .auth import UserManager
from .blackbox_ai import BlackboxAI
from .language import LanguageManager
from .medication_reminder import MedicationReminder

class MedicalAgent:
    def __init__(self, provider="openai", model=None):
        """
        Initialize the Medical Agent with specified AI provider
        
        Args:
            provider (str): The AI provider to use ('openai', 'google', or 'blackbox')
            model (str): Specific model to use, or None for default
        """
        # Set up the AI model based on provider
        self.provider = provider.lower()
        self.model_name = model
        
        # Initialize API keys
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        # Initialize components
        self.doc_processor = DocumentProcessor()
        self.visualizer = DataVisualizer()
        self.image_analyzer = MedicalImageAnalyzer()
        self.voice_interface = VoiceInterface()
        self.collaboration_manager = CollaborationManager()
        self.user_manager = UserManager()
        self.blackbox_ai = BlackboxAI(model=model or "blackboxai")
        self.language_manager = LanguageManager()
        self.medication_reminder = MedicationReminder()
        
        # Default language (can be changed per user)
        self.current_language = 'en'
        
        # Set up the disclaimer
        self.disclaimer = (
            "IMPORTANT MEDICAL DISCLAIMER: This information is provided for educational purposes only and "
            "is not intended as a substitute for professional medical advice, diagnosis, or treatment. "
            "Always seek the advice of your physician or other qualified health provider with any "
            "questions you may have regarding a medical condition. Never disregard professional medical "
            "advice or delay in seeking it because of something you have read here."
        )
        
        # Set up OpenAI client if needed
        if self.provider == "openai" and self.openai_api_key:
            openai.api_key = self.openai_api_key
            
    def change_provider(self, provider, model=None):
        """Change the AI provider dynamically"""
        self.provider = provider.lower()
        self.model_name = model
        try:
            if provider.lower() == "blackbox" and model:
                self.blackbox_ai.change_model(model)
            return True
        except Exception as e:
            print(f"Error changing provider: {str(e)}")
            return False
    
    def diagnose(self, symptoms, language=None):
        """Analyze symptoms and suggest possible diagnoses"""
        # Use specified language or default
        target_language = language or self.current_language
        
        prompt = (
            "You are a medical AI assistant. A patient describes the following symptoms: {symptoms}\n\n"
            "Based only on these symptoms, suggest possible conditions that might match these symptoms, "
            "organized from most to least likely. For each, include:\n"
            "1. The name of the condition\n"
            "2. Why it matches the symptoms\n"
            "3. What other symptoms might be present if this condition is correct\n"
            "4. What kind of medical professional should be consulted\n\n"
            "Remember to be thorough but emphasize the importance of consulting a healthcare professional for accurate diagnosis."
        ).format(symptoms=symptoms)
        
        # Get response based on provider
        result = self._get_ai_response(prompt)
        
        # Translate result if needed
        if target_language != 'en':
            result = self.language_manager.translate_medical_content(result, target_language)
            disclaimer = self.language_manager.translate_text(self.disclaimer, target_language)
            return f"{disclaimer}\n\n{result}"
        else:
            return f"{self.disclaimer}\n\n{result}"
    
    def recommend_treatment(self, condition, language=None):
        """Provide information about treatment options for a condition"""
        # Use specified language or default
        target_language = language or self.current_language
        
        prompt = (
            "You are a medical AI assistant. A user is asking about treatment options for: {condition}\n\n"
            "Provide information about:\n"
            "1. Common evidence-based treatment approaches\n"
            "2. Lifestyle modifications that might help\n"
            "3. What type of healthcare provider typically manages this condition\n"
            "4. Important considerations patients should know\n\n"
            "Focus on providing balanced, evidence-based information while emphasizing the importance of personalized medical advice."
        ).format(condition=condition)
        
        # Get response based on provider
        result = self._get_ai_response(prompt)
        
        # Translate result if needed
        if target_language != 'en':
            result = self.language_manager.translate_medical_content(result, target_language)
            disclaimer = self.language_manager.translate_text(self.disclaimer, target_language)
            return f"{disclaimer}\n\n{result}"
        else:
            return f"{self.disclaimer}\n\n{result}"
    
    def research_disease(self, disease, language=None):
        """Research information about a specific disease or medical condition"""
        # Use specified language or default
        target_language = language or self.current_language
        
        prompt = (
            "You are a medical AI assistant. A user wants to learn about: {disease}\n\n"
            "Provide comprehensive, well-structured information including:\n"
            "1. Definition and overview of the condition\n"
            "2. Causes and risk factors\n"
            "3. Signs and symptoms\n"
            "4. Diagnostic approaches\n"
            "5. Treatment options\n"
            "6. Prognosis and complications\n"
            "7. Prevention strategies if applicable\n"
            "8. Current research directions\n\n"
            "Use current medical knowledge and emphasize evidence-based information. Format your response with clear headings for readability."
        ).format(disease=disease)
        
        # Get response based on provider
        result = self._get_ai_response(prompt)
        
        # Translate result if needed
        if target_language != 'en':
            result = self.language_manager.translate_medical_content(result, target_language)
            disclaimer = self.language_manager.translate_text(self.disclaimer, target_language)
            return f"{disclaimer}\n\n{result}"
        else:
            return f"{self.disclaimer}\n\n{result}"
    
    def _get_ai_response(self, prompt):
        """Get response from the selected AI provider"""
        if self.provider == "openai":
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            
            model = self.model_name or "gpt-4"
            response = openai.Completion.create(
                engine=model,
                prompt=prompt,
                temperature=0.2,
                max_tokens=2000
            )
            return response.choices[0].text
            
        elif self.provider == "google":
            if not self.google_api_key:
                raise ValueError("GOOGLE_API_KEY environment variable is not set")
            
            model = self.model_name or "gemini-1.0-pro"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.google_api_key
            }
            data = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2}
            }
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response generated")
            
        elif self.provider == "blackbox":
            return self.blackbox_query(prompt)
            
        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Supported providers are 'openai', 'google', and 'blackbox'")
    
    def blackbox_query(self, query, conversation_id=None):
        """Use the Blackbox AI for a query"""
        try:
            response = self.blackbox_ai.chat(query, conversation_id)
            return response
        except Exception as e:
            print(f"Error using BlackboxAI: {str(e)}")
            return "Sorry, there was an error connecting to the AI service. Please try again later."
    
    def get_blackbox_models(self):
        """Get the list of available BlackboxAI models"""
        return self.blackbox_ai.get_available_models()
    
    def upload_document(self, file_content, file_name):
        """Upload and process a medical document"""
        return self.doc_processor.process_file(file_content, file_name)
    
    def get_uploaded_documents(self):
        """Get the list of uploaded documents"""
        return self.doc_processor.get_document_sources()
    
    def generate_symptom_visualization(self, symptoms_data, title="Common Symptoms"):
        """Generate a visualization of symptom data"""
        description = "Bar chart showing symptom frequency or severity"
        try:
            image_path = self.visualizer.create_bar_chart(
                data=symptoms_data,
                title=title,
                x_label="Symptoms",
                y_label="Frequency/Severity",
                description=description
            )
            return {"path": image_path, "description": description}
        except Exception as e:
            print(f"Error generating symptom visualization: {str(e)}")
            return {"error": str(e)}
    
    def generate_treatment_visualization(self, treatment_data, title="Treatment Efficacy"):
        """Generate a visualization of treatment efficacy data"""
        description = "Comparison of different treatment approaches"
        try:
            image_path = self.visualizer.create_comparison_chart(
                data=treatment_data,
                title=title,
                description=description
            )
            return {"path": image_path, "description": description}
        except Exception as e:
            print(f"Error generating treatment visualization: {str(e)}")
            return {"error": str(e)}
    
    def generate_progression_visualization(self, progression_data, title="Disease Progression", 
                                      x_label="Time", y_label="Metric"):
        """Generate a visualization of disease progression over time"""
        description = "Line chart showing disease progression metrics over time"
        try:
            image_path = self.visualizer.create_line_chart(
                data=progression_data,
                title=title,
                x_label=x_label,
                y_label=y_label,
                description=description
            )
            return {"path": image_path, "description": description}
        except Exception as e:
            print(f"Error generating progression visualization: {str(e)}")
            return {"error": str(e)}
    
    def extract_visualization_data(self, text, data_type="symptoms"):
        """Extract data for visualization from text using AI"""
        prompt_templates = {
            "symptoms": (
                "The following text contains medical information about symptoms. "
                "Extract the symptoms and their frequency or severity as a JSON object. "
                "For example: {{'Headache': 75, 'Fever': 60, 'Nausea': 45}}. "
                "Text: {text}"
            ),
            "treatments": (
                "The following text contains information about treatments. "
                "Extract the treatments and their efficacy rates as a JSON object. "
                "For example: {{'Medication A': 85, 'Therapy B': 70, 'Surgery C': 90}}. "
                "Text: {text}"
            ),
            "progression": (
                "The following text contains information about disease progression over time. "
                "Extract the time points and corresponding metric values as a JSON object. "
                "For example: {{'Week 1': 10, 'Week 2': 15, 'Week 3': 25, 'Week 4': 20}}. "
                "Text: {text}"
            )
        }
        
        prompt = prompt_templates.get(data_type, prompt_templates["symptoms"]).format(text=text)
        
        # Get AI response
        result = self._get_ai_response(prompt)
        
        # Try to extract JSON data
        try:
            # Find JSON-like content in the response
            result = result.strip()
            start_idx = result.find('{')
            end_idx = result.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = result[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {}
        except Exception as e:
            print(f"Error extracting visualization data: {str(e)}")
            return {}
    
    def analyze_medical_image(self, image_data, enhancement=None):
        """Analyze a medical image and provide insights"""
        # Apply enhancement if specified
        if enhancement:
            image_data = self.image_analyzer.enhance_image(image_data, enhancement)
        
        # Extract image features
        features = self.image_analyzer.extract_features(image_data)
        
        # Generate analysis prompt
        prompt = (
            "You are a medical imaging AI assistant. Analyze this medical image with the following extracted features:\n"
            f"{json.dumps(features, indent=2)}\n\n"
            "Provide a detailed analysis including:\n"
            "1. What type of medical image this appears to be\n"
            "2. Notable structures or anomalies visible in the image\n"
            "3. Potential medical significance of the observed features\n"
            "4. Recommendations for further analysis or imaging if needed\n\n"
            "Remember to emphasize that this is an AI-assisted preliminary analysis and should be reviewed by a qualified medical professional."
        )
        
        # Get AI response
        result = self._get_ai_response(prompt)
        
        return {
            "analysis": result,
            "features": features,
            "enhanced": enhancement is not None,
            "enhancement_type": enhancement if enhancement else "none"
        }
    
    def enhance_medical_image(self, image_data, enhancement_type):
        """Apply enhancement to a medical image"""
        return self.image_analyzer.enhance_image(image_data, enhancement_type)
    
    def get_available_image_enhancements(self):
        """Get list of available image enhancement techniques"""
        return self.image_analyzer.get_available_enhancements()
    
    def transcribe_voice_input(self, audio_data, language='en-US'):
        """Transcribe voice input to text"""
        return self.voice_interface.transcribe_audio(audio_data, language)
    
    def generate_voice_response(self, text, voice_type=None):
        """Generate a voice response from text"""
        return self.voice_interface.text_to_speech(text, voice_type)
    
    def extract_medical_terms_from_speech(self, text):
        """Extract key medical terms from speech transcript"""
        return self.voice_interface.extract_medical_terms(text)
    
    def get_supported_languages(self):
        """Get a list of languages supported by the system"""
        return self.language_manager.get_supported_languages()
    
    # Collaboration methods
    def create_consultation_session(self, patient_id, session_type="consultation"):
        """Create a new consultation session"""
        return self.collaboration_manager.create_session(patient_id, session_type)
    
    def join_consultation(self, session_id, participant_id, role="doctor"):
        """Join an existing consultation session"""
        return self.collaboration_manager.join_session(session_id, participant_id, role)
    
    def leave_consultation(self, session_id, participant_id):
        """Leave a consultation session"""
        return self.collaboration_manager.leave_session(session_id, participant_id)
    
    def send_consultation_message(self, session_id, sender_id, content, message_type="text"):
        """Send a message in a consultation session"""
        return self.collaboration_manager.send_message(session_id, sender_id, content, message_type)
    
    def get_consultation_messages(self, session_id, since_timestamp=None):
        """Get messages from a consultation session"""
        return self.collaboration_manager.get_messages(session_id, since_timestamp)
    
    def get_active_consultations(self, participant_id=None):
        """Get a list of active consultation sessions"""
        return self.collaboration_manager.get_active_sessions(participant_id)
    
    def end_consultation(self, session_id):
        """End a consultation session"""
        return self.collaboration_manager.end_session(session_id)
    
    # User management methods
    def register_user(self, username, email, password, role='patient', name=None, profile=None):
        """Register a new user"""
        return self.user_manager.register_user(username, email, password, role, name, profile)
    
    def authenticate_user(self, username_or_email, password):
        """Authenticate a user"""
        return self.user_manager.authenticate(username_or_email, password)
    
    def get_user(self, user_id):
        """Get user information"""
        return self.user_manager.get_user(user_id)
    
    def update_user_profile(self, user_id, data):
        """Update a user's profile"""
        return self.user_manager.update_profile(user_id, data)
    
    def change_user_password(self, user_id, current_password, new_password):
        """Change a user's password"""
        return self.user_manager.change_password(user_id, current_password, new_password)
    
    # Language management methods
    def change_language(self, language_code):
        """Change the current language"""
        if language_code in self.language_manager.get_supported_languages():
            self.current_language = language_code
            return True
        else:
            return False
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        return self.language_manager.get_supported_languages()
    
    def detect_language(self, text):
        """Detect the language of a text"""
        return self.language_manager.detect_language(text)
    
    def translate_text(self, text, target_language=None):
        """Translate text to the target language"""
        target_language = target_language or self.current_language
        return self.language_manager.translate_text(text, target_language)
    
    # Medication reminder methods
    def get_user_medications(self, user_id):
        """Get user medications"""
        return self.medication_reminder.get_user_medications(user_id)
    
    def add_medication(self, user_id, name, dosage, frequency, start_date, end_date=None, notes=None):
        """Add a medication reminder"""
        return self.medication_reminder.add_medication(user_id, name, dosage, frequency, start_date, end_date, notes)
    
    def update_medication(self, user_id, medication_id, updates):
        """Update a medication reminder"""
        return self.medication_reminder.update_medication(user_id, medication_id, updates)
    
    def delete_medication(self, user_id, medication_id):
        """Delete a medication reminder"""
        return self.medication_reminder.delete_medication(user_id, medication_id)
    
    def record_medication_taken(self, user_id, medication_id, taken_at=None):
        """Record that a medication was taken"""
        return self.medication_reminder.record_medication_taken(user_id, medication_id, taken_at)
    
    def record_medication_missed(self, user_id, medication_id, missed_at=None):
        """Record that a medication was missed"""
        return self.medication_reminder.record_medication_missed(user_id, medication_id, missed_at)
    
    def get_adherence_rate(self, user_id, medication_id=None):
        """Get medication adherence rate"""
        return self.medication_reminder.get_adherence_rate(user_id, medication_id)
    
    def get_due_medications(self, user_id, hours_window=24):
        """Get medications due in the next time window"""
        return self.medication_reminder.get_due_medications(user_id, hours_window)
    
    def generate_medication_schedule_visualization(self, user_id, days=7):
        """Generate a visualization of the user's medication schedule"""
        medications = self.medication_reminder.get_user_medications(user_id)
        if not medications:
            return {"error": "No medications found for user"}
        
        # Generate schedule data
        schedule_data = {}
        import datetime
        today = datetime.datetime.now().date()
        
        for i in range(days):
            day = today + datetime.timedelta(days=i)
            day_str = day.strftime("%Y-%m-%d")
            schedule_data[day_str] = {}
            
            for med in medications:
                # Simple scheduling logic - can be enhanced based on frequency
                if med.get("frequency") == "daily":
                    schedule_data[day_str][med["name"]] = True
                elif med.get("frequency") == "weekly" and i % 7 == 0:
                    schedule_data[day_str][med["name"]] = True
                elif med.get("frequency") == "twice_daily":
                    schedule_data[day_str][f"{med['name']} (Morning)"] = True
                    schedule_data[day_str][f"{med['name']} (Evening)"] = True
        
        # Generate visualization
        description = f"Medication schedule for the next {days} days"
        try:
            # Convert to format expected by visualizer
            chart_data = []
            for day, meds in schedule_data.items():
                for med_name, scheduled in meds.items():
                    chart_data.append({
                        "Day": day,
                        "Medication": med_name,
                        "Scheduled": 1 if scheduled else 0
                    })
            
            image_path = self.visualizer.create_schedule_chart(
                data=chart_data,
                title=f"Medication Schedule - Next {days} Days",
                description=description
            )
            return {"path": image_path, "description": description, "data": schedule_data}
        except Exception as e:
            print(f"Error generating medication schedule visualization: {str(e)}")
            return {"error": str(e), "data": schedule_data}
    
    def get_medication_suggestions(self, condition, language=None):
        """Get medication suggestions for a medical condition (for educational purposes only)"""
        # Use specified language or default
        target_language = language or self.current_language
        
        prompt = (
            "You are a medical AI assistant providing EDUCATIONAL INFORMATION ONLY about medications. "
            "A user is asking about medications commonly used for: {condition}\n\n"
            "Provide educational information about:\n"
            "1. Classes of medications typically used for this condition\n"
            "2. Common examples within each class (generic names)\n"
            "3. General information about how these medications work\n"
            "4. Important considerations patients should know\n\n"
            "IMPORTANT: Make it absolutely clear this is educational information only and not a recommendation. "
            "Emphasize that medication decisions must be made by a qualified healthcare provider based on the "
            "individual's specific situation, medical history, and other factors."
        ).format(condition=condition)
        
        # Get AI response
        result = self._get_ai_response(prompt)
        
        # Add extra disclaimer for medication information
        med_disclaimer = (
            "MEDICATION INFORMATION DISCLAIMER: The information provided about medications is strictly "
            "for educational purposes. It is NOT a recommendation or prescription. Only a licensed healthcare "
            "provider who knows your medical history, current medications, allergies, and specific situation "
            "can recommend appropriate medications. Never start, stop, or change medications without consulting "
            "your healthcare provider."
        )
        
        # Translate if needed
        if target_language != 'en':
            result = self.language_manager.translate_medical_content(result, target_language)
            disclaimer = self.language_manager.translate_text(self.disclaimer, target_language)
            med_disclaimer = self.language_manager.translate_text(med_disclaimer, target_language)
            return f"{disclaimer}\n\n{med_disclaimer}\n\n{result}"
        else:
            return f"{self.disclaimer}\n\n{med_disclaimer}\n\n{result}"
    
    def generate_medication_report(self, user_id):
        """Generate a PDF report of the user's medications"""
        return self.medication_reminder.generate_medication_report(user_id) 