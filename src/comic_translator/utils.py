# src/comic_translator/utils.py
import logging
import os
from pathlib import Path

def setup_logging():
  """Configure logging for the application"""
  log_dir = Path("logs")
  log_dir.mkdir(exist_ok=True)
  
  logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
      handlers=[
          logging.FileHandler(log_dir / "comic_translator.log"),
          logging.StreamHandler()
      ]
  )
  return logging.getLogger(__name__)

def ensure_directories():
  """Create necessary directories if they don't exist"""
  directories = [
      "data/downloads",
      "data/extracted_text",
      "data/translated_text",
      "data/output",
      "logs"
  ]
  for dir_path in directories:
      Path(dir_path).mkdir(parents=True, exist_ok=True)

def save_json(data, filepath):
  """Save data to JSON file"""
  import json
  with open(filepath, 'w', encoding='utf-8') as f:
      json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filepath):
  """Load data from JSON file"""
  import json
  with open(filepath, 'r', encoding='utf-8') as f:
      return json.load(f)