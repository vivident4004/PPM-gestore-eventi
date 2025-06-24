#!/bin/bash

# Termina lo script se un comando fallisce
set -e

pip install setuptools
pip install --no-cache-dir -r requirements.txt

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py compilemessages -l it
python makesu.py