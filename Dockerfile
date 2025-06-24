# Use Python 3.10 slim as base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies, INCLUDING GETTEXT
RUN apt-get update \
    && apt-get install -y gettext \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Compila le traduzioni
#RUN python manage.py compilemessages -l it
#COPY traduzioni.sh /traduzioni.sh
#RUN chmod +x /traduzioni.sh
#ENTRYPOINT ["/traduzioni.sh"]
#EXPOSE 8000

RUN chmod +x /build.sh
ENTRYPOINT ["/build.sh"]

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "ProgettoEventi.wsgi:application"]