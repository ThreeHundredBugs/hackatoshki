FROM python:3.13-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY conf/requirements.txt conf/requirements.txt
RUN pip install --no-cache-dir -r conf/requirements.txt

# Copy application code
COPY src/ src/

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"] 