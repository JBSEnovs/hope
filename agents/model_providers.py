import os
import openai
import cohere
import requests

class ModelProvider:
    """Base class for all model providers"""
    def __init__(self, temperature=0.2):
        self.temperature = temperature
        
    def generate_response(self, prompt):
        """Generate a response for the given prompt"""
        raise NotImplementedError("Subclasses must implement this method")

class OpenAIProvider(ModelProvider):
    """Provider for OpenAI models"""
    def __init__(self, model="gpt-4", temperature=0.2):
        super().__init__(temperature)
        self.model_name = model
        
        # Check for API key
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Set the API key
        openai.api_key = self.api_key
        
    def generate_response(self, prompt):
        """Generate a response using OpenAI API"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful medical assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error with OpenAI API: {str(e)}")
            return f"Error generating response: {str(e)}"

class CohereProvider(ModelProvider):
    """Provider for Cohere models"""
    def __init__(self, model="command", temperature=0.2):
        super().__init__(temperature)
        self.model_name = model
        
        # Check for API key
        self.api_key = os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError("COHERE_API_KEY environment variable is not set")
        
        # Initialize client
        self.client = cohere.Client(self.api_key)
        
    def generate_response(self, prompt):
        """Generate a response using Cohere API"""
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                temperature=self.temperature,
                max_tokens=2000
            )
            return response.generations[0].text
        except Exception as e:
            print(f"Error with Cohere API: {str(e)}")
            return f"Error generating response: {str(e)}"

class GoogleProvider(ModelProvider):
    """Provider for Google Gemini models"""
    def __init__(self, model="gemini-1.0-pro", temperature=0.2):
        super().__init__(temperature)
        self.model_name = model
        
        # Check for API key
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
    def generate_response(self, prompt):
        """Generate a response using Google Gemini API"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            data = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": self.temperature}
            }
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            return result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "No response generated")
        except Exception as e:
            print(f"Error with Google API: {str(e)}")
            return f"Error generating response: {str(e)}"

def get_provider(provider_name, model=None):
    """Factory method to get the appropriate provider"""
    providers = {
        "openai": OpenAIProvider,
        "cohere": CohereProvider,
        "google": GoogleProvider
    }
    
    if provider_name not in providers:
        raise ValueError(f"Unknown provider: {provider_name}. Available providers: {', '.join(providers.keys())}")
    
    provider_class = providers[provider_name]
    if model:
        return provider_class(model=model)
    return provider_class() 