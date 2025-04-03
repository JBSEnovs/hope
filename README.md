# Medical AI Assistant

An advanced healthcare management application that provides personalized medical information, medication tracking, and health metrics visualization.

![Medical AI Assistant](screenshot.png)

## Features

- 🤖 **AI-Powered Medical Chatbot**: Get answers to medical questions in natural language
- 💊 **Medication Management**: Track medications, set reminders, and monitor adherence
- 📊 **Health Dashboard**: Visualize health metrics and trends
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- 🌐 **Multilingual Support**: Access information in your preferred language
- 🔒 **Privacy-Focused**: Your health data stays on your device

## Setup and Installation

### Prerequisites

- Python 3.10+ (tested up to Python 3.13)
- Flask
- Modern web browser
- Internet connection for AI features

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/medical-ai-assistant.git
   cd medical-ai-assistant
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables (optional, for advanced features):
   Create a `.env` file with the following variables:
   ```
   FLASK_SECRET_KEY=your_secret_key_here
   OPENAI_API_KEY=your_openai_api_key_here  # Optional, for enhanced AI capabilities
   ```

## Running the Application

### Basic Usage (Minimal App)

For a lightweight version with no external AI dependencies:

```
python minimal_app.py
```

Then visit http://127.0.0.1:5000 in your browser.

### Full Version

To run the complete application with all features:

```
python app.py
```

Then visit http://127.0.0.1:5000 in your browser.

## Usage Guide

### Chatbot

1. Navigate to the Chatbot page
2. Type your medical question and press Enter or click Send
3. View the AI response and any relevant visualizations
4. You can select different AI providers from the dropdown menu

### Medication Management

1. Go to the Medications page
2. View your current medications and adherence stats
3. Click "Add Medication" to add a new medication
4. Mark medications as taken with the checkbox
5. View medication details for more information

### Dashboard

The dashboard provides a comprehensive overview of your health metrics, including:
- Medication adherence
- Blood pressure trends
- Activity tracking
- Upcoming appointments

## Customization

### Theme

You can change the application theme in Settings > Appearance.

### Language

Change the interface language in Settings > Language.

## Security and Privacy

- All data is stored locally on your device
- No data is sent to external servers without explicit permission
- Medical information is provided for educational purposes only

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Bootstrap for the responsive UI framework
- Font Awesome for icons
- Chart.js for health data visualization

## Disclaimer

This application provides information for educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns. 