# Use Python slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create a non-root user to run the application
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Expose port
EXPOSE 8001

# Set environment variable for Service A URL (can be overridden at runtime)
ENV SERVICE_A_BASE_URL=http://service-a:8000

# Run the application with Gunicorn
CMD ["gunicorn", "app.main:app", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8001"]