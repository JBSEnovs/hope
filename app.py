import os
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, make_response
from dotenv import load_dotenv
from agents.medical_agent import MedicalAgent
from agents.auth import User, UserManager
from werkzeug.utils import secure_filename
from agents.document_processor import DocumentProcessor
from agents.data_visualizer import DataVisualizer
from agents.image_analyzer import MedicalImageAnalyzer
from agents.voice_interface import VoiceInterface
from agents.collaboration import CollaborationManager
from agents.blackbox_ai import BlackboxAI
from agents.language import LanguageManager
from agents.medication_reminder import MedicationReminder
from agents.email_service import EmailService, mail
from agents.reminder_scheduler import ReminderScheduler
from functools import wraps
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
# Enable CORS for all routes - this helps prevent CORS errors
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'temp_uploads')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key_change_in_production')

# Configure Flask-Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL', 'False') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'no-reply@medicalai.example.com')
app.config['APP_URL'] = os.getenv('APP_URL', 'http://localhost:5000')

# Initialize mail extension
mail.init_app(app)

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data/documents', exist_ok=True)
os.makedirs('data/images', exist_ok=True)
os.makedirs('data/audio', exist_ok=True)
os.makedirs('data/sessions', exist_ok=True)
os.makedirs('data/users', exist_ok=True)
os.makedirs('data/medications', exist_ok=True)

# Initialize components
medical_agent = MedicalAgent()
doc_processor = DocumentProcessor()
data_visualizer = DataVisualizer()
image_analyzer = MedicalImageAnalyzer()
voice_interface = VoiceInterface()
collaboration_manager = CollaborationManager()
user_manager = UserManager()
blackbox_ai = BlackboxAI()
language_manager = LanguageManager()
medication_reminder = MedicationReminder()
email_service = EmailService(app)
reminder_scheduler = ReminderScheduler(app, user_manager, medication_reminder, email_service)

@app.route('/')
def index():
    return render_template('welcome.html')

# API routes - remove authentication requirement
@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    data = request.json
    symptoms = data.get('symptoms', '')
    
    try:
        diagnosis = medical_agent.diagnose(symptoms)
        
        # If visualization data is requested
        include_vis = data.get('include_visualization', False)
        visualization = None
        
        if include_vis:
            # Extract structured symptom data
            symptom_data = medical_agent.extract_visualization_data(diagnosis, data_type="symptoms")
            visualization = medical_agent.generate_symptom_visualization(symptom_data)
        
        response = {"result": diagnosis}
        if visualization:
            response["visualization"] = visualization
            
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/treatment', methods=['POST'])
def treatment():
    data = request.json
    condition = data.get('condition', '')
    
    try:
        treatment = medical_agent.recommend_treatment(condition)
        
        # If visualization data is requested
        include_vis = data.get('include_visualization', False)
        visualization = None
        
        if include_vis:
            # Extract structured treatment data
            treatment_data = medical_agent.extract_visualization_data(treatment, data_type="treatments")
            visualization = medical_agent.generate_treatment_visualization(treatment_data)
        
        response = {"result": treatment}
        if visualization:
            response["visualization"] = visualization
            
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/research', methods=['POST'])
def research():
    data = request.json
    disease = data.get('disease', '')
    
    try:
        research_info = medical_agent.research_disease(disease)
        
        # If visualization data is requested
        include_vis = data.get('include_visualization', False)
        visualization = None
        
        if include_vis:
            # Extract structured progression data
            progression_data = medical_agent.extract_visualization_data(research_info, data_type="progression")
            visualization = medical_agent.generate_progression_visualization(progression_data)
        
        response = {"result": research_info}
        if visualization:
            response["visualization"] = visualization
            
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload_document', methods=['POST'])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file:
        try:
            # Read file content
            file_content = file.read()
            file_name = secure_filename(file.filename)
            
            # Process the document
            result = medical_agent.upload_document(file_content, file_name)
            
            if result.get('success', False):
                return jsonify({
                    "success": True,
                    "message": f"Successfully processed document: {file_name}",
                    "details": result
                })
            else:
                return jsonify({
                    "success": False,
                    "error": result.get('error', 'Unknown error processing document')
                }), 500
                
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def get_documents():
    try:
        documents = medical_agent.get_uploaded_documents()
        return jsonify({"documents": documents})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/change_provider', methods=['POST'])
def change_provider():
    data = request.json
    provider = data.get('provider', '')
    model = data.get('model', None)
    
    if not provider:
        return jsonify({"error": "Provider name is required"}), 400
    
    try:
        success = medical_agent.change_provider(provider, model)
        if success:
            return jsonify({"result": f"Successfully changed provider to {provider}" + (f" with model {model}" if model else "")})
        else:
            return jsonify({"error": "Failed to change provider"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/providers', methods=['GET'])
def providers():
    """Returns available providers and their default models"""
    try:
        blackbox_models = medical_agent.get_blackbox_models() or ["blackboxai"]
    except Exception as e:
        print(f"Error getting blackbox models: {e}")
        blackbox_models = ["blackboxai"]
        
    providers = {
        "openai": {
            "default_model": "gpt-4",
            "available_models": ["gpt-4", "gpt-3.5-turbo"]
        },
        # Removed cohere due to Python 3.13 compatibility issues
        "google": {
            "default_model": "gemini-1.0-pro",
            "available_models": ["gemini-1.0-pro", "gemini-1.5-pro"]
        },
        "blackbox": {
            "default_model": "blackboxai",
            "available_models": blackbox_models
        }
    }
    
    return jsonify(providers)

# Image Analysis Endpoints
@app.route('/api/analyze_image', methods=['POST'])
def analyze_image():
    data = request.json
    image_data = data.get('image_data', '')
    enhancement = data.get('enhancement', None)
    
    if not image_data:
        return jsonify({'error': 'No image data provided'}), 400
    
    # Remove data URL prefix if present
    if image_data.startswith('data:image'):
        image_data = image_data.split(',')[1]
    
    try:
        result = medical_agent.analyze_medical_image(image_data, enhancement)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/enhance_image', methods=['POST'])
def enhance_image():
    data = request.json
    image_data = data.get('image_data', '')
    enhancement_type = data.get('enhancement_type', '')
    
    if not image_data or not enhancement_type:
        return jsonify({'error': 'Missing image data or enhancement type'}), 400
    
    # Remove data URL prefix if present
    if image_data.startswith('data:image'):
        image_data = image_data.split(',')[1]
    
    try:
        result = medical_agent.enhance_medical_image(image_data, enhancement_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/image_enhancements', methods=['GET'])
def get_image_enhancements():
    try:
        enhancements = medical_agent.get_available_image_enhancements()
        return jsonify({'enhancements': enhancements})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Voice Interface Endpoints
@app.route('/api/transcribe_audio', methods=['POST'])
def transcribe_audio():
    data = request.json
    audio_data = data.get('audio_data', '')
    language = data.get('language', 'en-US')
    
    if not audio_data:
        return jsonify({'error': 'No audio data provided'}), 400
    
    # Remove data URL prefix if present
    if audio_data.startswith('data:audio'):
        audio_data = audio_data.split(',')[1]
    
    try:
        result = medical_agent.transcribe_voice_input(audio_data, language)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/synthesize_speech', methods=['POST'])
def synthesize_speech():
    data = request.json
    text = data.get('text', '')
    voice_type = data.get('voice_type', None)
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        result = medical_agent.generate_voice_response(text, voice_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/supported_languages', methods=['GET'])
def get_supported_languages():
    try:
        languages = medical_agent.get_supported_languages()
        return jsonify({'languages': languages})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Collaboration Endpoints
@app.route('/api/create_consultation', methods=['POST'])
def create_consultation():
    data = request.json
    session_type = data.get('session_type', 'consultation')
    
    try:
        result = medical_agent.create_consultation_session(current_user.id, session_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/join_consultation/<session_id>', methods=['POST'])
def join_consultation(session_id):
    data = request.json
    role = data.get('role', 'doctor' if current_user.get_role() == 'doctor' else 'patient')
    
    try:
        result = medical_agent.join_consultation(session_id, current_user.id, role)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/leave_consultation/<session_id>', methods=['POST'])
def leave_consultation(session_id):
    try:
        result = medical_agent.leave_consultation(session_id, current_user.id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/send_message/<session_id>', methods=['POST'])
def send_consultation_message(session_id):
    data = request.json
    content = data.get('content', '')
    message_type = data.get('message_type', 'text')
    
    if not content:
        return jsonify({'error': 'No message content provided'}), 400
    
    try:
        result = medical_agent.send_consultation_message(session_id, current_user.id, content, message_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/get_messages/<session_id>', methods=['GET'])
def get_consultation_messages(session_id):
    since = request.args.get('since', None)
    if since:
        since = int(since)
    
    try:
        result = medical_agent.get_consultation_messages(session_id, since)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/active_consultations', methods=['GET'])
def get_active_consultations():
    try:
        result = medical_agent.get_active_consultations(current_user.id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/end_consultation/<session_id>', methods=['POST'])
def end_consultation(session_id):
    try:
        result = medical_agent.end_consultation(session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# User Profile Endpoints
@app.route('/api/user_profile', methods=['GET'])
def get_user_profile():
    try:
        user_data = get_default_user()
        return jsonify({
            'success': True,
            'user': user_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/update_profile', methods=['POST'])
def update_user_profile():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        result = medical_agent.update_user_profile(current_user.id, data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/change_password', methods=['POST'])
def change_password():
    data = request.json
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Missing password information'}), 400
    
    try:
        result = medical_agent.change_user_password(current_user.id, current_password, new_password)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# BlackboxAI Endpoints
@app.route('/api/blackbox/query', methods=['POST'])
def blackbox_query():
    data = request.json
    query = data.get('query', '')
    conversation_id = data.get('conversation_id', None)
    model = data.get('model', None)
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    # Save current provider
    current_provider = medical_agent.provider
    current_model = medical_agent.model_name
    
    try:
        # Temporarily switch to BlackboxAI provider
        if current_provider != "blackbox":
            medical_agent.change_provider("blackbox", model)
        elif model and model != medical_agent.blackbox_ai.model:
            medical_agent.blackbox_ai.change_model(model)
        
        # Send query to BlackboxAI
        response_data = {}
        if conversation_id:
            # Continue existing conversation
            result = medical_agent.blackbox_ai.continue_conversation(conversation_id, query)
            response_data['conversation_id'] = conversation_id
        else:
            # Start new conversation
            result = medical_agent.blackbox_ai.send_message(query)
            response_data['conversation_id'] = result.get('conversation_id') if result.get('success', False) else None
        
        # Restore original provider if needed
        if current_provider != "blackbox":
            medical_agent.change_provider(current_provider, current_model)
        
        # Build response
        if result.get('success', False):
            response_data['success'] = True
            response_data['response'] = result.get('response')
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Unknown error')}), 500
        
        return jsonify(response_data)
        
    except Exception as e:
        # Restore original provider if needed
        if current_provider != "blackbox":
            medical_agent.change_provider(current_provider, current_model)
        
        return jsonify({"error": str(e)}), 500

@app.route('/api/blackbox/models', methods=['GET'])
def blackbox_models():
    try:
        models = medical_agent.get_blackbox_models()
        return jsonify({'models': models})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Language Management Endpoints
@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get supported languages"""
    try:
        languages = medical_agent.get_supported_languages()
        return jsonify({"languages": languages})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/set_language', methods=['POST'])
def set_language():
    """Set preferred language for a user"""
    data = request.json
    language_code = data.get('language_code', 'en')
    
    try:
        success = medical_agent.change_language(language_code)
        if success:
            # Also store the language preference in user's profile
            user_profile = {"preferred_language": language_code}
            medical_agent.update_user_profile(current_user.id, user_profile)
            return jsonify({"result": f"Language set to {language_code}"})
        else:
            return jsonify({"error": "Invalid language code"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate_text():
    """Translate text to selected language"""
    data = request.json
    text = data.get('text', '')
    target_language = data.get('target_language', None)
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        translated_text = medical_agent.translate_text(text, target_language)
        return jsonify({"result": translated_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/detect_language', methods=['POST'])
def detect_language():
    """Detect language of text"""
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        detected_language = medical_agent.detect_language(text)
        return jsonify({"language_code": detected_language})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add routes for multilingual versions of existing endpoints
@app.route('/api/diagnose_translated', methods=['POST'])
def diagnose_translated():
    """Analyze symptoms and return results in user's preferred language"""
    data = request.json
    symptoms = data.get('symptoms', '')
    language = data.get('language', None)
    
    if not symptoms:
        return jsonify({"error": "No symptoms provided"}), 400
    
    try:
        diagnosis = medical_agent.diagnose(symptoms, language)
        
        # If visualization data is requested
        include_vis = data.get('include_visualization', False)
        visualization = None
        
        if include_vis:
            # Extract structured symptom data
            symptom_data = medical_agent.extract_visualization_data(diagnosis, data_type="symptoms")
            visualization = medical_agent.generate_symptom_visualization(symptom_data)
        
        response = {"result": diagnosis}
        if visualization:
            response["visualization"] = visualization
            
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/treatment_translated', methods=['POST'])
def treatment_translated():
    """Get treatment information in user's preferred language"""
    data = request.json
    condition = data.get('condition', '')
    language = data.get('language', None)
    
    if not condition:
        return jsonify({"error": "No condition provided"}), 400
    
    try:
        treatment = medical_agent.recommend_treatment(condition, language)
        
        # If visualization data is requested
        include_vis = data.get('include_visualization', False)
        visualization = None
        
        if include_vis:
            # Extract structured treatment data
            treatment_data = medical_agent.extract_visualization_data(treatment, data_type="treatments")
            visualization = medical_agent.generate_treatment_visualization(treatment_data)
        
        response = {"result": treatment}
        if visualization:
            response["visualization"] = visualization
            
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/research_translated', methods=['POST'])
def research_translated():
    """Get disease research information in user's preferred language"""
    data = request.json
    disease = data.get('disease', '')
    language = data.get('language', None)
    
    if not disease:
        return jsonify({"error": "No disease provided"}), 400
    
    try:
        research_info = medical_agent.research_disease(disease, language)
        
        # If visualization data is requested
        include_vis = data.get('include_visualization', False)
        visualization = None
        
        if include_vis:
            # Extract structured progression data
            progression_data = medical_agent.extract_visualization_data(research_info, data_type="progression")
            visualization = medical_agent.generate_progression_visualization(progression_data)
        
        response = {"result": research_info}
        if visualization:
            response["visualization"] = visualization
            
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Language UI routes
@app.route('/language', methods=['GET'])
def language_settings():
    """Language settings page"""
    return render_template('language.html')

# New chatbot UI route
@app.route('/chatbot', methods=['GET'])
def chatbot():
    """AI chatbot interface"""
    return render_template('chatbot.html')

# User dashboard route
@app.route('/dashboard', methods=['GET'])
def dashboard():
    """User health dashboard"""
    # Get user profile information
    user_id = get_default_user()['id']
    user_result = medical_agent.get_user(user_id)
    
    if user_result.get('success', False):
        user_profile = user_result.get('user', {})
        # Get recent consultations (placeholder data for now)
        consultations = []  # In a real app, this would fetch from the database
        
        return render_template('dashboard.html', user_profile=user_profile, consultations=consultations)
    else:
        flash('Error loading user profile', 'danger')
        return redirect(url_for('index'))

@app.route('/medications', methods=['GET'])
def medications_page():
    """Render the medications management page"""
    return render_template('medications.html')

@app.route('/api/medications', methods=['GET'])
def get_medications():
    """Get all medications for the default user"""
    try:
        user_id = get_default_user()['id']
        medications = medication_reminder.get_user_medications(user_id)
        return jsonify({
            'success': True,
            'medications': medications
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/medications', methods=['POST'])
def add_medication():
    """Add a new medication reminder"""
    data = request.json
    
    name = data.get('name')
    dosage = data.get('dosage')
    frequency = data.get('frequency')
    start_date = data.get('start_date')
    end_date = data.get('end_date', None)
    notes = data.get('notes', None)
    
    user_id = get_default_user()['id']
    
    try:
        result = medication_reminder.add_medication(
            user_id, name, dosage, frequency, start_date, end_date, notes
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/medications/<medication_id>', methods=['GET'])
def get_medication(medication_id):
    """Get details for a specific medication"""
    user_id = get_default_user()['id']
    
    try:
        medication = medication_reminder.get_medication(user_id, medication_id)
        if medication:
            return jsonify({
                'success': True,
                'medication': medication
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Medication not found'
            }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/medications/<medication_id>', methods=['DELETE'])
def delete_medication(medication_id):
    """Delete a medication reminder"""
    user_id = get_default_user()['id']
    
    try:
        result = medication_reminder.delete_medication(user_id, medication_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/medications/<medication_id>/<status>', methods=['POST'])
def record_medication_status(medication_id, status):
    """Record medication as taken or missed"""
    user_id = get_default_user()['id']
    
    try:
        if status == 'taken':
            result = medication_reminder.record_medication_taken(user_id, medication_id)
        elif status == 'missed':
            result = medication_reminder.record_medication_missed(user_id, medication_id)
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid status. Use "taken" or "missed".'
            }), 400
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/medications/due', methods=['GET'])
def get_due_medications():
    """Get medications due within the next 24 hours"""
    user_id = get_default_user()['id']
    hours = request.args.get('hours', 24, type=int)
    
    try:
        medications = medication_reminder.get_due_medications(user_id, hours)
        return jsonify({
            'success': True,
            'medications': medications
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/medications/schedule/visualization', methods=['GET'])
def get_medication_schedule_visualization():
    """Get a visualization of the user's medication schedule"""
    user_id = get_default_user()['id']
    days = request.args.get('days', 7, type=int)
    
    try:
        result = medical_agent.generate_medication_schedule_visualization(user_id, days)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/medications/suggestions', methods=['POST'])
def get_medication_suggestions():
    """Get medication suggestions for a condition (for educational purposes only)"""
    data = request.json
    condition = data.get('condition', '')
    language = data.get('language')
    
    if not condition:
        return jsonify({
            'success': False,
            'error': 'Condition is required'
        }), 400
    
    suggestions = medical_agent.get_medication_suggestions(condition, language)
    
    return jsonify(suggestions)

@app.route('/api/medications/report', methods=['GET'])
def generate_medication_report():
    """Generate a PDF report of the user's medications"""
    user_id = get_default_user()['id']
    
    try:
        result = medical_agent.generate_medication_report(user_id)
        if result.get('success'):
            report_path = result.get('report_path')
            return send_from_directory(
                os.path.dirname(report_path),
                os.path.basename(report_path),
                as_attachment=True,
                download_name="medication_report.pdf"
            )
        else:
            return jsonify(result), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Health Analytics API Endpoints
@app.route('/api/analytics/adherence', methods=['GET'])
def get_adherence_analytics():
    """Get adherence analytics data for the current user"""
    user_id = get_default_user()['id']
    
    try:
        # Get adherence data from medication reminder
        adherence_rate = medication_reminder.get_adherence_rate(user_id)
        medications = medication_reminder.get_user_medications(user_id)
        
        # Calculate statistics
        total_meds = len(medications)
        taken_count = 0
        missed_count = 0
        
        for med in medications:
            history = med.get('history', [])
            for event in history:
                if event.get('status') == 'taken':
                    taken_count += 1
                elif event.get('status') == 'missed':
                    missed_count += 1
        
        # Calculate upcoming doses (placeholder logic)
        upcoming_count = total_meds * 2  # Simplified calculation
        
        return jsonify({
            'success': True,
            'adherence_rate': adherence_rate,
            'statistics': {
                'taken': taken_count,
                'missed': missed_count,
                'upcoming': upcoming_count,
                'total_medications': total_meds
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics/health_metrics', methods=['GET'])
def get_health_metrics():
    """Get health metrics data for the current user"""
    user_id = get_default_user()['id']
    
    try:
        # This would normally fetch from a database
        # Using placeholder data for now
        metrics = {
            'blood_pressure': [
                {'date': '2025-01-01', 'value': 120},
                {'date': '2025-02-01', 'value': 122},
                {'date': '2025-03-01', 'value': 119},
                {'date': '2025-04-01', 'value': 118},
                {'date': '2025-05-01', 'value': 121},
                {'date': '2025-06-01', 'value': 117}
            ],
            'blood_glucose': [
                {'date': '2025-01-01', 'value': 95},
                {'date': '2025-02-01', 'value': 97},
                {'date': '2025-03-01', 'value': 94},
                {'date': '2025-04-01', 'value': 98},
                {'date': '2025-05-01', 'value': 92},
                {'date': '2025-06-01', 'value': 95}
            ],
            'weight': [
                {'date': '2025-01-01', 'value': 70},
                {'date': '2025-02-01', 'value': 71},
                {'date': '2025-03-01', 'value': 70.5},
                {'date': '2025-04-01', 'value': 70},
                {'date': '2025-05-01', 'value': 69},
                {'date': '2025-06-01', 'value': 68.5}
            ]
        }
        
        return jsonify({
            'success': True,
            'metrics': metrics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics/health_activities', methods=['GET'])
def get_health_activities():
    """Get recent and upcoming health activities for the current user"""
    user_id = get_default_user()['id']
    
    try:
        # Placeholder data - in a real app, this would come from a database
        activities = [
            {
                'type': 'medication',
                'title': 'Medication check-in',
                'due_date': '2025-04-02',
                'status': 'due_today'
            },
            {
                'type': 'appointment',
                'title': 'Doctor appointment',
                'due_date': '2025-04-03',
                'status': 'upcoming'
            },
            {
                'type': 'assessment',
                'title': 'Health assessment due',
                'due_date': '2025-04-05',
                'status': 'upcoming'
            }
        ]
        
        return jsonify({
            'success': True,
            'activities': activities
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    # Check if the request path starts with /api
    if request.path.startswith('/api/'):
        return jsonify({"error": "Not found", "code": 404}), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    # Check if the request path starts with /api
    if request.path.startswith('/api/'):
        return jsonify({"error": "Internal server error", "code": 500}), 500
    return render_template('500.html'), 500

@app.errorhandler(401)
def unauthorized_error(error):
    """Handle 401 errors"""
    # Check if the request path starts with /api
    if request.path.startswith('/api/'):
        return jsonify({"error": "Unauthorized", "code": 401}), 401
    return redirect(url_for('login'))

# Add default user function for operations that previously required current_user
def get_default_user():
    """Return a default user for operations that previously required authentication"""
    return {
        'id': 'default_user',
        'name': 'Guest User',
        'username': 'guest',
        'email': 'guest@example.com',
        'role': 'patient',
        'profile': {
            'phone': '',
            'bio': 'Default user profile',
            'height': 170,
            'weight': 70,
            'blood_type': 'A+',
            'dob': '2000-01-01',
            'allergies': '',
            'chronic_conditions': '',
            'family_history': '',
            'share_data': True
        }
    }

@app.route('/settings')
def settings():
    """Render the settings page"""
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(debug=True) 