FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY examples/fastapi_app/requirements.txt ./examples/fastapi_app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r examples/fastapi_app/requirements.txt
RUN pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Run the FastAPI example
CMD ["python", "examples/fastapi_app/main.py"]
