# Marketplace API - Deployment Guide

## Overview

This guide covers deploying the Django Marketplace API using Docker and Docker Compose with PostgreSQL database.

## Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 1.29+)
- Git

## Local Development Setup

### 1. Clone and Setup

```bash
git clone <repository-url>
cd marketplace
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` with your local settings:

```env
DEBUG=True
SECRET_KEY=your-development-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=marketplace
DB_USER=marketplace_user
DB_PASSWORD=dev_password_123
DB_HOST=db
DB_PORT=5432
TELEGRAM_BOT_TOKEN=your-bot-token
CORS_ALLOW_ALL_ORIGINS=True
```

### 3. Build and Run Containers

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

### 4. Access Application

- **API**: http://localhost:8000
- **Admin**: http://localhost:8000/admin
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Database**: localhost:5432

### 5. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx
```

## Production Deployment

### 1. Environment Variables

Create `.env` with production settings:

```env
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-min-50-chars
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=marketplace_prod
DB_USER=marketplace_user
DB_PASSWORD=very-secure-password-min-20-chars
DB_HOST=db
DB_PORT=5432
TELEGRAM_BOT_TOKEN=your-production-bot-token
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. SSL/TLS Certificates

Place your SSL certificates in `ssl/` directory:

```bash
mkdir -p ssl
# Copy your certificate files
cp /path/to/cert.pem ssl/
cp /path/to/key.pem ssl/
```

Or use Let's Encrypt with Certbot:

```bash
docker run -it --rm \
  -v ./ssl:/etc/letsencrypt \
  certbot/certbot certonly --standalone \
  -d yourdomain.com -d www.yourdomain.com
```

### 3. Deploy to Server

```bash
# SSH into your server
ssh user@your-server.com

# Clone repository
git clone <repository-url>
cd marketplace

# Create .env file with production values
nano .env

# Build and start
docker-compose -f docker-compose.yml up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### 4. Database Backup

```bash
# Backup PostgreSQL
docker-compose exec db pg_dump -U marketplace_user marketplace > backup.sql

# Restore from backup
cat backup.sql | docker-compose exec -T db psql -U marketplace_user -d marketplace
```

### 5. Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild images
docker-compose build

# Restart services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

## Common Commands

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# View database
docker-compose exec db psql -U marketplace_user -d marketplace

# Access web container shell
docker-compose exec web bash

# Run Django management commands
docker-compose exec web python manage.py <command>

# Check service health
docker-compose ps
```

## Monitoring

### View Logs

```bash
# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs web
```

### Health Checks

```bash
# Check if services are running
docker-compose ps

# Test API
curl http://localhost:8000/health/

# Test database connection
docker-compose exec web python manage.py dbshell
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if database is running
docker-compose ps db

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Static Files Not Loading

```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput --clear

# Check permissions
docker-compose exec web ls -la staticfiles/
```

### Permission Denied Errors

```bash
# Fix file permissions
docker-compose exec web chown -R www-data:www-data /app/media
docker-compose exec web chmod -R 755 /app/media
```

### Out of Memory

Increase Docker memory limits in Docker Desktop settings or:

```bash
# In docker-compose.yml, add to services:
services:
  web:
    mem_limit: 2g
  db:
    mem_limit: 1g
```

## Security Best Practices

1. **Never commit `.env` file** - Use `.env.example` as template
2. **Use strong passwords** - Min 20 characters with mixed case, numbers, symbols
3. **Enable HTTPS** - Always use SSL/TLS in production
4. **Regular backups** - Backup database daily
5. **Update dependencies** - Run `pip install --upgrade` regularly
6. **Monitor logs** - Check logs for errors and suspicious activity
7. **Restrict CORS** - Set specific allowed origins, not all
8. **Use environment variables** - Never hardcode secrets

## Performance Optimization

### Database

```env
# In .env
DB_CONN_MAX_AGE=600
```

### Caching (Optional)

Add Redis to docker-compose.yml:

```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

### Static File Compression

Nginx automatically compresses responses with gzip.

## Scaling

### Increase Web Workers

In `docker-compose.yml`:

```yaml
web:
  command: gunicorn --bind 0.0.0.0:8000 --workers 8 --timeout 120 core.wsgi:application
```

### Load Balancing

Use Nginx upstream with multiple web containers or deploy to Kubernetes.

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Review this guide
3. Check Django documentation: https://docs.djangoproject.com/
4. Check Docker documentation: https://docs.docker.com/
