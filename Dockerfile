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

# Start the app (Cloud Run expects $PORT)
CMD ["python", "main.py"]
