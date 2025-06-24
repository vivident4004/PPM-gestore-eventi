#!/bin/sh
# Assicura che lo script si interrompa immediatamente se un comando fallisce.
set -e
# Applica le migrazioni del database
python manage.py migrate --noinput
python manage.py makesu