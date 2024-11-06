# Comic Translator

An automated comic translation tool that processes comic pages by extracting text, translating it, and generating new images with the translated text.

## Features

- Text extraction from comic images using OCR
- Automatic translation to target language
- Generation of new images with translated text
- Preservation of original text positioning and styling

## Requirements

- Python 3.10-3.11
- Windows OS
- Chrome/ChromeDriver (for Selenium)

## Installation

1. Clone the repository
```
git clone https://github.com/GabLimaC/comictranslator.git
cd comic-translator
```

2. Set up the environment
```
# Run setup script
scripts\setupwin.bat

# Activate virtual environment
.venv\Scripts\activate
```

3. Install the package
```
pip install -e .
```

## Project Structure

```
comic_translator/
│
├── src/comic_translator/    # Source code
│   ├── __init__.py
│   ├── main.py             # Main orchestration
│   ├── downloader.py       # Comic page downloader
│   ├── text_extraction.py  # OCR text extraction
│   ├── translator.py       # Text translation
│   ├── image_generator.py  # Translated image generation
│   └── utils.py           # Utilities and logging
│
├── tests/                  # Test files
│   ├── __init__.py
│   ├── test_extraction.py
│   └── test_integration.py
│
├── scripts/               # Setup scripts
│   ├── setup_env.ps1
│   ├── create_venv.ps1
│   └── setupwin.bat
│
├── data/                  # Data directories
│   ├── downloads/         # Downloaded comic pages
│   ├── extracted_text/    # Extracted text JSON files
│   ├── translated_text/   # Translated text JSON files
│   └── output/           # Final translated images
│
├── logs/                  # Log files
├── requirements.txt       # Project dependencies
├── setup.py              # Package installation
└── run.py                # Main execution script
```

## Usage

1. Activate the virtual environment (if not already activated):
```
.venv\Scripts\activate
```

2. Run the program:
```
python run.py
```

## Dependencies

Main dependencies (see requirements.txt for complete list):
- doctr (OCR)
- deep-translator
- Pillow (Image processing)
- selenium (Web scraping)

## Development

To set up the development environment:

1. Create and activate virtual environment
2. Install development dependencies:
```
pip install -e ".[dev]"
```

## License

[MIT License](LICENSE)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
