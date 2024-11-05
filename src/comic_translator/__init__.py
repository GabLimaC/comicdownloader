# src/comic_translator/__init__.py
from .downloader import ComicDownloader
from .text_extraction import TextExtractor
from .translator import Translator
from .image_generator import ImageGenerator

__version__ = "0.1.0"