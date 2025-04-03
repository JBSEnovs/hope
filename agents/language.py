import os
import json
import requests

class LanguageManager:
    """
    Manages language preferences and translation services for the MedicalAI Assistant.
    """
    
    def __init__(self):
        """Initialize the language manager with default settings"""
        self.default_language = 'en'
        self.languages_dir = os.path.join('data', 'languages')
        os.makedirs(self.languages_dir, exist_ok=True)
        
        # Load supported languages
        self.supported_languages = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'zh-CN': 'Chinese (Simplified)',
            'ja': 'Japanese',
            'ar': 'Arabic',
            'ru': 'Russian',
            'pt': 'Portuguese',
            'hi': 'Hindi',
            'sw': 'Swahili'
        }
        
        # Load translations
        self.translations = self._load_translations()
    
    def _load_translations(self):
        """Load all translation files"""
        translations = {}
        
        for lang_code in self.supported_languages.keys():
            lang_file = os.path.join(self.languages_dir, f"{lang_code}.json")
            
            if os.path.exists(lang_file):
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        translations[lang_code] = json.load(f)
                except Exception as e:
                    print(f"Error loading translation file {lang_file}: {e}")
                    translations[lang_code] = {}
            else:
                translations[lang_code] = {}
                
                # Create empty translation file if it doesn't exist
                if lang_code != 'en':  # Don't create for English (base language)
                    try:
                        with open(lang_file, 'w', encoding='utf-8') as f:
                            json.dump({}, f, ensure_ascii=False, indent=2)
                    except Exception as e:
                        print(f"Error creating translation file {lang_file}: {e}")
        
        return translations
    
    def translate_text(self, text, target_language=None):
        """
        Translate text to the target language using a web API
        
        Args:
            text (str): Text to translate
            target_language (str): Target language code (ISO 639-1)
            
        Returns:
            str: Translated text
        """
        if not target_language or target_language == self.default_language:
            return text
        
        try:
            # Check if we have a LibreTranslate API key
            api_key = os.getenv("LIBRETRANSLATE_API_KEY", "")
            
            # Try LibreTranslate API if key is available
            if api_key:
                endpoint = os.getenv("LIBRETRANSLATE_URL", "https://translate.argosopentech.com/translate")
                payload = {
                    "q": text,
                    "source": "auto",
                    "target": target_language,
                    "format": "text",
                    "api_key": api_key
                }
                
                response = requests.post(endpoint, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("translatedText", text)
            
            # Fallback: Add translation placeholder to indicate need for translation
            return f"[NEEDS TRANSLATION TO {target_language}]: {text}"
            
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def get_ui_string(self, key, language=None):
        """
        Get a UI string in the specified language
        
        Args:
            key (str): The string identifier
            language (str): Language code (ISO 639-1)
            
        Returns:
            str: Translated string or the key itself if not found
        """
        language = language or self.default_language
        
        # If language is not supported, fall back to default
        if language not in self.supported_languages:
            language = self.default_language
        
        # Check if we have a translation for this key
        if language in self.translations and key in self.translations[language]:
            return self.translations[language][key]
        
        # If no translation is found and language is not English, fall back to English
        if language != 'en' and 'en' in self.translations and key in self.translations['en']:
            return self.translations['en'][key]
        
        # If still no translation found, return the key itself
        return key
    
    def add_translation(self, key, value, language):
        """
        Add or update a translation
        
        Args:
            key (str): The string identifier
            value (str): The translated string
            language (str): Language code (ISO 639-1)
            
        Returns:
            bool: Success status
        """
        if language not in self.supported_languages:
            return False
        
        # Make sure this language exists in our translations
        if language not in self.translations:
            self.translations[language] = {}
        
        # Add/update the translation
        self.translations[language][key] = value
        
        # Save the updated translations
        lang_file = os.path.join(self.languages_dir, f"{language}.json")
        try:
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(self.translations[language], f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving translation to {lang_file}: {e}")
            return False
    
    def get_supported_languages(self):
        """
        Get list of supported languages
        
        Returns:
            dict: Dictionary of language codes and names
        """
        return self.supported_languages
    
    def detect_language(self, text):
        """
        Detect the language of the text
        
        Args:
            text (str): Text to analyze
            
        Returns:
            str: Detected language code
        """
        try:
            # Check if we have a LibreTranslate API key
            api_key = os.getenv("LIBRETRANSLATE_API_KEY", "")
            
            # Try LibreTranslate language detection API if key is available
            if api_key:
                endpoint = os.getenv("LIBRETRANSLATE_URL", "https://translate.argosopentech.com/detect")
                payload = {
                    "q": text[:100],  # Just use first 100 chars for detection
                    "api_key": api_key
                }
                
                response = requests.post(endpoint, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    if data and isinstance(data, list) and len(data) > 0:
                        return data[0].get("language", self.default_language)
            
            # Fallback: assume English
            return self.default_language
            
        except Exception as e:
            print(f"Language detection error: {e}")
            return self.default_language
    
    def translate_medical_content(self, content, target_language):
        """
        Translate medical content while preserving medical terminology
        
        Args:
            content (str): Medical content to translate
            target_language (str): Target language code
            
        Returns:
            str: Translated content
        """
        if not target_language or target_language == self.default_language:
            return content
        
        try:
            # Medical terms that should be preserved during translation
            medical_terms = [
                "COVID-19", "MRI", "CT scan", "X-ray", "EKG", "EEG", "CBC", "WBC",
                "RBC", "HDL", "LDL", "BMI", "DNA", "RNA", "HIV", "AIDS", "COPD",
                "IBS", "GERD", "ADHD", "OCD", "PTSD", "TBI", "MS"
            ]
            
            # Replace medical terms with placeholders
            replacements = {}
            for i, term in enumerate(medical_terms):
                placeholder = f"__MEDICAL_TERM_{i}__"
                if term.lower() in content.lower():
                    # Replace the term with the placeholder, preserving case
                    index = content.lower().find(term.lower())
                    actual_term = content[index:index+len(term)]
                    content = content.replace(actual_term, placeholder)
                    replacements[placeholder] = actual_term
            
            # Translate the content
            translated = self.translate_text(content, target_language)
            
            # Replace placeholders back with original medical terms
            for placeholder, term in replacements.items():
                translated = translated.replace(placeholder, term)
            
            return translated
        
        except Exception as e:
            print(f"Medical content translation error: {e}")
            return content 