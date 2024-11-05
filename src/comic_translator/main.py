# src/comic_translator/main.py
from .downloader import ComicDownloader
from .text_extraction import TextExtractor
from .translator import Translator
from .image_generator import ImageGenerator
from .utils import setup_logging, ensure_directories
from pathlib import Path

class ComicTranslator:
  def __init__(self):
      self.logger = setup_logging()
      ensure_directories()
      
      self.downloader = ComicDownloader()
      self.extractor = TextExtractor()
      self.translator = Translator()
      self.generator = ImageGenerator()
      
  def process_comic_page(self, url, page_name, target_lang="en"):
      """Process a single comic page"""
      # Download page
      image_path = self.downloader.download_comic_page(url, page_name)
      if not image_path:
          return False
          
      # Extract text
      extracted_data = self.extractor.extract_text(image_path)
      if not extracted_data:
          return False
          
      # Translate text
      extracted_text_path = Path("data/extracted_text") / f"{page_name}_text.json"
      translated_data = self.translator.translate_text(extracted_text_path, target_lang)
      if not translated_data:
          return False
          
      # Generate new image
      translated_text_path = Path("data/translated_text") / f"{page_name}_text_translated.json"
      final_image_path = self.generator.generate_translated_image(image_path, translated_text_path)
      if not final_image_path:
          return False
          
      self.logger.info(f"Successfully processed comic page: {page_name}")
      return True