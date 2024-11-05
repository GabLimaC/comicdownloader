# run.py
from comic_translator.main import ComicTranslator
import logging

# Set up logging at the start of your program
"""def setup_logging():

  
  # Create a file handler
  file_handler = logging.FileHandler('logs/debug.log')
  file_handler.setLevel(logging.DEBUG)
  
  # Create a formatter
  formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  file_handler.setFormatter(formatter)
  
  # Get the root logger and add handlers
  root_logger = logging.getLogger()
  root_logger.setLevel(logging.DEBUG)
  root_logger.addHandler(file_handler)
"""
def main():
  #setup_logging()
  translator = ComicTranslator()
  
  # Example usage
  url = "https://mangasee123.com/read-online/Pick-Me-Up-Infinite-Gacha-chapter-1-page-1.html"  # Replace with actual comic URL
  translator.process_comic_page(url, "page1", target_lang="en")

if __name__ == "__main__":
  main()