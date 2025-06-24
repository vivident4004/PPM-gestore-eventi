#!/bin/sh
# Exit on error
set -e
python manage.py migrate --noinput
python manage.py setup_groups
python manage.py makesu
python manage.py compilemessages -l it
python manage.py collectstatic --noinput
echo "Deployment tasks completed successfully!"
