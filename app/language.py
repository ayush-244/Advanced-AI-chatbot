from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
import re

# Make langdetect deterministic
DetectorFactory.seed = 0


class LanguageProcessor:

    def detect_lang(self, text):
        try:
            # Check if text is primarily English by common patterns
            english_patterns = [
                r'\b(what|who|where|when|why|how|is|are|was|were|the|a|an)\b'
            ]
            
            text_lower = text.lower()
            english_word_count = sum(
                len(re.findall(pattern, text_lower)) 
                for pattern in english_patterns
            )
            
            # If 2+ common English words, assume English
            if english_word_count >= 2:
                return "en"
            
            # Check for common Hindi/Hinglish words
            hindi_patterns = [
                r'\b(kya|kaun|kaise|kab|kahan|kyun|hai|hain|the|ko|ka|ki|ke|batao|bata)\b'
            ]
            
            hindi_word_count = sum(
                len(re.findall(pattern, text_lower)) 
                for pattern in hindi_patterns
            )
            
            # If 2+ common Hindi words, assume Hindi
            if hindi_word_count >= 2:
                return "hi"
            
            # For short text, be conservative
            if len(text.split()) < 5:
                # Try detection but default to English on ambiguity
                lang = detect(text)
                # Common misdetections for short English queries
                if lang in ['so', 'cy', 'ro', 'pl', 'af', 'nl', 'fi', 'et']:
                    return "en"
                return lang
            
            return detect(text)
        except:
            return "en"


    def to_english(self, text, lang):
        if lang == "en":
            return text

        try:
            return GoogleTranslator(
                source=lang,
                target="en"
            ).translate(text)
        except:
            return text


    def from_english(self, text, lang):
        if lang == "en":
            return text

        try:
            return GoogleTranslator(
                source="en",
                target=lang
            ).translate(text)
        except:
            return text
