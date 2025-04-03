import os
import json
import uuid
import requests
from datetime import datetime

class BlackboxAI:
    """
    Class for integration with BlackboxAI service.
    This allows using BlackboxAI models for medical queries.
    """
    
    def __init__(self, model="blackboxai"):
        """
        Initialize the BlackboxAI agent
        
        Args:
            model (str): Model to use (defaults to "blackboxai")
        """
        # Use direct BlackboxAI API instead of a local API service
        self.api_url = "https://api.blackbox.ai/api/chat"
        self.headers = {
            "Content-Type": "application/json"
            # No API key required for the free version
        }
        self.conversations = {}  # Store conversation histories
        self.model = model or "blackboxai"
        
        # Available models in BlackboxAI
        self.available_models = [
            "gpt-4o",
            "claude-sonnet-3.5",
            "gemini-pro",
            "blackboxai"  # Free model
        ]
        
        # Demo responses for when the API is unavailable
        self.demo_responses = {
            "symptoms": "Based on the symptoms you've described, this could be consistent with several conditions including:\n\n1. Common Cold\n- Matches your symptoms of sore throat and congestion\n- Other symptoms might include mild fever and cough\n- Usually resolves within 7-10 days with rest and hydration\n\n2. Seasonal Allergies\n- Often presents with congestion and sometimes sore throat\n- May also cause itchy eyes and sneezing\n- Typically worsens during specific seasons\n\n3. Viral Pharyngitis\n- Primarily causes sore throat\n- Often accompanied by mild fever and fatigue\n- Usually improves within a week\n\nIt would be advisable to consult with a primary care physician if symptoms persist beyond a few days or worsen significantly.\n\nNote: This is not a diagnosis, just educational information about what these symptoms might be associated with.",
            "medication": "Here's some information about this medication:\n\n- Mechanism of Action: This medication works by inhibiting specific enzymes in the body that contribute to inflammation and pain.\n- Common Side Effects: May include mild stomach upset, dizziness, and in some cases, headache. Most side effects are temporary and resolve on their own.\n- Usage Guidelines: Typically taken with food to reduce stomach irritation. It's important to take it at regular intervals as prescribed.\n- Precautions: Should be used with caution in people with kidney disease, heart conditions, or those taking blood thinners.\n\nRemember to follow your doctor's specific instructions for your situation, as they may differ from general guidelines.",
            "general": "I understand you have a question about this health topic. The Medical AI Assistant can provide educational information about common conditions, medications, and general health topics.\n\nFor personalized medical advice, it's important to consult with a healthcare professional who can consider your specific medical history and situation.\n\nIf you'd like to learn more about general health information on this topic, please provide more details about what specific aspects you're interested in."
        }
    
    def chat(self, content, conversation_id=None):
        """
        Send a message to BlackboxAI and get a response
        
        Args:
            content (str): Message content
            conversation_id (str): Optional conversation ID for continuing a chat
            
        Returns:
            str: Response text from BlackboxAI
        """
        try:
            result = self.send_message(content, conversation_id)
            if result.get('success'):
                return result.get('response', '')
            else:
                error_msg = result.get('error', 'Unknown error')
                # If service unavailable, provide a demo response
                if "503" in error_msg or "timeout" in error_msg.lower():
                    return self.get_demo_response(content) + "\n\n[Note: This is a demo response because the AI service is currently unavailable]"
                return f"Error: {error_msg}"
        except Exception as e:
            return f"Error communicating with BlackboxAI: {str(e)}\n\nHere's a fallback response:\n\n{self.get_demo_response(content)}"
    
    def get_demo_response(self, query):
        """
        Get a demo response based on the query content
        
        Args:
            query (str): User query
            
        Returns:
            str: Demo response text
        """
        query = query.lower()
        if any(word in query for word in ["symptom", "pain", "feel", "hurt", "ache"]):
            return self.demo_responses["symptoms"]
        elif any(word in query for word in ["medication", "drug", "pill", "medicine", "prescription"]):
            return self.demo_responses["medication"]
        else:
            return self.demo_responses["general"]
    
    def send_message(self, content, conversation_id=None):
        """
        Send a message to BlackboxAI
        
        Args:
            content (str): Message content
            conversation_id (str): Conversation ID for continuing a conversation
            
        Returns:
            dict: Response with conversation data and BlackboxAI response
        """
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Initialize conversation history if needed
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        # Add user message to history
        user_message = {
            "id": conversation_id,
            "content": content,
            "role": "user"
        }
        self.conversations[conversation_id].append(user_message)
        
        # Prepare the payload based on the BlackboxAI API
        payload = {
            "messages": self.conversations[conversation_id],
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
            "userSelectedModel": self.model  # Dynamic model selection
        }
        
        try:
            # Send request to BlackboxAI
            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=30)
            
            # Check for successful response
            if response.status_code == 200:
                # Get response text and clean it
                response_text = response.text
                cleaned_response = response_text.replace("Generated by BLACKBOX.AI, try unlimited chat https://www.blackbox.ai\n\n", "")
                
                # Create assistant message
                assistant_message = {
                    "id": f"response-{datetime.now().timestamp()}",
                    "content": cleaned_response,
                    "role": "assistant"
                }
                
                # Add to conversation history
                self.conversations[conversation_id].append(assistant_message)
                
                return {
                    "success": True,
                    "conversation_id": conversation_id,
                    "response": cleaned_response
                }
            else:
                return {
                    "success": False,
                    "error": f"BlackboxAI returned status code {response.status_code}"
                }
            
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Error communicating with BlackboxAI: {str(e)}"
            }
    
    def continue_conversation(self, conversation_id, content):
        """
        Continue an existing conversation with BlackboxAI
        
        Args:
            conversation_id (str): The ID of the conversation to continue
            content (str): Message content
            
        Returns:
            dict: Response with conversation data and BlackboxAI response
        """
        # Check if conversation exists
        if conversation_id not in self.conversations:
            return {
                "success": False,
                "error": "Conversation not found"
            }
        
        # Use the send_message method with the existing conversation ID
        return self.send_message(content, conversation_id)
    
    def get_available_models(self):
        """
        Get available models for BlackboxAI
        
        Returns:
            list: Available model names
        """
        return self.available_models
    
    def change_model(self, model):
        """
        Change the BlackboxAI model
        
        Args:
            model (str): Model name to use
            
        Returns:
            bool: Success status
        """
        if model in self.available_models:
            self.model = model
            return True
        return False 