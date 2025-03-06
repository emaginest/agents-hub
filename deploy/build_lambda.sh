#!/bin/bash

# Exit on any error
set -e

echo "Starting Lambda package build..."

# Clean up existing package directory and venv
rm -rf deploy/package deploy/venv

# Create a temporary directory for packaging
mkdir -p deploy/package

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv deploy/venv

# Activate virtual environment
echo "Activating virtual environment..."
source deploy/venv/bin/activate

try_cleanup() {
    # Deactivate virtual environment
    deactivate || true
    # Clean up virtual environment
    rm -rf deploy/venv
}

# Set up cleanup trap
trap try_cleanup EXIT

# Install dependencies with Lambda compatibility
echo "Installing dependencies..."
pip install --platform manylinux2014_x86_64 --implementation cp --python-version 3.9 --only-binary=:all: --upgrade pip -t deploy/package
pip install --platform manylinux2014_x86_64 --implementation cp --python-version 3.9 --only-binary=:all: -r requirements.txt -t deploy/package

# Copy application code
echo "Copying application code..."
cp -r app deploy/package/
cp lambda_handler.py deploy/package/

# Create ZIP file
echo "Creating Lambda deployment package..."
cd deploy/package
rm -f ../lambda_deployment.zip
zip -r ../lambda_deployment.zip ./*
cd ../..

# Clean up package directory
rm -rf deploy/package

echo "Lambda package created at deploy/lambda_deployment.zip"
