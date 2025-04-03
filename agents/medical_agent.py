import os
import json
from .blackbox_ai import BlackboxAI

class MedicalAgent:
    def __init__(self, model=None):
        """
        Initialize the Medical Agent
        
        Args:
            model (str): Specific model to use, or None for default
        """
        # Initialize components
        self.blackbox_ai = BlackboxAI(model=model or "blackboxai")
        
        # Set up the disclaimer
        self.disclaimer = (
            "MEDICAL INFORMATION NOTICE: The information provided is for educational purposes only. "
            "It is not intended to replace professional medical advice, diagnosis, or treatment. "
            "Always consult qualified healthcare providers with questions about medical conditions. "
            "Do not disregard professional medical advice based on information provided here."
        )
    
    def diagnose(self, symptoms):
        """Analyze symptoms and suggest possible diagnoses"""
        prompt = (
            "You are a medical AI assistant. A patient describes the following symptoms: {symptoms}\n\n"
            "Based only on these symptoms, suggest possible conditions that might match these symptoms, "
            "organized from most to least likely. For each, include:\n"
            "1. The name of the condition\n"
            "2. Why it matches the symptoms\n"
            "3. What other symptoms might be present if this condition is correct\n"
            "4. What kind of medical professional should be consulted\n\n"
            "Remember to be thorough but emphasize the importance of consulting a healthcare professional for accurate diagnosis."
        ).format(symptoms=symptoms)
        
        # Get response from BlackboxAI
        result = self.blackbox_ai.chat(prompt)
        return f"{self.disclaimer}\n\n{result}"
    
    def recommend_treatment(self, condition):
        """Provide information about treatment options for a condition"""
        prompt = (
            "You are a medical AI assistant. A user is asking about treatment options for: {condition}\n\n"
            "Provide information about:\n"
            "1. Common evidence-based treatment approaches\n"
            "2. Lifestyle modifications that might help\n"
            "3. What type of healthcare provider typically manages this condition\n"
            "4. Important considerations patients should know\n\n"
            "Focus on providing balanced, evidence-based information while emphasizing the importance of personalized medical advice."
        ).format(condition=condition)
        
        # Get response from BlackboxAI
        result = self.blackbox_ai.chat(prompt)
        return f"{self.disclaimer}\n\n{result}"
    
    def research_disease(self, disease):
        """Research information about a specific disease or medical condition"""
        prompt = (
            "You are a medical AI assistant. A user wants to learn about: {disease}\n\n"
            "Provide comprehensive, well-structured information including:\n"
            "1. Definition and overview of the condition\n"
            "2. Causes and risk factors\n"
            "3. Signs and symptoms\n"
            "4. Diagnostic approaches\n"
            "5. Treatment options\n"
            "6. Prognosis and complications\n"
            "7. Prevention strategies if applicable\n"
            "8. Current research directions\n\n"
            "Use current medical knowledge and emphasize evidence-based information. Format your response with clear headings for readability."
        ).format(disease=disease)
        
        # Get response from BlackboxAI
        result = self.blackbox_ai.chat(prompt)
        return f"{self.disclaimer}\n\n{result}"
    
    def get_blackbox_models(self):
        """Get available models for BlackboxAI"""
        try:
            return self.blackbox_ai.get_available_models()
        except:
            return ["blackboxai"]
    
    def change_provider(self, provider, model=None):
        """Change the AI provider (only blackbox supported)"""
        if provider.lower() != "blackbox":
            return False
            
        if model:
            return self.blackbox_ai.change_model(model)
        return True
    
    def analyze_medical_image(self, image_data, enhancement=None):
        """Placeholder for medical image analysis"""
        return {
            "analysis": "Image analysis would normally process the provided image data.",
            "recommendations": "For actual medical image interpretation, please consult with a radiologist or appropriate specialist."
        }
    
    def extract_visualization_data(self, text, data_type="symptoms"):
        """Placeholder to extract data for visualization"""
        if data_type == "symptoms":
            return {
                "labels": ["Condition A", "Condition B", "Condition C"],
                "values": [85, 60, 35],
                "title": "Possible Conditions"
            }
        elif data_type == "treatments":
            return {
                "labels": ["Option A", "Option B", "Option C"],
                "values": [90, 75, 60],
                "title": "Treatment Effectiveness"
            }
        else:
            return {
                "labels": ["Stage 1", "Stage 2", "Stage 3", "Stage 4"],
                "values": [1, 2, 3, 4],
                "title": "Disease Progression"
            }
    
    def generate_symptom_visualization(self, data):
        """Generate visualization for symptoms"""
        # Just return the data as a string representation
        return str(data)
    
    def generate_treatment_visualization(self, data):
        """Generate visualization for treatments"""
        # Just return the data as a string representation
        return str(data)
    
    def generate_progression_visualization(self, data):
        """Generate visualization for disease progression"""
        # Just return the data as a string representation
        return str(data)
        
    def upload_document(self, file_content, file_name):
        """Placeholder for document upload"""
        return {
            "success": True,
            "message": f"Document {file_name} processed successfully",
            "document_id": str(hash(file_name))
        }
    
    def get_uploaded_documents(self):
        """Get list of uploaded documents"""
        return [] # Empty list as placeholder 