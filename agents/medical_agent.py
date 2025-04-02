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
    
    def diagnose(self, symptoms):
        """Analyze symptoms and suggest possible diagnoses"""
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
            
            return f"{self.disclaimer}\n\n{result['text']}"
    
    def recommend_treatment(self, condition):
        """Provide information about treatment options for a condition"""
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
            
            return f"{self.disclaimer}\n\n{result['text']}"
    
    def research_disease(self, disease):
        """Provide latest research information about a disease"""
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