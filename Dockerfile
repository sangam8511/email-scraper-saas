FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 5001

# Create and set working directory
WORKDIR /app

# Install system dependencies (required for some python packages like lxml, regex, etc)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn email-validator dnspython

# Copy the entire backend and pre-built static frontend
COPY . .

# Expose the port
EXPOSE 5001

# Command to run the application using Gunicorn for production
CMD ["gunicorn", "-b", "0.0.0.0:5001", "--workers", "1", "--threads", "4", "--timeout", "120", "app:app"]
