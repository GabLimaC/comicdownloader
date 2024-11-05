# src/comic_translator/image_generator.py
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import logging
from .utils import load_json

class ImageGenerator:
  def __init__(self):
      self.logger = logging.getLogger(__name__)
      self.output_dir = Path("data/output")
      self.output_dir.mkdir(parents=True, exist_ok=True)

  def erase_original_text(self, draw, bbox, background_color="white"):
      """Erase the original text by drawing a filled rectangle"""
      x1, y1 = bbox[0]
      x2, y2 = bbox[1]
      
      # Convert to absolute coordinates
      x1 = int(x1 * self.image.width)
      y1 = int(y1 * self.image.height)
      x2 = int(x2 * self.image.width)
      y2 = int(y2 * self.image.height)
      
      # Add padding
      padding = 2
      draw.rectangle(
          [x1-padding, y1-padding, x2+padding, y2+padding],
          fill=background_color
      )

      
  def generate_translated_image(self, original_image_path, translated_text_path):
      """Generate new image with translated text"""
      try:
          # Load original image
          self.image = Image.open(original_image_path)
          draw = ImageDraw.Draw(self.image)
          
          # Load translated text data
          translated_data = load_json(translated_text_path)
          
          # Add translated text to image
          #font = ImageFont.truetype("arial.ttf", 20)  # Adjust font and size as needed
          
          for entry in translated_data:
              # First, erase original text
              for word in entry["original_words"]:
                  self.erase_original_text(draw, word["bbox"])
              
              # Calculate the space needed for translated text
              bbox = entry["bbox"]
              text = entry["translated_text"]
              
              # Convert coordinates
              x1, y1 = bbox[0]
              x2, y2 = bbox[1]
              x1 = int(x1 * self.image.width)
              y1 = int(y1 * self.image.height)
              x2 = int(x2 * self.image.width)
              y2 = int(y2 * self.image.height)
              
              # Calculate text size and position
              font_size = int((y2 - y1) * 0.8)  # 80% of height
              font = ImageFont.truetype("arial.ttf", font_size)
              
              # Adjust font size if text is too wide
              while True:
                  text_bbox = draw.textbbox((0, 0), text, font=font)
                  text_width = text_bbox[2] - text_bbox[0]
                  if text_width <= (x2 - x1) or font_size <= 10:
                      break
                  font_size -= 1
                  font = ImageFont.truetype("arial.ttf", font_size)
              
              # Center text in the space
              text_bbox = draw.textbbox((0, 0), text, font=font)
              text_width = text_bbox[2] - text_bbox[0]
              text_height = text_bbox[3] - text_bbox[1]
              
              text_x = x1 + ((x2 - x1) - text_width) // 2
              text_y = y1 + ((y2 - y1) - text_height) // 2
              
              # Draw text
              draw.text((text_x, text_y), text, font=font, fill="black")
          
          # Save new image
          output_path = self.output_dir / f"{Path(original_image_path).stem}_translated.jpg"
          self.image.save(output_path)
          
          self.logger.info(f"Successfully generated translated image: {output_path}")
          return str(output_path)
          
      except Exception as e:
          self.logger.error(f"Error generating translated image: {str(e)}")
          return None