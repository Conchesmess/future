# Use official Python image
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Set environment variable for Flask
ENV FLASK_APP=main.py
ENV PYTHONUNBUFFERED=1

# Start the app with Gunicorn (threaded to handle concurrent CDN proxy requests)
# --threads 8 allows up to 8 concurrent CDN fetches per worker without blocking
# --timeout 120 gives large WASM files (12MB+) time to download through the proxy
CMD ["gunicorn", "--workers", "2", "--threads", "8", "--timeout", "120", "--bind", "0.0.0.0:8080", "main:app"]
