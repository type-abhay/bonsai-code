#!/bin/bash
set -e

echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo "Creating superuser..."
if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
    echo "Superuser created successfully"
else
    echo "No superuser environment variables found"
fi

echo "Starting Django server..."
exec "$@"
