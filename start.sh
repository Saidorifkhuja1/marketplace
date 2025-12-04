#!/bin/bash

# Marketplace API - Quick Start Script

set -e

echo "🚀 Marketplace API - Quick Start"
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
    echo "   Then run this script again"
    exit 0
fi

# Check if .env has been customized
if grep -q "your-secret-key-change-this" .env; then
    echo "⚠️  Please update SECRET_KEY in .env file"
    exit 1
fi

if grep -q "your-bot-token" .env; then
    echo "⚠️  Please update TELEGRAM_BOT_TOKEN in .env file"
    exit 1
fi

echo "✅ Configuration found"

# Build images
echo ""
echo "🔨 Building Docker images..."
docker-compose build

# Start services
echo ""
echo "🌐 Starting services..."
docker-compose up -d

# Wait for database
echo ""
echo "⏳ Waiting for database to be ready..."
sleep 5

# Run migrations
echo ""
echo "📦 Running migrations..."
docker-compose exec -T web python manage.py migrate

# Collect static files
echo ""
echo "📁 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Create superuser prompt
echo ""
echo "👤 Creating superuser..."
docker-compose exec web python manage.py createsuperuser

# Display information
echo ""
echo "✅ Deployment Complete!"
echo ""
echo "📍 Access Points:"
echo "   - API: http://localhost:8000"
echo "   - Admin: http://localhost:8000/admin"
echo "   - Swagger Docs: http://localhost:8000/docs"
echo "   - ReDoc: http://localhost:8000/redoc"
echo "   - Database: localhost:5432"
echo ""
echo "📊 Useful Commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Restart services: docker-compose restart"
echo "   - Access shell: docker-compose exec web bash"
echo ""
echo "🎉 Happy coding!"
