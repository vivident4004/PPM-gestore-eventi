#!/bin/sh
# Exit on error
set -e

echo "Collecting static files..."
python -m pip install -r requirements.txt
python manage.py collectstatic --noinput

echo "Build completed successfully!"
