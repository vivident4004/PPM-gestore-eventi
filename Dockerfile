# Use Python 3.10 slim as base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies, INCLUDING GETTEXT
RUN apt-get update && apt-get install -y gettext && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ProgettoEventi.wsgi:application"]
