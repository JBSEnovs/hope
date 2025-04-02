import os
from langchain_openai import ChatOpenAI
from langchain_cohere import ChatCohere
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class ModelProvider:
    """Base class for all model providers"""
    def __init__(self, temperature=0.2):
        self.temperature = temperature
        
    def get_model(self):
        """Return the LLM model"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def create_chain(self, prompt_template):
        """Create a LangChain with the specified prompt template"""
        llm = self.get_model()
        prompt = PromptTemplate.from_template(prompt_template)
        return LLMChain(llm=llm, prompt=prompt)

class OpenAIProvider(ModelProvider):
    """Provider for OpenAI models"""
    def __init__(self, model="gpt-4", temperature=0.2):
        super().__init__(temperature)
        self.model_name = model
        
        # Check for API key
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
    def get_model(self):
        return ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key
        )

class CohereProvider(ModelProvider):
    """Provider for Cohere models"""
    def __init__(self, model="command", temperature=0.2):
        super().__init__(temperature)
        self.model_name = model
        
        # Check for API key
        self.api_key = os.getenv("COHERE_API_KEY")
        if not self.api_key:
            raise ValueError("COHERE_API_KEY environment variable is not set")
        
    def get_model(self):
        return ChatCohere(
            model=self.model_name,
            temperature=self.temperature,
            cohere_api_key=self.api_key
        )

class GoogleProvider(ModelProvider):
    """Provider for Google Gemini models"""
    def __init__(self, model="gemini-1.0-pro", temperature=0.2):
        super().__init__(temperature)
        self.model_name = model
        
        # Check for API key
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
    def get_model(self):
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            google_api_key=self.api_key
        )

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