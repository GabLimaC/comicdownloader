# src/comic_translator/translator.py
from deep_translator import GoogleTranslator
from pathlib import Path
import logging
from .utils import save_json, load_json
import time

class Translator:
  def __init__(self):
      self.logger = logging.getLogger(__name__)
      self.output_dir = Path("data/translated_text")
      self.output_dir.mkdir(parents=True, exist_ok=True)
      
  def translate_text(self, extracted_text_path, target_lang='pt'):
      """Translate extracted text to target language"""
      try:
          # Load extracted text
          extracted_data = load_json(extracted_text_path)
          
          # Translate each text entry
          translated_data = []
          
          for entry in extracted_data:
              try:
                  # Create a new translator instance for each translation
                  # and explicitly set source language to English
                  translator = GoogleTranslator(source='auto', target='pt')
                  
                  # Clean and prepare the text
                  text_to_translate = entry["text"].strip()
                  print("Text to translate:")
                  print(text_to_translate)
  
                    # Perform translation
                  translated_text = translator.translate(text=text_to_translate)

                  self.logger.info(f"Original: {text_to_translate}")
                  self.logger.info(f"Translated: {translated_text}")
                  
              except Exception as translation_error:
                  print(f"Translation error for text '{text_to_translate}': {str(translation_error)}")
                  break
              
              translated_data.append({
                  "original_text": entry["text"],
                  "translated_text": translated_text,
                  "original_words": entry["words"],
                  "bbox": entry["bbox"]
              })
          
          # Save translated data
          output_path = self.output_dir / f"{Path(extracted_text_path).stem}_translated.json"
          save_json(translated_data, output_path)
          
          self.logger.info(f"Successfully translated text from {extracted_text_path}")
          return translated_data
          
      except Exception as e:
          self.logger.error(f"Error translating text: {str(e)}")
          return None

  def detect_language(self, text):
      """Detect the language of the text"""
      try:
          translator = GoogleTranslator(source='auto', target='en')
          return translator.detect(text)
      except:
          return 'en'  # default to English if detection fails