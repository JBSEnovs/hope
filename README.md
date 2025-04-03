# Medical AI Assistant

A comprehensive medical information assistant powered by BlackboxAI, designed to provide educational health information, medication management, and visualized health data.

## Features

- **AI-Powered Medical Information**: Leverages BlackboxAI's API to provide educational information about medical conditions, treatments, and medications
- **Multiple AI Models Support**: Access to several AI models through the BlackboxAI API, including:
  - gpt-4o
  - claude-sonnet-3.5
  - gemini-pro
  - blackboxai (free tier)
- **Dashboard**: Visualize health metrics, track medication adherence, and view upcoming health activities
- **Medication Management**: Track medications, dosages, schedules, and adherence history
- **Responsive Design**: Modern, mobile-friendly interface

## Screenshots

![Screenshot](screenshot.png)

## Installation

1. Clone the repository:
```
git clone https://github.com/your-username/medical-ai-assistant.git
cd medical-ai-assistant
```

2. Create and activate a virtual environment:
```
python -m venv env
# On Windows
.\env\Scripts\activate
# On Unix/MacOS
source env/bin/activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Run the application:
```
python minimal_app.py
```

5. Open your browser and navigate to `http://127.0.0.1:5000`

## BlackboxAI Integration

This application integrates with the [BlackboxAI API](https://github.com/notsopreety/blackbox-api) to provide AI-powered medical information. The integration:

- Supports multiple AI models including GPT-4o, Claude, and Gemini Pro
- Maintains conversation context for natural interactions
- Provides fallback responses when the API is unavailable
- Formats medical information with appropriate medical disclaimers

### API Usage

The application uses BlackboxAI's API for:
- Symptom analysis and potential condition identification
- Treatment options and recommendations
- Medical research and disease information
- Answering general health questions

### Offline Capability

When BlackboxAI's API is unavailable, the application provides pre-defined responses for common medical queries to ensure continuous functionality.

## Project Structure

- `minimal_app.py`: Main Flask application
- `agents/`: AI and functionality modules
  - `blackbox_ai.py`: BlackboxAI API integration
  - `medical_agent.py`: Medical functionality and prompts
- `static/`: CSS, JavaScript, and images
- `templates/`: HTML templates for the web interface
- `logs/`: Application logs

## Security Notice

This application is for educational purposes only. It does not provide medical diagnosis, and the information should not replace professional medical advice. Always consult a qualified healthcare provider for medical concerns. 