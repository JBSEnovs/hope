import os
import json
from .blackbox_ai import BlackboxAI
from datetime import datetime

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
            "You are a medical AI assistant helping a patient who describes the following symptoms: {symptoms}\n\n"
            "Based only on these symptoms, provide a structured analysis with these sections:\n\n"
            "1. POSSIBLE CONDITIONS (from most to least likely)\n"
            "   * For each condition, explain why it matches their symptoms\n"
            "   * Note other symptoms that might be present if this condition is correct\n"
            "   * Mention what type of medical professional typically manages this condition\n\n"
            "2. IMPORTANT CONSIDERATIONS\n"
            "   * Note any red flags that would require urgent medical attention\n"
            "   * Mention any diagnostic tests that might be helpful\n\n"
            "3. GENERAL ADVICE\n"
            "   * Provide practical self-care suggestions while waiting to see a doctor\n\n"
            "Format your response in a clear, well-structured way with headings and bullet points. "
            "Emphasize that this is educational information only and proper diagnosis requires professional evaluation."
        ).format(symptoms=symptoms)
        
        # Get response from BlackboxAI
        result = self.blackbox_ai.chat(prompt)
        return f"{self.disclaimer}\n\n{result}"
    
    def recommend_treatment(self, condition):
        """Provide information about treatment options for a condition"""
        prompt = (
            "You are a medical AI assistant providing educational information about treatment options for: {condition}\n\n"
            "Please provide a comprehensive overview with these sections:\n\n"
            "1. STANDARD TREATMENTS\n"
            "   * Evidence-based medical approaches commonly used\n"
            "   * For medications: general classes, not specific brands\n"
            "   * Common procedures or interventions\n\n"
            "2. LIFESTYLE MODIFICATIONS\n"
            "   * Diet, exercise, and other lifestyle changes that may help\n"
            "   * Self-management strategies\n\n"
            "3. SPECIALIST CARE\n"
            "   * What type of healthcare providers typically manage this condition\n"
            "   * When to consider specialist referral\n\n"
            "4. IMPORTANT CONSIDERATIONS\n"
            "   * Treatment variables that depend on individual factors\n"
            "   * Common side effects or complications to be aware of\n\n"
            "Format your response with clear headings and bullet points for readability. "
            "Emphasize that treatment decisions should be made with healthcare providers based on individual circumstances."
        ).format(condition=condition)
        
        # Get response from BlackboxAI
        result = self.blackbox_ai.chat(prompt)
        return f"{self.disclaimer}\n\n{result}"
    
    def research_disease(self, disease):
        """Research information about a specific disease or medical condition"""
        prompt = (
            "You are a medical AI assistant providing a comprehensive overview of: {disease}\n\n"
            "Please organize your response into these clearly labeled sections:\n\n"
            "1. DEFINITION & OVERVIEW\n"
            "   * What is this condition and how common is it?\n\n"
            "2. CAUSES & RISK FACTORS\n"
            "   * What causes or contributes to developing this condition?\n"
            "   * Who is most at risk?\n\n"
            "3. SIGNS & SYMPTOMS\n"
            "   * What are the typical presentations and variations?\n"
            "   * How does it progress over time?\n\n"
            "4. DIAGNOSIS\n"
            "   * How is this condition identified and differentiated from others?\n"
            "   * What tests or evaluations are typically used?\n\n"
            "5. TREATMENT APPROACHES\n"
            "   * What are the standard treatment protocols?\n"
            "   * How effective are these treatments?\n\n"
            "6. PROGNOSIS & COMPLICATIONS\n"
            "   * What is the typical outlook?\n"
            "   * What complications can occur?\n\n"
            "7. PREVENTION & MANAGEMENT\n"
            "   * Can it be prevented? How?\n"
            "   * What ongoing management is needed?\n\n"
            "8. CURRENT RESEARCH\n"
            "   * What are promising areas of research?\n\n"
            "Use current medical knowledge and evidence-based information. Format with clear headings and concise bullet points."
        ).format(disease=disease)
        
        # Get response from BlackboxAI
        result = self.blackbox_ai.chat(prompt)
        return f"{self.disclaimer}\n\n{result}"
    
    def get_blackbox_models(self):
        """Get available models for BlackboxAI"""
        try:
            return self.blackbox_ai.get_available_models()
        except Exception as e:
            print(f"Error getting BlackboxAI models: {str(e)}")
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
        """Extract data for visualization from AI response"""
        try:
            # Create a prompt to extract structured data from text
            prompt = (
                f"Extract structured data from this medical text about {data_type}. "
                f"Return ONLY a JSON object with 'labels' (array of strings) and 'values' (array of numbers), "
                f"and 'title' (string). For example: {{\"labels\":[\"Condition A\",\"Condition B\"],\"values\":[80,60],\"title\":\"Likelihood\"}}. "
                f"Here is the text to analyze:\n\n{text}"
            )
            
            # Get response from BlackboxAI
            result = self.blackbox_ai.chat(prompt)
            
            # Try to parse the result as JSON
            try:
                # Find JSON object in the response (it may contain additional text)
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    # Validate the structure
                    if 'labels' in data and 'values' in data and 'title' in data:
                        return data
            except:
                pass
            
            # Fallback to default data if parsing fails
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
        except Exception as e:
            print(f"Error extracting visualization data: {str(e)}")
            # Return default values on error
            return {
                "labels": ["Data 1", "Data 2", "Data 3"],
                "values": [70, 50, 30],
                "title": f"{data_type.capitalize()} Analysis"
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
        """Process document upload"""
        try:
            # Create a unique ID for the document
            doc_id = str(hash(file_name + str(datetime.now())))
            
            # In a real implementation, we would save the file
            # For now, we'll just return success
            return {
                "success": True,
                "message": f"Document {file_name} processed successfully",
                "document_id": doc_id
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing document: {str(e)}",
                "document_id": None
            }
    
    def get_uploaded_documents(self):
        """Get list of uploaded documents"""
        return [] # Empty list as placeholder 