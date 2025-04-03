import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json
from datetime import datetime, timedelta
import uuid
import time

# Import the MedicalAgent class
from agents.medical_agent import MedicalAgent

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

# Create Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_12345')
CORS(app)

# Configure logging
app.logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler('logs/medical_app.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
app.logger.addHandler(console_handler)

app.logger.info('Medical AI Assistant startup')

# Application settings
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'temp_uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Create required directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Create directories
os.makedirs('logs', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('data/medications', exist_ok=True)

# Initialize the medical agent
medical_agent = MedicalAgent()

# Default user function to replace authentication
def get_default_user():
    """Return a default user object"""
    return {
        'id': '12345',
        'name': 'Demo User',
        'username': 'demo_user',
        'email': 'demo@example.com',
        'profile': {
            'height': '175 cm',
            'weight': '70 kg',
            'blood_type': 'O+',
            'allergies': 'None',
            'chronic_conditions': 'None',
            'medications': 'None',
            'emergency_contact': {
                'name': 'Emergency Contact',
                'phone': '123-456-7890',
                'relationship': 'Friend'
            }
        }
    }

# Medication storage (in-memory for demo)
medications_db = {
    '12345': [
        {
            'id': 'med1',
            'name': 'Aspirin',
            'dosage': '100mg',
            'frequency': 'Once daily',
            'start_date': '2024-04-01',
            'end_date': '2024-05-01',
            'notes': 'Take with food',
            'history': [
                {'date': '2024-04-01', 'status': 'taken'},
                {'date': '2024-04-02', 'status': 'taken'},
                {'date': '2024-04-03', 'status': 'missed'},
            ]
        },
        {
            'id': 'med2',
            'name': 'Vitamin D',
            'dosage': '1000 IU',
            'frequency': 'Once daily',
            'start_date': '2024-03-15',
            'end_date': None,
            'notes': 'Take with breakfast',
            'history': [
                {'date': '2024-04-01', 'status': 'taken'},
                {'date': '2024-04-02', 'status': 'taken'},
                {'date': '2024-04-03', 'status': 'taken'},
            ]
        }
    ]
}

# Routes
@app.route('/')
def index():
    """Render the home page"""
    app.logger.info('Home page accessed')
    return render_template('welcome.html')

@app.route('/index')
def original_index():
    """Render the original index page"""
    app.logger.info('Original index page accessed')
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Render the dashboard page"""
    app.logger.info('Dashboard page accessed')
    user_profile = get_default_user().get('profile', {})
    consultations = []  # In a real app, this would fetch from the database
    return render_template('dashboard.html', user_profile=user_profile, consultations=consultations)

@app.route('/chatbot')
def chatbot():
    """Render the chatbot page"""
    app.logger.info('Chatbot page accessed')
    return render_template('chatbot.html')

@app.route('/help')
def help_page():
    """Route for the help page"""
    app.logger.info('Help page accessed')
    return render_template('help.html')

@app.route('/about')
def about_page():
    """Route for the about page"""
    app.logger.info('About page accessed')
    return render_template('about.html')

@app.route('/settings')
def settings():
    """Route for the settings page"""
    app.logger.info('Settings page accessed')
    return render_template('settings.html')

@app.route('/profile')
def profile():
    """Route for the user profile page"""
    app.logger.info('Profile page accessed')
    return render_template('profile.html')

@app.route('/language')
def language_settings():
    """Route for the language settings page"""
    app.logger.info('Language settings page accessed')
    return render_template('language.html')

@app.route('/medications')
def medications_page():
    """Render the medications management page"""
    app.logger.info('Medications page accessed')
    return render_template('medications.html')

@app.route('/favicon.ico')
def favicon():
    """Serve the favicon"""
    return send_from_directory(os.path.join(app.root_path, 'static', 'img'),
                               'logo.png', mimetype='image/png')

# API Routes
@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """Process symptom diagnosis request"""
    app.logger.info('Symptom diagnosis API called')
    data = request.json
    symptoms = data.get('symptoms', '')
    
    if not symptoms:
        app.logger.warning('Diagnosis request with no symptoms')
        return jsonify({
            'success': False,
            'error': 'No symptoms provided'
        }), 400
    
    # In a real app, this would call a medical model
    diagnosis = {
        'possible_conditions': [
            {
                'name': 'Common Cold',
                'probability': 'High',
                'description': 'A viral infection of the upper respiratory tract.',
                'symptoms': ['Runny nose', 'Sore throat', 'Cough', 'Congestion', 'Mild fever'],
                'recommendations': 'Rest, hydration, and over-the-counter cold medications.'
            },
            {
                'name': 'Seasonal Allergies',
                'probability': 'Medium',
                'description': 'An immune response to environmental triggers like pollen or dust.',
                'symptoms': ['Runny nose', 'Sneezing', 'Itchy eyes', 'Congestion'],
                'recommendations': 'Antihistamines, nasal steroids, or avoiding allergens.'
            }
        ],
        'disclaimer': 'This information is for educational purposes only and should not replace professional medical advice.'
    }
    
    app.logger.info(f'Diagnosis provided for symptoms: {symptoms[:50]}...')
    return jsonify({
        'success': True,
        'diagnosis': diagnosis
    })

@app.route('/api/treatment', methods=['POST'])
def treatment():
    """Process treatment recommendation request"""
    app.logger.info('Treatment API called')
    data = request.json
    condition = data.get('condition', '')
    
    if not condition:
        app.logger.warning('Treatment request with no condition')
        return jsonify({
            'success': False,
            'error': 'No condition provided'
        }), 400
    
    # Mock treatment info (in a real app, this would come from a medical database)
    treatment_info = {
        'condition': condition,
        'treatments': [
            {
                'type': 'Medication',
                'name': 'Acetaminophen',
                'description': 'For pain and fever relief.',
                'usage': 'Take as directed by your healthcare provider.'
            },
            {
                'type': 'Home Care',
                'name': 'Rest and Hydration',
                'description': 'Allows your body to recover while staying hydrated.',
                'usage': 'Rest as much as possible and drink plenty of fluids.'
            }
        ],
        'preventive_measures': [
            'Wash hands frequently',
            'Avoid close contact with sick individuals',
            'Maintain a healthy diet and exercise routine'
        ],
        'disclaimer': 'This information is for educational purposes only and should not replace professional medical advice.'
    }
    
    app.logger.info(f'Treatment information provided for condition: {condition}')
    return jsonify({
        'success': True,
        'treatment': treatment_info
    })

@app.route('/api/medications', methods=['GET'])
def get_medications():
    """Get all medications for the default user"""
    app.logger.info('Get medications API called')
    try:
        user_id = get_default_user()['id']
        medications = medications_db.get(user_id, [])
        app.logger.info(f'Retrieved {len(medications)} medications for user {user_id}')
        return jsonify({
            'success': True,
            'medications': medications
        })
    except Exception as e:
        app.logger.error(f'Error retrieving medications: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/medications', methods=['POST'])
def add_medication():
    """Add a new medication reminder"""
    app.logger.info('Add medication API called')
    data = request.json
    
    name = data.get('name')
    dosage = data.get('dosage')
    frequency = data.get('frequency')
    start_date = data.get('start_date')
    end_date = data.get('end_date', None)
    notes = data.get('notes', None)
    
    # Input validation
    if not all([name, dosage, frequency, start_date]):
        app.logger.warning('Missing required fields in add medication request')
        return jsonify({
            'success': False,
            'error': 'Missing required fields'
        }), 400
    
    user_id = get_default_user()['id']
    
    try:
        new_medication = {
            'id': f'med{uuid.uuid4().hex[:6]}',
            'name': name,
            'dosage': dosage,
            'frequency': frequency,
            'start_date': start_date,
            'end_date': end_date,
            'notes': notes,
            'history': []
        }
        
        if user_id not in medications_db:
            medications_db[user_id] = []
            
        medications_db[user_id].append(new_medication)
        
        app.logger.info(f'Added new medication {name} for user {user_id}')
        return jsonify({
            'success': True,
            'medication': new_medication
        })
    except Exception as e:
        app.logger.error(f'Error adding medication: {str(e)}')
        return jsonify({"error": str(e)}), 500

@app.route('/api/medications/<medication_id>', methods=['GET'])
def get_medication(medication_id):
    """Get details for a specific medication"""
    app.logger.info(f'Get medication details API called for {medication_id}')
    user_id = get_default_user()['id']
    
    try:
        medications = medications_db.get(user_id, [])
        for medication in medications:
            if medication['id'] == medication_id:
                app.logger.info(f'Retrieved details for medication {medication_id}')
                return jsonify({
                    'success': True,
                    'medication': medication
                })
        
        app.logger.warning(f'Medication {medication_id} not found')
        return jsonify({
            'success': False,
            'error': 'Medication not found'
        }), 404
    except Exception as e:
        app.logger.error(f'Error retrieving medication {medication_id}: {str(e)}')
        return jsonify({"error": str(e)}), 500

@app.route('/api/medications/<medication_id>', methods=['DELETE'])
def delete_medication(medication_id):
    """Delete a medication"""
    app.logger.info(f'Delete medication API called for {medication_id}')
    user_id = get_default_user()['id']
    
    try:
        medications = medications_db.get(user_id, [])
        for i, medication in enumerate(medications):
            if medication['id'] == medication_id:
                del medications_db[user_id][i]
                app.logger.info(f'Deleted medication {medication_id}')
                return jsonify({
                    'success': True,
                    'message': 'Medication deleted'
                })
        
        app.logger.warning(f'Medication {medication_id} not found for deletion')
        return jsonify({
            'success': False,
            'error': 'Medication not found'
        }), 404
    except Exception as e:
        app.logger.error(f'Error deleting medication {medication_id}: {str(e)}')
        return jsonify({"error": str(e)}), 500

@app.route('/api/medications/<medication_id>/take', methods=['POST'])
def mark_medication_taken(medication_id):
    """Mark a medication as taken today"""
    app.logger.info(f'Mark medication as taken API called for {medication_id}')
    user_id = get_default_user()['id']
    today = datetime.now().strftime('%Y-%m-%d')
    
    try:
        medications = medications_db.get(user_id, [])
        for medication in medications:
            if medication['id'] == medication_id:
                # Check if there's already an entry for today
                today_entry = next((entry for entry in medication.get('history', []) if entry['date'] == today), None)
                
                if today_entry:
                    today_entry['status'] = 'taken'
                else:
                    if 'history' not in medication:
                        medication['history'] = []
                    medication['history'].append({'date': today, 'status': 'taken'})
                
                app.logger.info(f'Marked medication {medication_id} as taken for {today}')
                return jsonify({
                    'success': True,
                    'message': 'Medication marked as taken'
                })
        
        app.logger.warning(f'Medication {medication_id} not found for marking as taken')
        return jsonify({
            'success': False,
            'error': 'Medication not found'
        }), 404
    except Exception as e:
        app.logger.error(f'Error marking medication {medication_id} as taken: {str(e)}')
        return jsonify({"error": str(e)}), 500

@app.route('/api/user_profile', methods=['GET'])
def get_user_profile():
    """Get user profile information"""
    app.logger.info('Get user profile API called')
    try:
        user = get_default_user()
        app.logger.info(f'Retrieved profile for user {user["id"]}')
        return jsonify({
            'success': True,
            'user': user
        })
    except Exception as e:
        app.logger.error(f'Error retrieving user profile: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics/health_metrics', methods=['GET'])
def get_health_metrics():
    """Get health metrics data for the current user"""
    app.logger.info('Get health metrics API called')
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
        
        app.logger.info(f'Retrieved health metrics for user {user_id}')
        return jsonify({
            'success': True,
            'metrics': metrics
        })
    except Exception as e:
        app.logger.error(f'Error retrieving health metrics: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics/adherence', methods=['GET'])
def get_adherence_analytics():
    """Get adherence analytics data for the current user"""
    app.logger.info('Get adherence analytics API called')
    user_id = get_default_user()['id']
    
    try:
        # Get user's medications
        medications = medications_db.get(user_id, [])
        
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
        
        total_events = taken_count + missed_count
        adherence_rate = (taken_count / total_events) * 100 if total_events > 0 else 0
        
        # Calculate upcoming doses (placeholder logic)
        upcoming_count = total_meds * 2  # Simplified calculation
        
        app.logger.info(f'Retrieved adherence analytics for user {user_id}')
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
        app.logger.error(f'Error retrieving adherence analytics: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analytics/health_activities', methods=['GET'])
def get_health_activities():
    """Get recent and upcoming health activities for the current user"""
    app.logger.info('Get health activities API called')
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
        
        app.logger.info(f'Retrieved health activities for user {user_id}')
        return jsonify({
            'success': True,
            'activities': activities
        })
    except Exception as e:
        app.logger.error(f'Error retrieving health activities: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/research', methods=['POST'])
def research():
    """Process medical research request"""
    app.logger.info('Medical research API called')
    data = request.json
    disease = data.get('disease', '')
    
    if not disease:
        app.logger.warning('Research request with no disease specified')
        return jsonify({
            'success': False,
            'error': 'No disease provided'
        }), 400
    
    # Mock research info (in a real app, this would come from a medical database or AI)
    research_info = {
        'disease': disease,
        'summary': f'Recent research on {disease} has shown promising developments in treatment approaches and understanding of disease mechanisms.',
        'key_findings': [
            'New genetic factors identified that contribute to susceptibility',
            'Improved diagnostic techniques using biomarkers',
            'Novel therapeutic approaches showing efficacy in clinical trials'
        ],
        'recent_papers': [
            {
                'title': f'Advances in {disease} Treatment: A Comprehensive Review',
                'authors': 'Smith et al.',
                'journal': 'Journal of Medical Research',
                'year': 2024,
                'url': '#'
            },
            {
                'title': f'Pathophysiology of {disease}: New Insights',
                'authors': 'Johnson et al.',
                'journal': 'Clinical Medicine Today',
                'year': 2023,
                'url': '#'
            }
        ],
        'disclaimer': 'This information is for educational purposes only and should not replace professional medical advice.'
    }
    
    app.logger.info(f'Research information provided for disease: {disease}')
    return jsonify({
        'success': True,
        'research': research_info
    })

@app.route('/api/providers', methods=['GET'])
def providers():
    """Returns available providers and their default models"""
    app.logger.info('Providers API accessed')
    try:
        blackbox_models = medical_agent.get_blackbox_models() or ["blackboxai"]
    except Exception as e:
        app.logger.error(f"Error getting blackbox models: {e}")
        blackbox_models = ["blackboxai"]
        
    providers = {
        "blackbox": {
            "default_model": "blackboxai",
            "available_models": blackbox_models
        }
    }
    
    return jsonify(providers)

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """Get list of available documents"""
    app.logger.info('Documents API accessed')
    try:
        documents = medical_agent.get_uploaded_documents()
        return jsonify({"documents": documents})
    except Exception as e:
        app.logger.error(f"Error getting documents: {str(e)}")
        return jsonify({"documents": []})

@app.route('/api/blackbox/query', methods=['POST'])
def blackbox_query():
    """Handle direct queries to the BlackboxAI"""
    app.logger.info('BlackboxAI query API accessed')
    try:
        data = request.json
        query = data.get('query', '')
        if not query:
            return jsonify({"error": "No query provided"}), 400
            
        result = medical_agent.blackbox_ai.chat(query)
        return jsonify({"response": result})
    except Exception as e:
        app.logger.error(f"Error in blackbox query: {str(e)}")
        return jsonify({"error": f"Error processing query: {str(e)}"}), 500

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get available languages"""
    app.logger.info('Languages API accessed')
    languages = [
        {"code": "en", "name": "English", "native_name": "English"},
        {"code": "es", "name": "Spanish", "native_name": "Español"},
        {"code": "fr", "name": "French", "native_name": "Français"},
        {"code": "de", "name": "German", "native_name": "Deutsch"},
        {"code": "zh", "name": "Chinese", "native_name": "中文"},
        {"code": "ja", "name": "Japanese", "native_name": "日本語"},
        {"code": "ar", "name": "Arabic", "native_name": "العربية"},
        {"code": "hi", "name": "Hindi", "native_name": "हिन्दी"},
        {"code": "pt", "name": "Portuguese", "native_name": "Português"},
        {"code": "ru", "name": "Russian", "native_name": "Русский"}
    ]
    return jsonify({"languages": languages})

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    app.logger.warning(f'404 error: {request.path}')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    app.logger.error(f'500 error: {str(error)}')
    return render_template('500.html'), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    app.logger.info('Health check API called')
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(debug=True) 