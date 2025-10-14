#!/bin/sh

set -e

# Wait for PostgreSQL (if using database)
if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for PostgreSQL..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Run migrations
uv run python manage.py migrate --noinput

# Collect static files
uv run python manage.py collectstatic --noinput --clear

# Start Gunicorn
exec uv run gunicorn --bind 0.0.0.0:8000 --workers 2 carkeys_project.wsgi:application