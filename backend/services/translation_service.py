import fasttext
from argostranslate import translate
import os

# Load fasttext model for language detection
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../models/lid.176.bin")

def detect_language(text: str) -> tuple:
    """
    Detect language using fasttext
    Returns: (language_code, confidence)
    """
    try:
        if not os.path.exists(MODEL_PATH):
            print(f"FastText model not found at {MODEL_PATH}, defaulting to English")
            return "en", 1.0
        
        model = fasttext.load_model(MODEL_PATH)
        predictions = model.predict(text.replace('\n', ' '))
        lang_code = predictions[0][0].replace('__label__', '')
        confidence = predictions[1][0]
        return lang_code, confidence
    except Exception as e:
        print(f"Error detecting language: {e}")
        return "en", 1.0  # Default to English

def translate_to_english(text: str, source_lang: str) -> str:
    """
    Translate text to English using argos-translate
    Supports: Spanish (es), German (de), and more
    """
    if source_lang == "en":
        return text
    
    try:
        # Install translation models if not already installed
        installed_languages = translate.get_installed_languages()
        
        # Find source and target languages
        source_lang_obj = None
        target_lang_obj = None
        
        for lang in installed_languages:
            if lang.code == source_lang:
                source_lang_obj = lang
            if lang.code == "en":
                target_lang_obj = lang
        
        if not source_lang_obj or not target_lang_obj:
            print(f"Translation model not available for {source_lang} -> en")
            return text
        
        # Get translation
        translation = source_lang_obj.get_translation(target_lang_obj)
        translated_text = translation.translate(text)
        
        return translated_text
    except Exception as e:
        print(f"Error translating text: {e}")
        return text

def process_text(text: str) -> dict:
    """
    Detect language and translate to English if needed
    Returns: {
        "original_text": str,
        "translated_text": str,
        "language_code": str,
        "confidence": float
    }
    """
    lang_code, confidence = detect_language(text)
    
    if lang_code == "en":
        translated_text = text
    else:
        translated_text = translate_to_english(text, lang_code)
    
    return {
        "original_text": text,
        "translated_text": translated_text,
        "language_code": lang_code,
        "confidence": confidence
    }
