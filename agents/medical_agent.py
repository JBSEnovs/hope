import os
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_cohere import ChatCohere
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.combine_documents import create_stuff_documents_chain
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
            provider (str): The AI provider to use ('openai', 'cohere', 'google', or 'blackbox')
            model (str): Specific model to use, or None for default
        """
        # Set up the AI model based on provider
        self.provider = provider.lower()
        self.model_name = model
        self.llm = self._initialize_llm()
        
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
    
    def _initialize_llm(self):
        """Initialize the language model based on selected provider"""
        if self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            
            model = self.model_name or "gpt-4"
            return ChatOpenAI(
                model=model,
                temperature=0.2,
                api_key=api_key
            )
            
        elif self.provider == "cohere":
            api_key = os.getenv("COHERE_API_KEY")
            if not api_key:
                raise ValueError("COHERE_API_KEY environment variable is not set")
            
            model = self.model_name or "command"
            return ChatCohere(
                model=model,
                temperature=0.2,
                cohere_api_key=api_key
            )
            
        elif self.provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable is not set")
            
            model = self.model_name or "gemini-1.0-pro"
            return ChatGoogleGenerativeAI(
                model=model,
                temperature=0.2,
                google_api_key=api_key
            )
            
        elif self.provider == "blackbox":
            # Initialize BlackboxAI (no API key required for free version)
            self.blackbox_ai = BlackboxAI(model=self.model_name or "blackboxai")
            # Return None for LLM as we'll use the BlackboxAI agent directly
            return None
            
        else:
            raise ValueError(f"Unsupported provider: {self.provider}. Supported providers are 'openai', 'cohere', 'google', and 'blackbox'")
    
    def change_provider(self, provider, model=None):
        """Change the AI provider dynamically"""
        self.provider = provider.lower()
        self.model_name = model
        try:
            self.llm = self._initialize_llm()
            if provider.lower() == "blackbox" and model:
                self.blackbox_ai.change_model(model)
            return True
        except ValueError as e:
            print(f"Error changing provider: {str(e)}")
            return False
    
    def diagnose(self, symptoms, language=None):
        """Analyze symptoms and suggest possible diagnoses"""
        # Use specified language or default
        target_language = language or self.current_language
        
        if self.provider == "blackbox":
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
            
            result = self.blackbox_query(prompt)
            
            # Translate result if needed
            if target_language != 'en':
                result = self.language_manager.translate_medical_content(result, target_language)
                disclaimer = self.language_manager.translate_text(self.disclaimer, target_language)
                return f"{disclaimer}\n\n{result}"
            else:
                return f"{self.disclaimer}\n\n{result}"
        else:
            prompt = PromptTemplate.from_template(
                "You are a medical AI assistant. A patient describes the following symptoms: {symptoms}\n\n"
                "Based only on these symptoms, suggest possible conditions that might match these symptoms, "
                "organized from most to least likely. For each, include:\n"
                "1. The name of the condition\n"
                "2. Why it matches the symptoms\n"
                "3. What other symptoms might be present if this condition is correct\n"
                "4. What kind of medical professional should be consulted\n\n"
                "Remember to be thorough but emphasize the importance of consulting a healthcare professional for accurate diagnosis."
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.invoke({"symptoms": symptoms})
            
            # Translate result if needed
            if target_language != 'en':
                translated_result = self.language_manager.translate_medical_content(result['text'], target_language)
                disclaimer = self.language_manager.translate_text(self.disclaimer, target_language)
                return f"{disclaimer}\n\n{translated_result}"
            else:
                return f"{self.disclaimer}\n\n{result['text']}"
    
    def recommend_treatment(self, condition, language=None):
        """Provide information about treatment options for a condition"""
        # Use specified language or default
        target_language = language or self.current_language
        
        if self.provider == "blackbox":
            prompt = (
                "You are a medical AI assistant. A user is asking about treatment options for: {condition}\n\n"
                "Provide information about:\n"
                "1. Common evidence-based treatment approaches\n"
                "2. Lifestyle modifications that might help\n"
                "3. What type of healthcare provider typically manages this condition\n"
                "4. Important considerations patients should know\n\n"
                "Focus on providing balanced, evidence-based information while emphasizing the importance of personalized medical advice."
            ).format(condition=condition)
            
            result = self.blackbox_query(prompt)
            
            # Translate result if needed
            if target_language != 'en':
                result = self.language_manager.translate_medical_content(result, target_language)
                disclaimer = self.language_manager.translate_text(self.disclaimer, target_language)
                return f"{disclaimer}\n\n{result}"
            else:
                return f"{self.disclaimer}\n\n{result}"
        else:
            prompt = PromptTemplate.from_template(
                "You are a medical AI assistant. A user is asking about treatment options for: {condition}\n\n"
                "Provide information about:\n"
                "1. Common evidence-based treatment approaches\n"
                "2. Lifestyle modifications that might help\n"
                "3. What type of healthcare provider typically manages this condition\n"
                "4. Important considerations patients should know\n\n"
                "Focus on providing balanced, evidence-based information while emphasizing the importance of personalized medical advice."
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.invoke({"condition": condition})
            
            # Translate result if needed
            if target_language != 'en':
                translated_result = self.language_manager.translate_medical_content(result['text'], target_language)
                disclaimer = self.language_manager.translate_text(self.disclaimer, target_language)
                return f"{disclaimer}\n\n{translated_result}"
            else:
                return f"{self.disclaimer}\n\n{result['text']}"
    
    def research_disease(self, disease, language=None):
        """Provide latest research information about a disease"""
        # Use specified language or default
        target_language = language or self.current_language
        
        # First, check our document database for relevant information
        relevant_docs = self.doc_processor.search_documents(disease)
        
        if self.provider == "blackbox":
            # Create prompt for BlackboxAI
            if relevant_docs:
                context = "\n\n".join([f"Document from {doc.metadata.get('source', 'unknown source')}:\n{doc.page_content}" for doc in relevant_docs])
                prompt = (
                    "You are a medical AI assistant with access to medical knowledge and the following documents:\n\n"
                    "{context}\n\n"
                    "Based on these documents and your knowledge, provide information about: {disease}\n\n"
                    "Include information about:\n"
                    "1. Current understanding of causes/mechanisms\n"
                    "2. Recent research developments\n"
                    "3. Treatment advances\n"
                    "4. Areas of ongoing research\n\n"
                    "Focus on providing accurate, up-to-date information from reputable medical sources."
                ).format(disease=disease, context=context)
            else:
                prompt = (
                    "You are a medical AI assistant with access to medical knowledge. "
                    "Provide information about the latest understanding and research regarding: {disease}\n\n"
                    "Include information about:\n"
                    "1. Current understanding of causes/mechanisms\n"
                    "2. Recent research developments\n"
                    "3. Treatment advances\n"
                    "4. Areas of ongoing research\n\n"
                    "Focus on providing accurate, up-to-date information from reputable medical sources."
                ).format(disease=disease)
            
            result = self.blackbox_query(prompt)
            
            # Translate result if needed
            if target_language != 'en':
                result = self.language_manager.translate_medical_content(result, target_language)
                disclaimer = self.language_manager.translate_text(self.disclaimer, target_language)
                return f"{disclaimer}\n\n{result}"
            else:
                return f"{self.disclaimer}\n\n{result}"
        else:
            # Create a custom prompt that includes relevant document information if available
            if relevant_docs:
                prompt = PromptTemplate.from_template(
                    "You are a medical AI assistant with access to medical knowledge and the following documents:\n\n"
                    "{context}\n\n"
                    "Based on these documents and your knowledge, provide information about: {disease}\n\n"
                    "Include information about:\n"
                    "1. Current understanding of causes/mechanisms\n"
                    "2. Recent research developments\n"
                    "3. Treatment advances\n"
                    "4. Areas of ongoing research\n\n"
                    "Focus on providing accurate, up-to-date information from reputable medical sources."
                )
                
                # Format the document content
                context = "\n\n".join([f"Document from {doc.metadata.get('source', 'unknown source')}:\n{doc.page_content}" for doc in relevant_docs])
                
                # Use the stuff documents chain when we have relevant docs
                doc_chain = create_stuff_documents_chain(self.llm, prompt)
                result = doc_chain.invoke({"disease": disease, "context": context})
                
            else:
                # Use standard prompt when no relevant docs are found
                prompt = PromptTemplate.from_template(
                    "You are a medical AI assistant with access to medical knowledge. "
                    "Provide information about the latest understanding and research regarding: {disease}\n\n"
                    "Include information about:\n"
                    "1. Current understanding of causes/mechanisms\n"
                    "2. Recent research developments\n"
                    "3. Treatment advances\n"
                    "4. Areas of ongoing research\n\n"
                    "Focus on providing accurate, up-to-date information from reputable medical sources."
                )
                
                chain = LLMChain(llm=self.llm, prompt=prompt)
                result = chain.invoke({"disease": disease})
            
            # Translate result if needed
            if target_language != 'en':
                translated_result = self.language_manager.translate_medical_content(result['text'], target_language)
                disclaimer = self.language_manager.translate_text(self.disclaimer, target_language)
                return f"{disclaimer}\n\n{translated_result}"
            else:
                return f"{self.disclaimer}\n\n{result['text']}"
    
    def blackbox_query(self, query, conversation_id=None):
        """
        Send a direct query to BlackboxAI
        
        Args:
            query (str): The query text
            conversation_id (str, optional): Existing conversation ID
            
        Returns:
            str: BlackboxAI response text
        """
        if conversation_id:
            result = self.blackbox_ai.continue_conversation(conversation_id, query)
        else:
            result = self.blackbox_ai.send_message(query)
        
        if result.get('success', False):
            return result.get('response', 'No response from BlackboxAI')
        else:
            raise ValueError(f"BlackboxAI error: {result.get('error', 'Unknown error')}")
    
    def get_blackbox_models(self):
        """
        Get available models for BlackboxAI
        
        Returns:
            list: Available model names
        """
        return self.blackbox_ai.get_available_models()
    
    def upload_document(self, file_content, file_name):
        """Process and store a medical document for future reference"""
        return self.doc_processor.process_file(file_content, file_name)
    
    def get_uploaded_documents(self):
        """Get a list of all uploaded document sources"""
        return self.doc_processor.get_document_sources()
    
    def generate_symptom_visualization(self, symptoms_data, title="Common Symptoms"):
        """Generate a visualization of symptom frequencies"""
        data = self.visualizer.parse_symptoms_data(symptoms_data)
        if not data['labels']:
            return None
            
        return {
            "type": "bar",
            "image": self.visualizer.create_bar_chart(
                data,
                title=title,
                x_label="Symptoms",
                y_label="Frequency (%)"
            )
        }
    
    def generate_treatment_visualization(self, treatment_data, title="Treatment Efficacy"):
        """Generate a visualization of treatment efficacy"""
        data = self.visualizer.parse_treatment_efficacy(treatment_data)
        if not data['labels']:
            return None
            
        return {
            "type": "pie",
            "data": self.visualizer.create_pie_chart(
                data,
                title=title
            )
        }
    
    def generate_progression_visualization(self, progression_data, title="Disease Progression", 
                                          x_label="Time", y_label="Metric"):
        """Generate a visualization of disease progression over time"""
        data = self.visualizer.parse_time_series_data(progression_data)
        if not data['x_values'] or not data['series']:
            return None
            
        return {
            "type": "line",
            "data": self.visualizer.create_line_chart(
                data,
                title=title,
                x_label=x_label,
                y_label=y_label
            )
        }
        
    def extract_visualization_data(self, text, data_type="symptoms"):
        """Extract structured data for visualization from text"""
        prompt_templates = {
            "symptoms": (
                "Based on the following medical information, extract a list of symptoms and their "
                "approximate frequencies (in percentage). Format each symptom on a new line as 'Symptom: X%'.\n\n"
                "Medical information:\n{text}\n\n"
                "List of symptoms and frequencies (estimates are acceptable if exact percentages aren't provided):"
            ),
            "treatments": (
                "Based on the following treatment information, extract a list of treatments and their "
                "efficacy rates (in percentage). Format each treatment on a new line as 'Treatment: X%'.\n\n"
                "Treatment information:\n{text}\n\n"
                "List of treatments and efficacy rates (estimates are acceptable if exact percentages aren't provided):"
            ),
            "progression": (
                "Based on the following disease information, extract time series data showing disease progression "
                "metrics over time. Format the data as follows, with one time point per line:\n"
                "Date: YYYY, Metric1: X, Metric2: Y\n\n"
                "Disease information:\n{text}\n\n"
                "Time series progression data:"
            )
        }
        
        if data_type not in prompt_templates:
            return None
            
        prompt = PromptTemplate.from_template(prompt_templates[data_type])
        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.invoke({"text": text})
        
        return result['text']
    
    # Image analysis methods
    def analyze_medical_image(self, image_data, enhancement=None):
        """Analyze a medical image and return findings with AI interpretation"""
        # First, get basic image analysis from the image analyzer
        analysis_result = self.image_analyzer.analyze_image(image_data, enhancement)
        
        if not analysis_result.get('success', False):
            return analysis_result
        
        # Now use LLM to interpret the findings and provide additional context
        try:
            metrics = analysis_result.get('image_metrics', {})
            metrics_text = "\n".join([f"{k}: {v}" for k, v in metrics.items()])
            
            prompt = PromptTemplate.from_template(
                "You are a medical AI assistant analyzing an image with the following metrics:\n\n"
                "{metrics}\n\n"
                "Based on these metrics and general medical imaging knowledge, provide a general interpretation "
                "of what these values might indicate. Note that this is a preliminary analysis and should not be "
                "considered a medical diagnosis.\n\n"
                "Include the following in your analysis:\n"
                "1. General interpretation of the image metrics\n"
                "2. Potential relevance to medical imaging\n"
                "3. Clear disclaimer about the limitations of AI image analysis\n\n"
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.invoke({"metrics": metrics_text})
            
            # Add AI interpretation to the analysis result
            analysis_result['ai_interpretation'] = result['text']
            analysis_result['disclaimer'] = self.disclaimer
            
            return analysis_result
            
        except Exception as e:
            print(f"Error in AI interpretation of image: {e}")
            analysis_result['ai_interpretation'] = "AI interpretation unavailable due to an error."
            analysis_result['disclaimer'] = self.disclaimer
            return analysis_result
    
    def enhance_medical_image(self, image_data, enhancement_type):
        """Apply specified enhancement to a medical image"""
        return self.image_analyzer.enhance_image(image_data, enhancement_type)
    
    def get_available_image_enhancements(self):
        """Get available image enhancement options"""
        return self.image_analyzer.get_available_enhancements()
    
    # Voice interface methods
    def transcribe_voice_input(self, audio_data, language='en-US'):
        """Transcribe voice input to text"""
        return self.voice_interface.transcribe_audio(audio_data, language)
    
    def generate_voice_response(self, text, voice_type=None):
        """Generate speech from text response"""
        return self.voice_interface.synthesize_speech(text, voice_type)
    
    def extract_medical_terms_from_speech(self, text):
        """Extract medical terms from transcribed speech"""
        return self.voice_interface.extract_medical_terms(text)
    
    def get_supported_languages(self):
        """Get list of supported languages for voice recognition"""
        return self.voice_interface.get_supported_languages()
    
    # Collaboration methods
    def create_consultation_session(self, patient_id, session_type="consultation"):
        """Create a new collaboration session"""
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
        """Get active consultation sessions"""
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
        """Get user by ID"""
        user = self.user_manager.get_user(user_id)
        if user:
            # Convert to dict and remove sensitive data
            user_dict = user.to_dict()
            if 'password_hash' in user_dict.get('profile', {}):
                del user_dict['profile']['password_hash']
            return {'success': True, 'user': user_dict}
        return {'success': False, 'error': 'User not found'}
    
    def update_user_profile(self, user_id, data):
        """Update user profile"""
        return self.user_manager.update_user(user_id, data)
    
    def change_user_password(self, user_id, current_password, new_password):
        """Change user password"""
        return self.user_manager.change_password(user_id, current_password, new_password)
    
    def change_language(self, language_code):
        """
        Change the current language 
        
        Args:
            language_code (str): ISO 639-1 language code
        
        Returns:
            bool: Success status
        """
        if language_code in self.language_manager.supported_languages:
            self.current_language = language_code
            return True
        return False
    
    def get_supported_languages(self):
        """
        Get available languages 
        
        Returns:
            dict: Dictionary of language codes and names
        """
        return self.language_manager.get_supported_languages()
    
    def detect_language(self, text):
        """
        Detect language of text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Language code
        """
        return self.language_manager.detect_language(text)
    
    def translate_text(self, text, target_language=None):
        """
        Translate text to target language
        
        Args:
            text (str): Text to translate
            target_language (str): Target language code
            
        Returns:
            str: Translated text
        """
        return self.language_manager.translate_text(text, target_language or self.current_language)
    
    # Medication reminder methods
    def get_user_medications(self, user_id):
        """Get all medications for a user"""
        return self.medication_reminder.get_user_medications(user_id)
    
    def add_medication(self, user_id, name, dosage, frequency, start_date, end_date=None, notes=None):
        """Add a new medication reminder"""
        return self.medication_reminder.add_medication(
            user_id, name, dosage, frequency, start_date, end_date, notes
        )
    
    def update_medication(self, user_id, medication_id, updates):
        """Update an existing medication reminder"""
        return self.medication_reminder.update_medication(user_id, medication_id, updates)
    
    def delete_medication(self, user_id, medication_id):
        """Delete a medication reminder"""
        return self.medication_reminder.delete_medication(user_id, medication_id)
    
    def record_medication_taken(self, user_id, medication_id, taken_at=None):
        """Record that a medication dose was taken"""
        return self.medication_reminder.record_medication_taken(user_id, medication_id, taken_at)
    
    def record_medication_missed(self, user_id, medication_id, missed_at=None):
        """Record that a medication dose was missed"""
        return self.medication_reminder.record_medication_missed(user_id, medication_id, missed_at)
    
    def get_adherence_rate(self, user_id, medication_id=None):
        """Calculate medication adherence rate"""
        return self.medication_reminder.get_adherence_rate(user_id, medication_id)
    
    def get_due_medications(self, user_id, hours_window=24):
        """Get medications due within the specified time window"""
        return self.medication_reminder.get_due_medications(user_id, hours_window)
    
    def generate_medication_schedule_visualization(self, user_id, days=7):
        """
        Generate a visualization of upcoming medication schedule
        
        Args:
            user_id (str): User ID
            days (int): Number of days to include in schedule
            
        Returns:
            dict: Visualization data
        """
        medications = self.medication_reminder.get_user_medications(user_id)
        
        if not medications:
            return None
        
        # Group medications by day and time
        schedule_data = {}
        current_date = datetime.now().date()
        
        for day in range(days):
            target_date = current_date + timedelta(days=day)
            date_str = target_date.strftime('%Y-%m-%d')
            schedule_data[date_str] = []
            
            for med in medications:
                start_date = datetime.fromisoformat(med["start_date"].replace('Z', '+00:00')).date()
                
                if med["end_date"]:
                    end_date = datetime.fromisoformat(med["end_date"].replace('Z', '+00:00')).date()
                    if target_date < start_date or target_date > end_date:
                        continue
                elif target_date < start_date:
                    continue
                
                # Add to schedule based on frequency
                frequency = med["frequency"].lower()
                
                if "daily" in frequency:
                    schedule_data[date_str].append(med)
                elif "every" in frequency and "hour" in frequency:
                    schedule_data[date_str].append(med)
                elif "weekly" in frequency:
                    # Check if this is the right day of the week
                    if start_date.weekday() == target_date.weekday():
                        schedule_data[date_str].append(med)
                elif "monthly" in frequency:
                    # Check if this is the right day of the month
                    if start_date.day == target_date.day:
                        schedule_data[date_str].append(med)
                else:
                    # For other frequencies, include anyway
                    schedule_data[date_str].append(med)
        
        # Create visualization data
        formatted_data = {
            "dates": list(schedule_data.keys()),
            "medications": []
        }
        
        for med in medications:
            med_data = {
                "name": med["name"],
                "schedule": []
            }
            
            for date in formatted_data["dates"]:
                if med in schedule_data[date]:
                    med_data["schedule"].append(1)
                else:
                    med_data["schedule"].append(0)
            
            formatted_data["medications"].append(med_data)
        
        # Generate visualization using data visualizer
        return self.visualizer.create_medication_schedule_chart(formatted_data)
        
    def get_medication_suggestions(self, condition, language=None):
        """
        Get medication suggestions for a condition (for informational purposes only)
        
        Args:
            condition (str): Medical condition
            language (str, optional): Language code
            
        Returns:
            dict: Medication suggestions
        """
        target_language = language or self.current_language
        
        if self.provider == "blackbox":
            prompt = (
                "You are a medical AI assistant. A user has the following medical condition: {condition}\n\n"
                "Please provide a list of medications commonly prescribed for this condition. For each medication, include:\n"
                "1. Generic name\n"
                "2. Common brand names (if applicable)\n"
                "3. Typical dosage range\n"
                "4. Common side effects\n"
                "5. Important warnings or contraindications\n\n"
                "Format the response as a structured list. Begin with a clear disclaimer that this information is for "
                "educational purposes only and not a substitute for professional medical advice or prescription."
            ).format(condition=condition)
            
            result = self.blackbox_query(prompt)
            
            # Translate result if needed
            if target_language != 'en':
                result = self.language_manager.translate_medical_content(result, target_language)
                
            return {
                "success": True,
                "suggestions": result,
                "disclaimer": self.disclaimer
            }
        else:
            prompt = PromptTemplate.from_template(
                "You are a medical AI assistant. A user has the following medical condition: {condition}\n\n"
                "Please provide a list of medications commonly prescribed for this condition. For each medication, include:\n"
                "1. Generic name\n"
                "2. Common brand names (if applicable)\n"
                "3. Typical dosage range\n"
                "4. Common side effects\n"
                "5. Important warnings or contraindications\n\n"
                "Format the response as a structured list. Begin with a clear disclaimer that this information is for "
                "educational purposes only and not a substitute for professional medical advice or prescription."
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            result = chain.invoke({"condition": condition})
            
            # Translate result if needed
            if target_language != 'en':
                translated_result = self.language_manager.translate_medical_content(result['text'], target_language)
                
                return {
                    "success": True,
                    "suggestions": translated_result,
                    "disclaimer": self.language_manager.translate_text(self.disclaimer, target_language)
                }
            else:
                return {
                    "success": True,
                    "suggestions": result['text'],
                    "disclaimer": self.disclaimer
                }
    
    def generate_medication_report(self, user_id):
        """
        Generate a comprehensive PDF report of user medications
        
        Args:
            user_id (str): User ID
            
        Returns:
            bytes: PDF report as bytes or None if failed
        """
        return self.medication_reminder.generate_medication_report(user_id) 