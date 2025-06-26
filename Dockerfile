# Usa Python 3.10 slim come immagine base
FROM python:3.10-slim

# Imposta variabili d'ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Imposta la cartella di lavoro
WORKDIR /app

# Installa dipendenze di sistema
RUN apt-get update \
    && apt-get install -y gettext \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Installa dipendenze Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia l'intero progetto
COPY . /app/

# Operazioni che sono nel build.sh accorpate in uno unico strato RUN
RUN \
  python manage.py migrate && \
  python manage.py compilemessages -l it && \
  python manage.py collectstatic --noinput && \
  python makesu.py --noinput

EXPOSE 8000

# Incluso anche nel docker-compose.yml
CMD ["gunicorn", "ProgettoEventi.wsgi:application", "--bind", "0.0.0.0:8000"]