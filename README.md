# Medical AI Assistant

A comprehensive medical information assistant powered by BlackboxAI, designed to provide educational health information, medication management, and visualized health data.

## Features

- **AI-Powered Medical Information**: Directly integrates with BlackboxAI's API to provide educational information about medical conditions, treatments, and medications
- **Multiple AI Models Support**: Access to several AI models through the BlackboxAI API, including:
  - gpt-4o
  - claude-sonnet-3.5
  - gemini-pro
  - blackboxai (free tier)
- **Dashboard**: Visualize health metrics, track medication adherence, and view upcoming health activities
- **Medication Management**: Track medications, dosages, schedules, and adherence history
- **Responsive Design**: Modern, mobile-friendly interface
- **Conversation Memory**: Maintains chat history for natural, contextual conversations

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

This application directly integrates with the BlackboxAI API to provide AI-powered medical information. The integration was built based on [BlackboxAI API](https://github.com/notsopreety/blackbox-api) implementation, but adapted for native Python usage.

### Key Integration Features:

- **Direct API Access**: Makes direct API calls to BlackboxAI's service without middleware
- **Conversation Management**: Maintains conversation history using unique IDs for natural back-and-forth dialogue
- **Multi-Model Support**: Dynamically switch between AI models:
  - `gpt-4o`: Most advanced GPT model from OpenAI
  - `claude-sonnet-3.5`: Anthropic's powerful model for medical information
  - `gemini-pro`: Google's comprehensive AI model
  - `blackboxai`: Free tier model with good capabilities
- **Robust Error Handling**: Provides fallback responses for network issues or service unavailability
- **Response Cleaning**: Automatically removes promotional text from BlackboxAI responses

### Medical Prompt Engineering

The application uses carefully designed medical prompts that:
- Request structured, educational information about conditions and treatments
- Include appropriate medical disclaimers with all responses
- Format information with clear sections for symptom analysis, treatment options, and research
- Extract data that can be used for visualizations

### API Usage

The application uses BlackboxAI's capabilities for:
- Symptom analysis and potential condition identification
- Treatment options and recommendations
- Medical research and disease information
- Answering general health questions

### Offline Capability

When BlackboxAI's API is unavailable, the application provides pre-defined responses for common medical queries to ensure continuous functionality.

## Project Structure

- `minimal_app.py`: Main Flask application
- `agents/`: AI and functionality modules
  - `blackbox_ai.py`: BlackboxAI API direct integration
  - `medical_agent.py`: Medical functionality and prompts
- `static/`: CSS, JavaScript, and images
- `templates/`: HTML templates for the web interface
- `logs/`: Application logs

## Security Notice

This application is for educational purposes only. It does not provide medical diagnosis, and the information should not replace professional medical advice. Always consult a qualified healthcare provider for medical concerns. 