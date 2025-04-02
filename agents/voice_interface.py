import os
import io
import json
import base64
import tempfile
import uuid
from datetime import datetime
import re

# For production, you would use a real STT/TTS service like:
# - Google Cloud Speech-to-Text/Text-to-Speech
# - Microsoft Azure Cognitive Services 
# - Amazon Transcribe/Polly
# This implementation simulates these capabilities for demonstration

class VoiceInterface:
    """
    Class for handling voice interactions, including speech-to-text and text-to-speech operations.
    """
    
    def __init__(self):
        """Initialize the voice interface with defaults"""
        self.supported_languages = {
            'en-US': 'English (United States)',
            'en-GB': 'English (United Kingdom)',
            'es-ES': 'Spanish (Spain)',
            'fr-FR': 'French (France)',
            'de-DE': 'German (Germany)',
            'it-IT': 'Italian (Italy)',
            'ja-JP': 'Japanese (Japan)',
            'zh-CN': 'Chinese (Simplified, China)',
            'ru-RU': 'Russian (Russia)',
            'ar-SA': 'Arabic (Saudi Arabia)',
            'hi-IN': 'Hindi (India)',
            'pt-BR': 'Portuguese (Brazil)'
        }
        
        self.voice_options = {
            'default': 'Default synthesized voice',
            'male': 'Male voice',
            'female': 'Female voice',
            'child': 'Child voice',
            'senior': 'Senior voice'
        }
        
        self.medical_terms_patterns = [
            r'\b(?:acute|chronic|benign|malignant|terminal|remission)\b',
            r'\b(?:symptom|diagnosis|prognosis|treatment|therapy|medication)\b',
            r'\b(?:tumor|cancer|diabetes|hypertension|asthma|arthritis)\b',
            r'\b(?:cardiology|neurology|oncology|pediatrics|geriatrics)\b',
            r'\b(?:antibiotic|analgesic|antiviral|antiinflammatory|sedative)\b',
            r'\b(?:MRI|CT scan|X-ray|ultrasound|biopsy|endoscopy)\b'
        ]
        
        # Create storage directories
        self.audio_storage = os.path.join('data', 'audio')
        os.makedirs(self.audio_storage, exist_ok=True)
    
    def transcribe_audio(self, audio_data, language='en-US'):
        """
        Transcribe audio to text.
        
        Args:
            audio_data (str): Base64 encoded audio data
            language (str): Language code for transcription
            
        Returns:
            dict: Transcription results
        """
        try:
            # Validate language code
            if language not in self.supported_languages:
                return {
                    'success': False,
                    'error': f'Unsupported language code: {language}. Supported languages: {", ".join(self.supported_languages.keys())}'
                }
            
            # For demo purposes, let's simulate speech recognition
            # In a real application, you would:
            # 1. Save the audio to a temporary file
            # 2. Send it to a speech recognition service
            # 3. Process the results
            
            # Save audio to disk with a unique ID
            audio_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"audio_{timestamp}_{audio_id}.wav"
            filepath = os.path.join(self.audio_storage, filename)
            
            # Decode and save base64 audio
            audio_bytes = base64.b64decode(audio_data)
            with open(filepath, 'wb') as f:
                f.write(audio_bytes)
            
            # Simulate transcription
            # In a real application, this would call a speech recognition service
            simulated_text = self._simulate_transcription(audio_bytes, language)
            
            # Detect medical terms
            medical_terms = self.extract_medical_terms(simulated_text)
            
            return {
                'success': True,
                'transcription': simulated_text,
                'language': language,
                'language_name': self.supported_languages[language],
                'confidence': 0.85,  # Simulated confidence score
                'audio_id': audio_id,
                'storage_path': filepath,
                'duration_seconds': len(audio_bytes) / 16000,  # Approximate for demo
                'medical_terms_detected': medical_terms
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error transcribing audio: {str(e)}'
            }
    
    def synthesize_speech(self, text, voice_type=None):
        """
        Convert text to speech.
        
        Args:
            text (str): Text to convert to speech
            voice_type (str, optional): Type of voice to use
            
        Returns:
            dict: Speech synthesis results
        """
        try:
            # Validate voice type
            if voice_type and voice_type not in self.voice_options:
                return {
                    'success': False,
                    'error': f'Unsupported voice type: {voice_type}. Supported voice types: {", ".join(self.voice_options.keys())}'
                }
            
            # Use default voice if not specified
            voice_type = voice_type or 'default'
            
            # For demo purposes, simulate text-to-speech
            # In a real application, you would call a TTS service
            
            # Simulate synthesis by creating a dummy audio file
            # This would be replaced with actual TTS API calls
            audio_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"speech_{timestamp}_{audio_id}.wav"
            filepath = os.path.join(self.audio_storage, filename)
            
            # Generate dummy audio data
            # In a real app, this would be the audio from the TTS service
            simulated_audio = self._simulate_speech_synthesis(text, voice_type)
            
            # Save the audio file
            with open(filepath, 'wb') as f:
                f.write(simulated_audio)
            
            # Convert to base64 for web playback
            audio_base64 = base64.b64encode(simulated_audio).decode('utf-8')
            
            return {
                'success': True,
                'audio_data': audio_base64,
                'voice_type': voice_type,
                'text_length': len(text),
                'audio_id': audio_id,
                'storage_path': filepath,
                'duration_seconds': len(text) * 0.07  # Rough approximation
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error synthesizing speech: {str(e)}'
            }
    
    def extract_medical_terms(self, text):
        """
        Extract medical terminology from text.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            list: Extracted medical terms
        """
        medical_terms = set()
        
        # Apply each regex pattern
        for pattern in self.medical_terms_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                medical_terms.add(match.group(0).lower())
        
        return list(medical_terms)
    
    def get_supported_languages(self):
        """
        Get list of supported languages for voice recognition.
        
        Returns:
            dict: Supported languages with codes and names
        """
        return self.supported_languages
    
    def _simulate_transcription(self, audio_bytes, language):
        """
        Simulate speech-to-text for demo purposes.
        
        Args:
            audio_bytes (bytes): Raw audio data
            language (str): Language code
            
        Returns:
            str: Simulated transcription text
        """
        # In a real application, this would call a speech recognition API
        # For demo, return a fixed response based on audio length
        
        # Simple simulation based on the audio length
        audio_length = len(audio_bytes)
        
        if audio_length < 10000:
            return "Short audio sample. I'm experiencing some pain in my chest."
        elif audio_length < 50000:
            return "Medium length audio. I've been having persistent headaches for the past week, especially in the morning. The pain is concentrated around my temples."
        else:
            return "Longer audio recording. I've been experiencing shortness of breath, particularly when I exert myself. I also have a persistent cough that has lasted for about three weeks now. Sometimes I feel a tightness in my chest, especially after physical activity."
    
    def _simulate_speech_synthesis(self, text, voice_type):
        """
        Simulate text-to-speech for demo purposes.
        
        Args:
            text (str): Text to synthesize
            voice_type (str): Type of voice
            
        Returns:
            bytes: Simulated audio data
        """
        # In a real application, this would call a text-to-speech API
        # For demo, create a very simple WAV file
        
        # Generate silence with varying length based on text length
        # This is just a placeholder - real TTS would generate actual speech
        duration_samples = min(len(text) * 1600, 3 * 16000)  # Roughly ~length of text in seconds
        
        # Create a silent WAV file
        sample_rate = 16000  # 16 kHz
        
        # Create silent audio (all zeros)
        silent_audio = bytes(duration_samples)
        
        # Minimal WAV header
        header = bytearray()
        # RIFF header
        header.extend(b'RIFF')
        header.extend((len(silent_audio) + 36).to_bytes(4, byteorder='little'))  # File size - 8
        header.extend(b'WAVE')
        # Format chunk
        header.extend(b'fmt ')
        header.extend((16).to_bytes(4, byteorder='little'))  # Sub-chunk size
        header.extend((1).to_bytes(2, byteorder='little'))  # PCM format
        header.extend((1).to_bytes(2, byteorder='little'))  # Mono
        header.extend(sample_rate.to_bytes(4, byteorder='little'))  # Sample rate
        header.extend((sample_rate * 1).to_bytes(4, byteorder='little'))  # Byte rate
        header.extend((1).to_bytes(2, byteorder='little'))  # Block align
        header.extend((8).to_bytes(2, byteorder='little'))  # Bits per sample
        # Data chunk
        header.extend(b'data')
        header.extend(len(silent_audio).to_bytes(4, byteorder='little'))
        
        # Combine header and audio data
        wav_data = header + silent_audio
        
        return wav_data 