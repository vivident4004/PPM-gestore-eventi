#!/bin/bash

# Termina lo script se un comando fallisce
set -e

#pip install setuptools
pip install --no-cache-dir -r requirements.txt

python manage.py makemigrations
python manage.py migrate
# La compilazione della traduzione va fatta prima di collectstatic
python manage.py compilemessages -l it
python manage.py collectstatic --noinput
python makesu.py --noinput
# Avvia il processo passato come CMD/command
exec "$@"