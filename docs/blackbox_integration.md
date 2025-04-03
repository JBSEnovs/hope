# BlackboxAI Integration Documentation

This document provides comprehensive information about how the Medical AI Assistant integrates with BlackboxAI's services.

## Overview

The Medical AI Assistant directly communicates with BlackboxAI's API to provide intelligent responses for medical queries. This integration is implemented in `agents/blackbox_ai.py` and based on the implementation patterns from [BlackboxAI API](https://github.com/notsopreety/blackbox-api) but adapted for direct Python usage without an intermediary server.

## Available Models

BlackboxAI provides access to several powerful AI models:

1. **blackboxai** - Free tier model with good capabilities (default)
2. **gpt-4o** - OpenAI's advanced GPT-4o model with excellent medical knowledge
3. **claude-sonnet-3.5** - Anthropic's Claude model, known for thoughtful responses
4. **gemini-pro** - Google's Gemini Pro model with broad knowledge

## Implementation Details

### Core Components

- **BlackboxAI Class**: Handles all communications with the BlackboxAI service
- **Conversation Management**: Maintains conversation history for context-aware responses
- **Error Handling**: Provides fallback responses when the API is unavailable
- **Model Switching**: Allows dynamic selection of AI models

### API Endpoints

The BlackboxAI API endpoint used is:
```
https://api.blackbox.ai/api/chat
```

### Conversation Structure

Conversations are maintained using a unique conversation ID and stored as a sequence of message objects with the following structure:

```python
{
    "id": "conversation_id",
    "content": "message content",
    "role": "user" or "assistant" 
}
```

### Request Payload

When sending a request to BlackboxAI, the following payload structure is used:

```python
{
    "messages": [message_history],
    "id": conversation_id,
    "previewToken": None,
    "userId": None,
    "codeModelMode": True,
    "agentMode": {},
    "trendingAgentMode": {},
    "isMicMode": False,
    "userSystemPrompt": None,
    "maxTokens": 1024,
    "playgroundTopP": 0.9,
    "playgroundTemperature": 0.5,
    "isChromeExt": False,
    "githubToken": None,
    "clickedAnswer2": False,
    "clickedAnswer3": False,
    "clickedForceWebSearch": False,
    "visitFromDelta": False,
    "mobileClient": False,
    "userSelectedModel": selected_model
}
```

## Fallback Mechanism

When the BlackboxAI service is unavailable (due to network issues, service outages, or rate limiting), the application provides pre-defined responses based on the type of query:

- **Symptom-related queries**: Basic information about potential conditions
- **Medication-related queries**: General information about medication usage
- **General medical queries**: General health information and disclaimers

## Usage in Application

The BlackboxAI integration is used throughout the application:

1. **Chatbot Interface**: Direct interaction with the AI through the web UI
2. **Symptom Analysis**: Structured analysis of user-reported symptoms
3. **Treatment Information**: Educational information about treatment options
4. **Medical Research**: In-depth information about medical conditions

## Standalone Client

The application includes a standalone BlackboxAI client (`blackbox_client.py`) for testing and debugging purposes. This allows direct interaction with the BlackboxAI API without running the full web application.

### Using the Client

```bash
# Interactive mode
python blackbox_client.py

# Use a specific model
python blackbox_client.py --model gpt-4o

# List available models
python blackbox_client.py --list-models

# Send a one-off message
python blackbox_client.py --message "What is diabetes?"

# Continue a conversation
python blackbox_client.py --conversation your-conversation-id
```

## Usage in Code

To use the BlackboxAI integration in your own code:

```python
from agents.blackbox_ai import BlackboxAI

# Initialize with default model (blackboxai)
blackbox = BlackboxAI()

# Or with a specific model
blackbox = BlackboxAI(model="gpt-4o")

# Send a message and get a response
response = blackbox.chat("What are the symptoms of the flu?")
print(response)

# Start or continue a conversation
conversation_id = "unique-conversation-id"
response1 = blackbox.chat("What are the symptoms of diabetes?", conversation_id)
response2 = blackbox.chat("What are the treatment options?", conversation_id)

# Change the model
blackbox.change_model("claude-sonnet-3.5")
```

## Security and Privacy Considerations

- BlackboxAI does not require an API key for basic usage
- Communication is done over HTTPS for security
- No personal health information should be sent to the API
- All responses include an appropriate medical disclaimer 