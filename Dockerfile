# Use Python 3.10 slim as base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y gettext \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/
RUN python manage.py compilemessages -l it
RUN python manage.py collectstatic --noinput

# Run deploy script
COPY deploy.sh /app/deploy.sh
RUN chmod +x /app/deploy.sh

CMD ["gunicorn", "ProgettoEventi.wsgi:application"]