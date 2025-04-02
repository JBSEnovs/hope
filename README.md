# MedicalAI Assistant

An AI-powered web application for medical information, diagnosis assistance, and research updates.

## Features

- **Symptom Analysis**: Describe your symptoms and get possible diagnoses
- **Treatment Information**: Get information about treatment options for medical conditions
- **Medical Research**: Access latest research information about various diseases
- **Multi-Model Support**: Switch between different AI providers (OpenAI, Cohere, and Google Gemini)

## Important Disclaimer

This application is for **educational purposes only** and is not a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone this repository
```
git clone <repository-url>
cd medicalai-assistant
```

2. Create a virtual environment (recommended)
```
python -m venv venv
```

3. Activate the virtual environment
   - Windows:
   ```
   venv\Scripts\activate
   ```
   - macOS/Linux:
   ```
   source venv/bin/activate
   ```

4. Install dependencies
```
pip install -r requirements.txt
```

5. Set up environment variables by editing the `.env` file
   - Add your API keys to the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   COHERE_API_KEY=your_cohere_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```

### Running the Application

1. Start the Flask development server
```
flask run
```

2. Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

## Usage

1. **Selecting an AI Provider**: Choose between OpenAI, Cohere, or Google Gemini models
2. **Symptom Analysis**: Enter your symptoms in detail in the symptom analysis section and click "Analyze Symptoms"
3. **Treatment Information**: Enter a medical condition in the treatment information section and click "Get Treatment Info"
4. **Medical Research**: Enter a disease name in the medical research section and click "Research Disease"

## Supported AI Providers

- **OpenAI**: Uses GPT-4 or GPT-3.5-Turbo models
- **Cohere**: Uses Command models for natural language tasks
- **Google**: Uses Gemini models for comprehensive analysis

## Technical Details

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **AI Models**: 
  - OpenAI GPT models (via LangChain)
  - Cohere Command models (via LangChain)
  - Google Gemini models (via LangChain)

## License

This project is for educational purposes only.

## Author

[Your Name] 