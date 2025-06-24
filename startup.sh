#!/bin/sh

# Questo script viene eseguito ogni volta che il container si avvia.

# Il comando 'set -e' assicura che lo script si interrompa immediatamente se un comando fallisce.
set -e

# 1. Compila i messaggi di traduzione
# Questo ora viene eseguito all'avvio, quando il DB è potenzialmente raggiungibile (anche se non necessario per questo comando)
echo "Compiling messages..."
python manage.py compilemessages -l it

# 2. Applica le migrazioni del database
# Questo è il posto perfetto per eseguire le migrazioni!
echo "Applying database migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

# 3. Avvia il server Gunicorn
# Il comando 'exec' è importante: sostituisce il processo dello script con il processo di Gunicorn.
# Questo permette a Gunicorn di ricevere correttamente i segnali di stop da Railway.
echo "Starting Gunicorn..."
exec gunicorn ProgettoEventi.wsgi:application