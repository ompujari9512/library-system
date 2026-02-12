#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Convert static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Create superuser automatically (fails silently if user already exists)
python manage.py createsuperuser --noinput || true