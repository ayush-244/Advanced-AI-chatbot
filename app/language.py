from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
import re


# Make language detection consistent
DetectorFactory.seed = 0


class LanguageProcessor:

    def detect_lang(self, text):

        try:
            text_lower = text.lower()

            # Check for common English words
            english_patterns = [
                r'\b(what|who|where|when|why|how|is|are|was|were|the|a|an)\b'
            ]

            english_count = sum(
                len(re.findall(pattern, text_lower))
                for pattern in english_patterns
            )

            if english_count >= 2:
                return "en"


            # Check for common Hindi / Hinglish words
            hindi_patterns = [
                r'\b(kya|kaun|kaise|kab|kahan|kyun|hai|hain|the|ko|ka|ki|ke|batao|bata)\b'
            ]

            hindi_count = sum(
                len(re.findall(pattern, text_lower))
                for pattern in hindi_patterns
            )

            if hindi_count >= 2:
                return "hi"


            # Handle short inputs carefully
            if len(text.split()) < 5:

                lang = detect(text)

                # Fix common wrong detections
                if lang in ["so", "cy", "ro", "pl", "af", "nl", "fi", "et"]:
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
