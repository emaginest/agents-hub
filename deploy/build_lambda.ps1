# Ensure running with administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Please run this script as Administrator"
    Exit
}

# Remove existing package directory and venv if they exist
if (Test-Path .\deploy\package) {
    Remove-Item -Path .\deploy\package -Recurse -Force
}
if (Test-Path .\deploy\venv) {
    Remove-Item -Path .\deploy\venv -Recurse -Force
}

# Create a temporary directory for packaging
New-Item -ItemType Directory -Force -Path .\deploy\package

try {
    # Create and activate virtual environment with explicit path and permissions
    Write-Host "Creating virtual environment..."
    python -m venv .\deploy\venv --clear
    
    # Activate virtual environment
    Write-Host "Activating virtual environment..."
    .\deploy\venv\Scripts\Activate

    # Install dependencies with Lambda compatibility
    Write-Host "Installing dependencies..."
    pip install --platform manylinux2014_x86_64 --implementation cp --python-version 3.9 --only-binary=:all: --upgrade pip -t .\deploy\package
    pip install --platform manylinux2014_x86_64 --implementation cp --python-version 3.9 --only-binary=:all: -r requirements.txt -t .\deploy\package

    # Copy application code
    Write-Host "Copying application code..."
    Copy-Item -Path .\app -Destination .\deploy\package\app -Recurse -Force
    Copy-Item -Path .\lambda_handler.py -Destination .\deploy\package\ -Force

    # Deactivate virtual environment
    deactivate
}
catch {
    Write-Error "An error occurred: $_"
    Exit 1
}
finally {
    # Clean up virtual environment
    if (Test-Path .\deploy\venv) {
        Remove-Item -Path .\deploy\venv -Recurse -Force
    }
}

# Create ZIP file
Write-Host "Creating Lambda deployment package..."
if (Test-Path .\deploy\lambda_deployment.zip) {
    Remove-Item -Path .\deploy\lambda_deployment.zip -Force
}
Compress-Archive -Path .\deploy\package\* -DestinationPath .\deploy\lambda_deployment.zip -Force

# Clean up package directory
Remove-Item -Path .\deploy\package -Recurse -Force

Write-Host "Lambda package created at deploy/lambda_deployment.zip"
