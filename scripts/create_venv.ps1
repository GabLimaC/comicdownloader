# Ensure we stop on errors
$ErrorActionPreference = "Stop"

try {
    # Get project root directory
    $PROJECT_ROOT = (Get-Item $PSScriptRoot).Parent.FullName
    Set-Location $PROJECT_ROOT

    # Get Python path from pyenv
    $pythonPath = & pyenv which python
    if (-not $pythonPath) {
        throw "Could not find Python path"
    }
    
    Write-Host "Using Python at: $pythonPath" -ForegroundColor Cyan

    # Remove existing virtual environment if it exists
    if (Test-Path ".venv") {
        Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force ".venv"
    }

    # Create new virtual environment
    Write-Host "Creating new virtual environment..." -ForegroundColor Cyan
    & $pythonPath -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create virtual environment"
    }

    # Activate virtual environment
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & .venv\Scripts\Activate.ps1

    # Upgrade pip
    Write-Host "Upgrading pip..." -ForegroundColor Cyan
    & python -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to upgrade pip"
    }

    # Install dependencies
    if (Test-Path "requirements.txt") {
        Write-Host "Installing dependencies..." -ForegroundColor Cyan
        & pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install dependencies"
        }
    }

    Write-Host "`nVirtual environment setup complete!" -ForegroundColor Green
    Write-Host "To activate the environment in a new terminal, run:" -ForegroundColor Yellow
    Write-Host ".venv\Scripts\Activate.ps1" -ForegroundColor Cyan
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}