# src/comic_translator/text_extraction.py
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import numpy as np
from pathlib import Path
import logging
from .utils import save_json

class TextExtractor:
  def __init__(self):
      self.logger = logging.getLogger(__name__)
      
      try:
          self.predictor = ocr_predictor(pretrained=True)
          self.logger.info("OCR model loaded successfully.")
      except Exception as e:
          self.logger.error(f"Failed to load OCR model: {str(e)}")
          raise e
      
      self.output_dir = Path("data/extracted_text")
      self.output_dir.mkdir(parents=True, exist_ok=True)

  def should_merge_words(self, word1, word2, threshold_y=0.1, threshold_x=0.1):
      """
      Determine if two words should be merged based on their proximity
      """
      bbox1 = word1["bbox"]
      bbox2 = word2["bbox"]
      
      # Calculate vertical and horizontal distances between words
      vertical_diff = abs(bbox1[0][1] - bbox2[0][1])  # Compare y-coordinates
      horizontal_diff = abs(bbox2[0][0] - bbox1[1][0])  # Compare x-coordinates
      
      # Words should be on roughly the same line and close horizontally
      return vertical_diff < threshold_y or horizontal_diff < threshold_x

  def merge_bboxes(self, bbox1, bbox2):
      """
      Merge two bounding boxes into one that encompasses both
      """
      x1 = min(bbox1[0][0], bbox2[0][0])
      y1 = min(bbox1[0][1], bbox2[0][1])
      x2 = max(bbox1[1][0], bbox2[1][0])
      y2 = max(bbox1[1][1], bbox2[1][1])
      return [[x1, y1], [x2, y2]]

  def extract_text(self, image_path):
      """Extract text from comic page"""
      try:
          # Load image
          doc = DocumentFile.from_images(image_path)
          
          # Perform OCR
          result = self.predictor(doc)
          
          # Extract words with their positions
          word_data = []
          for page in result.pages:
              for block_idx, block in enumerate(page.blocks):
                  for line_idx, line in enumerate(block.lines):
                      for word in line.words:
                          word_data.append({
                              "text": word.value,
                              "bbox": word.geometry,
                              "line_idx": f"{block_idx}_{line_idx}",
                              "original_bbox": word.geometry  # Keep original bbox
                          })
          
          # Group words into sentences while preserving individual word data
          grouped_data = []
          
          if not word_data:
              self.logger.warning(f"No text detected in {image_path}")
              return []

          # Sort words by vertical position then horizontal
          sorted_words = sorted(word_data, key=lambda w: (w["bbox"][0][1], w["bbox"][0][0]))
          
          current_group = {
              "text": sorted_words[0]["text"],
              "words": [sorted_words[0]],
              "bbox": sorted_words[0]["bbox"],
              "line_idx": sorted_words[0]["line_idx"]
          }
          
          for word in sorted_words[1:]:
              # Check if we should merge with current group
              if self.should_merge_words(current_group, word):
                  # Add to current group
                  current_group["text"] += " " + word["text"]
                  current_group["words"].append(word)
                  current_group["bbox"] = self.merge_bboxes(current_group["bbox"], word["bbox"])
              else:
                  # Start new group
                  grouped_data.append(current_group)
                  current_group = {
                      "text": word["text"],
                      "words": [word],
                      "bbox": word["bbox"],
                      "line_idx": word["line_idx"]
                  }
          
          # Add the last group
          grouped_data.append(current_group)
          
          # Save results
          output_path = self.output_dir / f"{Path(image_path).stem}_text.json"
          save_json(grouped_data, output_path)
          
          # Debug logging
          self.logger.debug(f"Extracted {len(grouped_data)} text groups")
          for group in grouped_data:
              self.logger.debug(f"Group text: {group['text']}")
              self.logger.debug(f"Word count: {len(group['words'])}")
          
          return grouped_data
          
      except Exception as e:
          self.logger.error(f"Error extracting text: {str(e)}")
          import traceback
          self.logger.error(traceback.format_exc())
          return None