#!/bin/bash

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "Installing pyenv..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install pyenv
    else
        # Linux
        curl https://pyenv.run | bash
    fi
    
    # Add pyenv to PATH
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
    echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    
    echo "Please restart your terminal and run this script again"
    exit 1
fi

# Install Python 3.11.5
pyenv install 3.11.5
pyenv local 3.11.5

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

echo "Environment setup complete! Use 'source .venv/bin/activate' to activate the environment."