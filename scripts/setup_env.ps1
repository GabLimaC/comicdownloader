# Ensure we stop on errors
$ErrorActionPreference = "Stop"

# Function to Write Status Messages
function Write-Status {
    param($Step, $Message)
    Write-Host "`n[Step $Step] $Message" -ForegroundColor Cyan
}

# Function to handle errors
function Handle-Error {
    param($ErrorMessage)
    Write-Host "`nError: $ErrorMessage" -ForegroundColor Red
    Set-ExecutionPolicy Restricted -Scope CurrentUser -Force
    exit 1
}

try {
    # Get project root directory
    $PROJECT_ROOT = (Get-Item $PSScriptRoot).Parent.FullName
    Write-Status "1/6" "Setting up environment in: $PROJECT_ROOT"
    Set-Location $PROJECT_ROOT

    # Check if pyenv is installed
    Write-Status "2/6" "Checking pyenv installation..."
    $pyenvPath = "$env:USERPROFILE\.pyenv\pyenv-win\bin"
    
    if (-not (Test-Path "$pyenvPath\pyenv.bat")) {
        Write-Host "pyenv not found. Installing pyenv-win..." -ForegroundColor Yellow
        
        # Download and run pyenv-win installer
        $installer = "install-pyenv-win.ps1"
        Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile $installer
        & ".\$installer"
        Remove-Item $installer
        
        # Update PATH for current session
        $env:Path = "$env:USERPROFILE\.pyenv\pyenv-win\bin;$env:USERPROFILE\.pyenv\pyenv-win\shims;$env:Path"
        
        Write-Host "pyenv-win installed. Please restart your terminal and run this script again." -ForegroundColor Green
        exit 0
    }

    # Ensure pyenv is in PATH for current session
    Write-Status "3/6" "Configuring pyenv environment..."
    $env:PYENV_ROOT = "$env:USERPROFILE\.pyenv\pyenv-win"
    $env:Path = "$env:PYENV_ROOT\bin;$env:PYENV_ROOT\shims;$env:Path"

    # Install Python 3.11.5 if needed
    Write-Status "4/6" "Setting up Python 3.11.5..."
    $pythonVersions = & pyenv versions
    if ($pythonVersions -notmatch "3.11.5") {
        Write-Host "Installing Python 3.11.5..." -ForegroundColor Yellow
        $output = & pyenv install 3.11.5 2>&1
        if ($LASTEXITCODE -ne 0) {
            Handle-Error "Failed to install Python 3.11.5`n$output"
        }
        
        # Verify installation
        $pythonVersions = & pyenv versions
        if ($pythonVersions -notmatch "3.11.5") {
            Handle-Error "Python 3.11.5 installation verification failed"
        }
    }
    else {
        Write-Host "Python 3.11.5 is already installed" -ForegroundColor Green
    }

    # Set local version
    Write-Status "5/6" "Setting local Python version..."
    $output = & pyenv local 3.11.5 2>&1
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to set local Python version`n$output"
    }

    # Create virtual environment
    Write-Status "6/6" "Setting up virtual environment..."
    $createVenvScript = Join-Path $PSScriptRoot "create_venv.ps1"
    if (-not (Test-Path $createVenvScript)) {
        Handle-Error "create_venv.ps1 script not found"
    }
    
    & $createVenvScript
    if ($LASTEXITCODE -ne 0) {
        Handle-Error "Failed to create virtual environment"
    }

    Write-Host "`nSetup completed successfully!" -ForegroundColor Green
}
catch {
    Handle-Error $_.Exception.Message
}