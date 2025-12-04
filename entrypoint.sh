#!/bin/bash

set -e

echo "🚀 Starting Django Marketplace API..."

# Wait for database to be ready
echo "⏳ Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done
echo "✅ Database is ready!"

# Run migrations
echo "📦 Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create cache table (if using database cache)
echo "💾 Creating cache table..."
python manage.py createcachetable || true

# Start Gunicorn
echo "🌐 Starting Gunicorn..."
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class sync \
    --worker-tmp-dir /dev/shm \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    core.wsgi:application
