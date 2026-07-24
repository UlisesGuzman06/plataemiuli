#!/usr/bin/env bash
# exit on error
set -o errexit

export PYTHONDONTWRITEBYTECODE=1

find . -name "*.pyc" -delete 2>/dev/null || true
find . -type d -name "__pycache__" -delete 2>/dev/null || true

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py seed_data
