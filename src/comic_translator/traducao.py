import os
import json
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import cv2
import numpy as np
from deep_translator import GoogleTranslator
import textwrap
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sklearn.cluster import DBSCAN

def download_image(url, download_folder):
  try:
      # Set up Selenium WebDriver
      service = Service(ChromeDriverManager().install())
      options = webdriver.ChromeOptions()
      options.add_argument('--headless')  # Run in headless mode
      driver = webdriver.Chrome(service=service, options=options)
      driver.get(url)

      # Wait for the image to load
      wait = WebDriverWait(driver, 10)
      image_element = wait.until(EC.presence_of_element_located(
          (By.CSS_SELECTOR, 'img.img-fluid[ng-src]')))
      image_url = image_element.get_attribute('ng-src')

      # Download the image
      image_response = requests.get(image_url)
      image_response.raise_for_status()

      # Save the image
      if not os.path.exists(download_folder):
          os.makedirs(download_folder)
      image_path = os.path.join(download_folder, 'comic_page.png')
      with open(image_path, 'wb') as f:
          f.write(image_response.content)
      print("Image downloaded successfully")

      driver.quit()
      return image_path
  except Exception as e:
      print(f"Error downloading the image: {e}")
      if 'driver' in locals():
          driver.quit()
      return None

def extract_text(image_path, text_output_folder):
  try:
      # Import required libraries
      import os
      import json
      import numpy as np
      from PIL import Image
      import tensorflow as tf
      from doctr.io import DocumentFile
      from doctr.models import ocr_predictor
      from sklearn.cluster import DBSCAN

      # Load the image
      image = Image.open(image_path)
      
      # Initialize docTR model with better detection for manga/comics
      predictor = ocr_predictor(
          det_arch='db_resnet50', 
          reco_arch='crnn_vgg16_bn',
          pretrained=True,
          assume_straight_pages=True
      )
      
      # Load and prepare image for docTR
      doc = DocumentFile.from_images(image_path)
      result = predictor(doc)
      
      # Extract words with their bounding boxes
      words = []
      for page in result.pages:
          for block in page.blocks:
              for line in block.lines:
                  for word in line.words:
                      # Get coordinates
                      coords = word.geometry
                      # Convert relative coordinates to absolute pixels
                      left = int(coords[0][0] * image.width)
                      top = int(coords[0][1] * image.height)
                      right = int(coords[1][0] * image.width)
                      bottom = int(coords[1][1] * image.height)
                      
                      if word.value.strip():  # Only add non-empty text
                          words.append({
                              'text': word.value,
                              'left': left,
                              'top': top,
                              'right': right,
                              'bottom': bottom,
                              'width': right - left,
                              'height': bottom - top,
                              'center_x': (left + right) / 2,
                              'center_y': (top + bottom) / 2,
                              'confidence': float(word.confidence)
                          })

      # Prepare data for clustering
      if not words:
          raise ValueError("No text detected in the image")

      positions = np.array([[word['center_x'], word['center_y']] for word in words])
      
      # Use DBSCAN clustering to group nearby text
      clustering = DBSCAN(eps=80, min_samples=1).fit(positions)
      labels = clustering.labels_

      # Group words into text blocks
      grouped_blocks = {}
      for idx, label in enumerate(labels):
          if label not in grouped_blocks:
              grouped_blocks[label] = {
                  'text': words[idx]['text'],
                  'left': words[idx]['left'],
                  'top': words[idx]['top'],
                  'right': words[idx]['right'],
                  'bottom': words[idx]['bottom'],
                  'confidence': [words[idx]['confidence']]
              }
          else:
              grouped_blocks[label]['text'] += ' ' + words[idx]['text']
              grouped_blocks[label]['left'] = min(grouped_blocks[label]['left'], words[idx]['left'])
              grouped_blocks[label]['top'] = min(grouped_blocks[label]['top'], words[idx]['top'])
              grouped_blocks[label]['right'] = max(grouped_blocks[label]['right'], words[idx]['right'])
              grouped_blocks[label]['bottom'] = max(grouped_blocks[label]['bottom'], words[idx]['bottom'])
              grouped_blocks[label]['confidence'].append(words[idx]['confidence'])

      # Format text blocks for output
      text_blocks = []
      for block in grouped_blocks.values():
          avg_confidence = sum(block['confidence']) / len(block['confidence'])
          if avg_confidence >= 0.3:  # Filter out low confidence detections
              text_blocks.append({
                  'text': block['text'],
                  'left': int(block['left']),
                  'top': int(block['top']),
                  'width': int(block['right'] - block['left']),
                  'height': int(block['bottom'] - block['top']),
                  'confidence': avg_confidence
              })
      
      print(f"Detected {len(text_blocks)} text blocks")

      # Save text data to JSON
      if not os.path.exists(text_output_folder):
          os.makedirs(text_output_folder)
      text_output_path = os.path.join(text_output_folder, 'original_text.json')
      with open(text_output_path, 'w', encoding='utf-8') as f:
          json.dump(text_blocks, f, ensure_ascii=False, indent=4)
      print(f"Original text saved to {text_output_path}")

      return text_blocks, image

  except Exception as e:
      print(f"Error extracting text from the image: {e}")
      return None, None

def translate_text(text_input_folder, translated_output_folder, target_language='pt'):
  try:
      # Load original text from JSON
      text_input_path = os.path.join(text_input_folder, 'original_text.json')
      with open(text_input_path, 'r', encoding='utf-8') as f:
          text_blocks = json.load(f)

      # Translate text
      translator = GoogleTranslator(source='auto', target=target_language)
      for block in text_blocks:
          block['translated_text'] = translator.translate(block['text'])
      print("Text translated successfully")

      # Save translated text to JSON
      if not os.path.exists(translated_output_folder):
          os.makedirs(translated_output_folder)
      translated_output_path = os.path.join(
          translated_output_folder, 'translated_text.json')
      with open(translated_output_path, 'w', encoding='utf-8') as f:
          json.dump(text_blocks, f, ensure_ascii=False, indent=4)
      print(f"Translated text saved to {translated_output_path}")

      return text_blocks
  except Exception as e:
      print(f"Error translating text: {e}")
      return None

def create_translated_image(image_path, text_input_folder, output_folder):
  try:
      # Load image
      image = Image.open(image_path)

      # Load translated text from JSON
      translated_input_path = os.path.join(text_input_folder, 'translated_text.json')
      with open(translated_input_path, 'r', encoding='utf-8') as f:
          text_blocks = json.load(f)

      # Prepare image for editing
      open_cv_image = np.array(image)
      open_cv_image = open_cv_image[:, :, ::-1].copy()
      mask = np.zeros(open_cv_image.shape[:2], dtype=np.uint8)
      for block in text_blocks:
          x, y, w, h = int(block['left']), int(block['top']), int(block['width']), int(block['height'])
          cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
      inpainted_image = cv2.inpaint(
          open_cv_image, mask, 3, cv2.INPAINT_TELEA)
      result_image = Image.fromarray(
          cv2.cvtColor(inpainted_image, cv2.COLOR_BGR2RGB))
      draw = ImageDraw.Draw(result_image)

      # Load font (update font path as necessary)
      font_path = "arial.ttf"
      for block in text_blocks:
          x, y, w, h = int(block['left']), int(block['top']), int(block['width']), int(block['height'])
          translated_text = block['translated_text']
          if translated_text.strip() != '':
              # Start with a large font size and decrease until it fits
              font_size = 40
              while font_size > 10:
                  font = ImageFont.truetype(font_path, font_size)
                  # Calculate text size
                  lines = textwrap.wrap(translated_text, width=1000)
                  line_height = font.getbbox('Hg')[3] - font.getbbox('Hg')[1]
                  total_height = line_height * len(lines)
                  max_line_width = max([font.getbbox(line)[2] - font.getbbox(line)[0] for line in lines])
                  # Check if text fits within the bounding box
                  if total_height <= h and max_line_width <= w:
                      break
                  font_size -= 2
              else:
                  font = ImageFont.truetype(font_path, font_size)

              # Draw text centered in the bounding box
              y_text = y + (h - total_height) / 2
              for line in lines:
                  line_width = font.getbbox(line)[2] - font.getbbox(line)[0]
                  x_text = x + (w - line_width) / 2
                  draw.text((x_text, y_text), line,
                            font=font, fill=(0, 0, 0))
                  y_text += line_height

      # Save the final image
      if not os.path.exists(output_folder):
          os.makedirs(output_folder)
      output_path = os.path.join(output_folder, 'translated_comic_page.png')
      result_image.save(output_path)
      print(f"Translated image saved as {output_path}")

      return True
  except Exception as e:
      print(f"Error creating translated image: {e}")
      return False

if __name__ == "__main__":
  url = 'https://mangasee123.com/read-online/Pick-Me-Up-Infinite-Gacha-chapter-1-page-1.html'
  download_folder = 'downloaded_pages'
  original_text_folder = 'original_text'
  translated_text_folder = 'translated_text'
  generated_pages_folder = 'generated_pages'
  target_language = 'pt'  # Change as needed

  # Step 1: Download the image
  image_path = download_image(url, download_folder)
  if image_path:
      # Step 2: Extract text and save to JSON
      text_blocks, image = extract_text(
          image_path, original_text_folder)
      if text_blocks:
          # Step 3: Translate text and save to JSON
          translated_blocks = translate_text(
              original_text_folder, translated_text_folder, target_language)
          if translated_blocks:
              # Step 4: Create translated image
              create_translated_image(
                  image_path, translated_text_folder, generated_pages_folder)