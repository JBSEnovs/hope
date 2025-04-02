import os
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from agents.medical_agent import MedicalAgent
from agents.auth import User, UserManager
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'temp_uploads')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key_change_in_production')

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data/documents', exist_ok=True)
os.makedirs('data/images', exist_ok=True)
os.makedirs('data/audio', exist_ok=True)
os.makedirs('data/sessions', exist_ok=True)
os.makedirs('data/users', exist_ok=True)

# Initialize the medical agent with default provider (OpenAI)
medical_agent = MedicalAgent()
user_manager = UserManager()

@login_manager.user_loader
def load_user(user_id):
    return user_manager.get_user(user_id)

@app.route('/')
def index():
    return render_template('index.html')

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.get_json() if request.is_json else request.form.to_dict()
    username = data.get('username')
    password = data.get('password')
    
    result = medical_agent.authenticate_user(username, password)
    
    if result.get('success'):
        user = result.get('user')
        if user:
            # Convert to User object if not already
            if not isinstance(user, User):
                user = User.from_dict(user)
            login_user(user)
            return jsonify({'success': True, 'redirect': '/'})
    
    if request.is_json:
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    else:
        return render_template('login.html', error='Invalid username or password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.get_json() if request.is_json else request.form.to_dict()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    name = data.get('name', '')
    role = data.get('role', 'patient')
    
    result = medical_agent.register_user(username, email, password, role, name)
    
    if result.get('success'):
        if request.is_json:
            return jsonify({'success': True, 'message': 'Registration successful'})
        else:
            return redirect(url_for('login'))
    
    if request.is_json:
        return jsonify({'success': False, 'error': result.get('error', 'Registration failed')}), 400
    else:
        return render_template('register.html', error=result.get('error', 'Registration failed'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Existing API routes with login_required
@app.route('/api/diagnose', methods=['POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
def get_documents():
    try:
        documents = medical_agent.get_uploaded_documents()
        return jsonify({"documents": documents})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/change_provider', methods=['POST'])
@login_required
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
    providers = {
        "openai": {
            "default_model": "gpt-4",
            "available_models": ["gpt-4", "gpt-3.5-turbo"]
        },
        "cohere": {
            "default_model": "command",
            "available_models": ["command", "command-light", "command-nightly"]
        },
        "google": {
            "default_model": "gemini-1.0-pro",
            "available_models": ["gemini-1.0-pro", "gemini-1.5-pro"]
        },
        "blackbox": {
            "default_model": "blackboxai",
            "available_models": medical_agent.get_blackbox_models()
        }
    }
    
    return jsonify(providers)

# Image Analysis Endpoints
@app.route('/api/analyze_image', methods=['POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
def create_consultation():
    data = request.json
    session_type = data.get('session_type', 'consultation')
    
    try:
        result = medical_agent.create_consultation_session(current_user.id, session_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/join_consultation/<session_id>', methods=['POST'])
@login_required
def join_consultation(session_id):
    data = request.json
    role = data.get('role', 'doctor' if current_user.get_role() == 'doctor' else 'patient')
    
    try:
        result = medical_agent.join_consultation(session_id, current_user.id, role)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/leave_consultation/<session_id>', methods=['POST'])
@login_required
def leave_consultation(session_id):
    try:
        result = medical_agent.leave_consultation(session_id, current_user.id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/send_message/<session_id>', methods=['POST'])
@login_required
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
@login_required
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
@login_required
def get_active_consultations():
    try:
        result = medical_agent.get_active_consultations(current_user.id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/end_consultation/<session_id>', methods=['POST'])
@login_required
def end_consultation(session_id):
    try:
        result = medical_agent.end_consultation(session_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# User Profile Endpoints
@app.route('/api/user_profile', methods=['GET'])
@login_required
def get_user_profile():
    try:
        result = medical_agent.get_user(current_user.id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update_profile', methods=['POST'])
@login_required
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
@login_required
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
@login_required
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

if __name__ == '__main__':
    app.run(debug=True) 