import pytest
from pathlib import Path
from comic_translator.main import process_comic_page

def test_process_comic_page():
  """Test full processing pipeline."""
  url = 'https://mangasee123.com/read-online/Pick-Me-Up-Infinite-Gacha-chapter-1-page-1.html'
  output_path = process_comic_page(url, target_language='en')
  
  assert output_path is not None
  assert output_path.exists()
  assert output_path.suffix == '.png'

def test_process_invalid_url():
  """Test processing with invalid URL."""
  url = 'https://invalid-url.com'
  output_path = process_comic_page(url)
  
  assert output_path is None