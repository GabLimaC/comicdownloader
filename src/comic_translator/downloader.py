# src/comic_translator/downloader.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import requests
from pathlib import Path
import logging

class ComicDownloader:
  def __init__(self):
      self.logger = logging.getLogger(__name__)
      self.download_dir = Path("data/downloads")
      self.download_dir.mkdir(parents=True, exist_ok=True)
      
      chrome_options = Options()
      chrome_options.add_argument("--headless")
      chrome_options.add_argument("--disable-gpu")
      
      self.driver = webdriver.Chrome(options=chrome_options)
      
  def download_comic_page(self, url, page_name):
      """Download a single comic page"""
      try:
          self.driver.get(url)
          WebDriverWait(self.driver, 10).until(
              EC.presence_of_element_located((By.TAG_NAME, "img"))
          )
          
          # Find comic image
          image_element = self.driver.find_element(By.CSS_SELECTOR, "img.img-fluid[ng-src]")
          image_url = image_element.get_attribute("ng-src")
          
          # Download image
          response = requests.get(image_url)
          if response.status_code == 200:
              output_path = self.download_dir / f"{page_name}.jpg"
              with open(output_path, "wb") as f:
                  f.write(response.content)
              self.logger.info(f"Successfully downloaded {page_name}")
              return str(output_path)
          else:
              self.logger.error(f"Failed to download image: {response.status_code}")
              return None
              
      except Exception as e:
          self.logger.error(f"Error downloading comic page: {str(e)}")
          return None
          
  def __del__(self):
      self.driver.quit()