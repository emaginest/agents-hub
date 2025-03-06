#!/bin/bash

# Exit on any error
set -e

function test_env_file() {
    if [ ! -f .env ]; then
        echo "Error: Missing .env file. Please create one based on .env.example"
        return 1
    fi
    return 0
}

function test_required_tools() {
    if ! command -v npm &> /dev/null || \
       ! command -v cdk &> /dev/null || \
       ! command -v aws &> /dev/null; then
        echo "Error: Missing required tools. Please install Node.js, AWS CDK CLI, and AWS CLI"
        return 1
    fi
    return 0
}

function test_aws_credentials() {
    if ! aws sts get-caller-identity &> /dev/null; then
        echo "Error: AWS credentials not configured. Please run 'aws configure'"
        return 1
    fi
    return 0
}

function clean_cdk_output() {
    echo "Cleaning CDK output..."
    rm -rf ./cdk/cdk.out
    rm -f ./cdk-outputs.json
}

function deploy_cdk_stack() {
    local ORIGINAL_DIR=$(pwd)
    
    # Navigate to CDK directory
    cd cdk

    # Create and activate virtual environment
    echo "Setting up CDK environment..."
    rm -rf .venv
    python3 -m venv .venv
    source .venv/bin/activate

    # Set up cleanup trap
    trap cleanup EXIT
    
    # Install CDK dependencies
    echo "Installing CDK dependencies..."
    pip install -r requirements.txt || {
        echo "Error: Failed to install CDK dependencies"
        return 1
    }

    # Copy .env file to CDK directory
    echo "Copying environment variables..."
    cp ../.env .env

    # Deploy the stack
    echo "Deploying CDK stack..."
    
    # Synthesize first to validate
    echo "Synthesizing CDK stack..."
    cdk synth || {
        echo "Error: CDK synthesis failed"
        return 1
    }

    # Deploy with outputs
    echo "Deploying CDK stack..."
    cdk deploy --require-approval never --outputs-file ../cdk-outputs.json || {
        echo "Error: CDK deployment failed"
        return 1
    }

    echo "Deployment successful! Check cdk-outputs.json for API details."
    return 0
}

function cleanup() {
    # Deactivate virtual environment if active
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate
    fi
    
    # Return to original directory
    cd "$ORIGINAL_DIR"
}

# Main deployment process
{
    # Check prerequisites
    test_env_file || exit 1
    test_required_tools || exit 1
    test_aws_credentials || exit 1

    # Clean previous outputs
    clean_cdk_output

    # Build Lambda package
    echo "Building Lambda package..."
    chmod +x deploy/build_lambda.sh
    ./deploy/build_lambda.sh || {
        echo "Error: Lambda package build failed"
        exit 1
    }

    # Deploy CDK stack
    deploy_cdk_stack || exit 1

    echo "Deployment complete! API details saved to cdk-outputs.json"
} || {
    echo "Deployment failed"
    exit 1
}
