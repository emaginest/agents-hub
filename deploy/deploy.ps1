# Ensure running with administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Please run this script as Administrator"
    Exit
}

function Test-EnvFile {
    if (-not (Test-Path .env)) {
        Write-Error "Missing .env file. Please create one based on .env.example"
        return $false
    }
    return $true
}

function Test-RequiredTools {
    try {
        npm --version | Out-Null
        cdk --version | Out-Null
        aws --version | Out-Null
        return $true
    }
    catch {
        Write-Error "Missing required tools. Please install Node.js, AWS CDK CLI, and AWS CLI"
        return $false
    }
}

function Test-AwsCredentials {
    try {
        aws sts get-caller-identity | Out-Null
        return $true
    }
    catch {
        Write-Error "AWS credentials not configured. Please run 'aws configure'"
        return $false
    }
}

function Clean-CdkOutput {
    Write-Host "Cleaning CDK output..."
    if (Test-Path .\cdk\cdk.out) {
        Remove-Item -Path .\cdk\cdk.out -Recurse -Force
    }
    if (Test-Path .\cdk-outputs.json) {
        Remove-Item -Path .\cdk-outputs.json -Force
    }
}

function Deploy-CDKStack {
    try {
        # Navigate to CDK directory
        Push-Location -Path .\cdk

        # Create and activate virtual environment
        Write-Host "Setting up CDK environment..."
        if (Test-Path .venv) {
            Remove-Item -Path .venv -Recurse -Force
        }
        python -m venv .venv --clear
        .\.venv\Scripts\Activate

        # Install CDK dependencies
        Write-Host "Installing CDK dependencies..."
        pip install -r requirements.txt
        if (-not $?) {
            throw "Failed to install CDK dependencies"
        }

        # Clean output directories
        Write-Host "Cleaning output directories..."
        if (Test-Path .\cdk.out) {
            Remove-Item -Path .\cdk.out -Recurse -Force
        }
        if (Test-Path .\deploy) {
            Remove-Item -Path .\deploy -Recurse -Force
        }

        # Create deploy directory and copy files
        Write-Host "Copying required files..."
        New-Item -ItemType Directory -Force -Path .\deploy
        Copy-Item ..\.env .env -Force
        Copy-Item ..\deploy\lambda_deployment.zip .\deploy\lambda_deployment.zip -Force

        # Deploy the stack
        Write-Host "Deploying CDK stack..."

        # Synthesize with clean output
        Write-Host "Synthesizing CDK stack..."
        cdk synth --no-staging
        if (-not $?) {
            throw "CDK synthesis failed"
        }

        # Acknowledge CLI notice
        Write-Host "Acknowledging CLI notice..."
        cdk acknowledge 32775

        # Deploy with outputs
        Write-Host "Deploying CDK stack..."
        cdk deploy --require-approval never --outputs-file ..\cdk-outputs.json --no-staging
        if (-not $?) {
            throw "CDK deployment failed"
        }

        Write-Host "Deployment successful! Check cdk-outputs.json for API details."
    }
    catch {
        Write-Error "Deployment failed: $_"
        throw
    }
    finally {
        # Clean up
        if (Get-Command deactivate -errorAction SilentlyContinue) {
            deactivate
        }
        Pop-Location
    }
}

# Main deployment process
try {
    # Check prerequisites
    if (-not (Test-EnvFile)) { Exit 1 }
    if (-not (Test-RequiredTools)) { Exit 1 }
    if (-not (Test-AwsCredentials)) { Exit 1 }

    # Clean previous outputs
    Clean-CdkOutput

    # Build Lambda package
    Write-Host "Building Lambda package..."
    .\deploy\build_lambda.ps1
    if (-not $?) {
        throw "Lambda package build failed"
    }

    # Deploy CDK stack
    Deploy-CDKStack

    Write-Host "Deployment complete! API details saved to cdk-outputs.json"
}
catch {
    Write-Error "Deployment failed: $_"
    Exit 1
}
