# MedicalAI Assistant

![Project Logo](images/hope.png)

An AI-powered medical assistant web application that helps with diagnosing diseases, recommending treatments, and providing medical research information.

## Features

### Core Features
- **Symptom Analysis**: Analyze symptoms and get possible diagnoses
- **Treatment Information**: Get information about treatment options for medical conditions
- **Medical Research**: Access the latest research information about diseases
- **Document Repository**: Upload and process medical documents to enhance AI knowledge

### Advanced Features
- **Data Visualization**: Generate visual representations of medical data
- **Multiple AI Providers**: Support for OpenAI, Cohere, Google AI, and BlackboxAI models
- **User Authentication**: Secure account creation and management
- **Image Analysis**: AI-assisted analysis of medical images with enhancement options
- **Voice Interface**: Speak to the AI and listen to responses
- **Collaborative Consultations**: Real-time messaging between patients and healthcare providers
- **Chatbot Interface**: Intuitive chat-based interface with the medical assistant
- **Health Metrics Dashboard**: Track and visualize personal health metrics
- **Multilingual Support**: Get medical information in 11 different languages
- **Medication Reminders**: Track medications, set schedules, and monitor adherence

## Setup

### Requirements
- Python 3.9 or higher
- Flask web framework
- Various AI and language processing libraries

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables in a `.env` file:
   ```
   FLASK_SECRET_KEY=your_secret_key
   OPENAI_API_KEY=your_openai_key
   COHERE_API_KEY=your_cohere_key
   GOOGLE_API_KEY=your_google_key
   ```
4. Run the application:
   ```
   python app.py
   ```

### BlackboxAI Standalone Server (Optional)
The application includes a BlackboxAI integration directly in the Python backend. However, if you prefer to run BlackboxAI as a separate service, a Node.js server is provided:

1. Install Node.js dependencies:
   ```
   npm install
   ```
2. Run the BlackboxAI server:
   ```
   node blackbox_server.js
   ```
3. The BlackboxAI server will run on port 3000 by default.

## Usage

### Authentication
- Register a new account as a patient, doctor, or specialist
- Log in to access the application features
- Manage your profile and password from the user menu

### AI Assistant
- Describe symptoms to get possible diagnoses
- Enter a medical condition to learn about treatment options
- Research diseases to get the latest information
- Optionally include visualizations with your requests
- Choose between different AI providers: OpenAI, Cohere, Google, or BlackboxAI

### Document Repository
- Upload medical documents (PDF, DOCX, TXT) to enhance the AI's knowledge
- View all uploaded documents

### Image Analysis
- Upload medical images for AI-assisted analysis
- Apply various enhancements to improve image quality
- Receive AI interpretation of image metrics

### Voice Interface
- Record voice input to describe symptoms or ask questions
- Process transcriptions for different types of analysis
- Listen to AI responses through speech synthesis

### Consultations
- Create or join consultation sessions
- Exchange real-time messages with healthcare providers
- Share images and files during consultations
- View participant information and session history

### Visualizations
- Generate visualizations of symptoms, treatments, and disease progression
- Save visualizations for future reference
- View gallery of saved visualizations

### Chatbot Interface
- Interact with the AI using a familiar chat interface
- See real-time typing indicators as the AI responds
- Get quick responses to medical questions
- Use voice commands to speak with the assistant
- Switch AI providers on-the-fly to compare responses
- Save and export chat conversations

### Health Dashboard
- Track key health metrics like BMI, blood pressure, heart rate, and oxygen saturation
- Visualize health data over time with interactive charts
- Receive personalized health recommendations based on your data
- View recent consultations and upcoming appointments
- Set health goals and track progress

### Multilingual Support
- Get medical information in 11 different languages
- Automatic language detection for input text
- Translate AI responses to your preferred language
- Preserve medical terminology during translation
- Special handling for medical terms to ensure accuracy

### Medication Management
- Add and track medications with dosage and schedule information
- Set up various frequency patterns (daily, weekly, every X hours, etc.)
- Record medication doses as taken or missed
- View upcoming medications due in the next 24 hours
- Monitor medication adherence with visual statistics
- Get personalized adherence improvement tips
- View 7-day medication schedule overview

## Technical Architecture

### Backend
- **Flask**: Web framework
- **LangChain**: Integration with multiple AI providers
- **Flask-Login**: User authentication
- **Pillow/OpenCV**: Image processing
- **SQLite/JSON**: Data storage
- **Googletrans**: Language translation

### Frontend
- **Bootstrap**: UI framework
- **JavaScript**: Dynamic interactions
- **Plotly**: Interactive data visualizations

### AI Providers
- **OpenAI**: GPT models (requires API key)
- **Cohere**: Command models (requires API key)
- **Google**: Gemini models (requires API key)
- **BlackboxAI**: Various AI models including GPT-4o, Claude, Gemini, and BlackboxAI's own model (no API key required)

### Supported Languages
- English
- Spanish
- French
- German
- Chinese (Simplified)
- Japanese
- Arabic
- Russian
- Portuguese
- Hindi
- Swahili

## Medical Disclaimer

This application provides information for educational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers for medical concerns.

## Important Disclaimer

This application is for **educational purposes only** and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.

## Author

![Creator Image](images/creator.jpg)

**uncoder-cloud**

- Email: webdayskenya@gmail.com
- WhatsApp: +254791258754
- Instagram: phantom0x01 