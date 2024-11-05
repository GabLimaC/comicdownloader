import logging
from pathlib import Path
from typing import Optional
import sys
from .utils import setup_logging, ensure_data_dirs
from .downloader import download_image
from .text_extraction import extract_text
from .translator import translate_text
from .image_generator import ImageGenerator

logger = logging.getLogger(__name__)

def process_comic_page(url: str, target_language: str = 'pt') -> Optional[Path]:
  """
  Process a comic page: download, extract text, translate, and generate new image.
  
  Args:
      url: URL of the comic page
      target_language: Target language code for translation
      
  Returns:
      Path to generated image or None if processing fails
  """
  try:
      # Set up directories
      downloads_dir, extracted_text_dir, translated_text_dir, output_dir = ensure_data_dirs()

      # Step 1: Download image
      logger.info(f"Downloading image from: {url}")
      image_path = download_image(url, downloads_dir)
      if not image_path:
          raise Exception("Failed to download image")

      # Step 2: Extract text
      logger.info("Extracting text from image")
      text_blocks, image = extract_text(image_path, extracted_text_dir)
      if not text_blocks:
          raise Exception("Failed to extract text")

      # Step 3: Translate text
      logger.info(f"Translating text to {target_language}")
      translated_blocks = translate_text(extracted_text_dir, translated_text_dir, target_language)
      if not translated_blocks:
          raise Exception("Failed to translate text")

      # Step 4: Generate translated image
      logger.info("Generating translated image")
      generator = ImageGenerator()
      output_path = generator.create_translated_image(image_path, translated_text_dir, output_dir)
      if not output_path:
          raise Exception("Failed to generate translated image")

      logger.info("Comic page processing completed successfully!")
      return output_path

  except Exception as e:
      logger.error(f"Error processing comic page: {e}")
      return None

def main():
  """Main entry point for the comic translator."""
  setup_logging()
  
  url = 'https://mangasee123.com/read-online/Pick-Me-Up-Infinite-Gacha-chapter-1-page-1.html'
  target_language = 'pt'
  
  try:
      output_path = process_comic_page(url, target_language)
      if not output_path:
          sys.exit(1)
      logger.info(f"Translation complete. Output saved to: {output_path}")
  
  except KeyboardInterrupt:
      logger.info("Process interrupted by user")
      sys.exit(1)
  except Exception as e:
      logger.error(f"Unexpected error: {e}")
      sys.exit(1)

if __name__ == "__main__":
  main()