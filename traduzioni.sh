#!/usr/bin/bash
set -e
echo "python manage.py compilemessages -l it"
exec "$@"