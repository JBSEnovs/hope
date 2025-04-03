import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json
from datetime import datetime, timedelta
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_12345')
CORS(app)

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'temp_uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
    return render_template('welcome.html')

@app.route('/dashboard')
def dashboard():
    """Render the dashboard page"""
    user_profile = get_default_user().get('profile', {})
    consultations = []  # In a real app, this would fetch from the database
    return render_template('dashboard.html', user_profile=user_profile, consultations=consultations)

@app.route('/chatbot')
def chatbot():
    """Render the chatbot page"""
    return render_template('chatbot.html')

@app.route('/language_settings')
def language_settings():
    """Render the language settings page"""
    return render_template('language.html')

@app.route('/settings')
def settings():
    """Render the settings page"""
    return render_template('settings.html')

@app.route('/help')
def help_page():
    """Render the help page"""
    return render_template('help.html')

@app.route('/about')
def about_page():
    """Render the about page"""
    return render_template('about.html')

@app.route('/medications')
def medications_page():
    """Render the medications management page"""
    return render_template('medications.html')

# API Routes
@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """Process symptom diagnosis request"""
    data = request.json
    symptoms = data.get('symptoms', '')
    
    if not symptoms:
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
    
    return jsonify({
        'success': True,
        'diagnosis': diagnosis
    })

@app.route('/api/treatment', methods=['POST'])
def treatment():
    """Process treatment recommendation request"""
    data = request.json
    condition = data.get('condition', '')
    
    if not condition:
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
    
    return jsonify({
        'success': True,
        'treatment': treatment_info
    })

@app.route('/api/medications', methods=['GET'])
def get_medications():
    """Get all medications for the default user"""
    try:
        user_id = get_default_user()['id']
        medications = medications_db.get(user_id, [])
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
        
        return jsonify({
            'success': True,
            'medication': new_medication
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/medications/<medication_id>', methods=['GET'])
def get_medication(medication_id):
    """Get details for a specific medication"""
    user_id = get_default_user()['id']
    
    try:
        medications = medications_db.get(user_id, [])
        for medication in medications:
            if medication['id'] == medication_id:
                return jsonify({
                    'success': True,
                    'medication': medication
                })
        
        return jsonify({
            'success': False,
            'error': 'Medication not found'
        }), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/user_profile', methods=['GET'])
def get_user_profile():
    """Get user profile information"""
    try:
        user = get_default_user()
        return jsonify({
            'success': True,
            'user': user
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

@app.route('/api/analytics/adherence', methods=['GET'])
def get_adherence_analytics():
    """Get adherence analytics data for the current user"""
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

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True) 