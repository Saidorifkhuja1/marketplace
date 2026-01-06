# Docker Setup Guide

## Files Created

### Docker Configuration
- **Dockerfile** - Multi-stage Docker image with Python 3.11, PostgreSQL client, and Gunicorn
- **docker-compose.yml** - Development environment with PostgreSQL, Django, and Nginx
- **docker-compose.prod.yml** - Production environment with optimized settings
- **entrypoint.sh** - Container startup script with database checks and migrations
- **.dockerignore** - Files to exclude from Docker build

### Configuration Files
- **.env.example** - Environment variables template
- **nginx.conf** - Nginx reverse proxy configuration with SSL support
- **start.sh** - Quick start script for easy deployment

### Documentation
- **README.md** - Complete project documentation
- **DEPLOYMENT.md** - Comprehensive deployment guide
- **DEPLOYMENT_CHECKLIST.md** - Pre/post deployment checklist
- **DOCKER_SETUP.md** - This file

### Code Updates
- **core/settings.py** - Updated for environment-based configuration and PostgreSQL
- **core/urls.py** - Added health check endpoint
- **core/health_check.py** - Health check view for monitoring
- **requirements.txt** - Added PostgreSQL driver, Gunicorn, and WhiteNoise

## Quick Start

### Option 1: Automated Setup
```bash
chmod +x start.sh
./start.sh
```

### Option 2: Manual Setup

1. **Create environment file**
```bash
cp .envexample .env
# Edit .env with your settings
```

2. **Build and start**
```bash
docker-compose build
docker-compose up -d
```

3. **Initialize database**
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --noinput
```

4. **Access application**
- API: http://localhost:8000
- Admin: http://localhost:8000/admin
- Docs: http://localhost:8000/docs

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client/Browser                        │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   Nginx (Port 80/443)                    │
│              Reverse Proxy & Load Balancer               │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼────────┐ ┌────▼──────────┐ ┌──▼────────────┐
│  Django Web    │ │  Django Web   │ │  Django Web   │
│  (Port 8000)   │ │  (Port 8000)  │ │  (Port 8000)  │
│  Gunicorn      │ │  Gunicorn     │ │  Gunicorn     │
└───────┬────────┘ └────┬──────────┘ └──┬────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────▼────────────────┐
        │   PostgreSQL Database           │
        │   (Port 5432)                   │
        │   Volume: postgres_data         │
        └─────────────────────────────────┘
```

## Services

### Database (PostgreSQL)
- **Image**: postgres:15-alpine
- **Port**: 5432
- **Volume**: postgres_data
- **Health Check**: Enabled
- **Credentials**: From .env file

### Web Application (Django)
- **Build**: Dockerfile
- **Port**: 8000
- **Workers**: 4 Gunicorn workers
- **Volumes**: 
  - staticfiles
  - media
- **Depends On**: db (healthy)

### Reverse Proxy (Nginx)
- **Image**: nginx:alpine
- **Ports**: 80 (HTTP), 443 (HTTPS)
- **Config**: nginx.conf
- **SSL**: From ssl/ directory
- **Volumes**:
  - Static files
  - Media files
  - SSL certificates

## Environment Variables

### Required
```env
SECRET_KEY=your-secret-key-min-50-chars
DB_PASSWORD=your-db-password-min-20-chars
TELEGRAM_BOT_TOKEN=your-bot-token
```

### Important
```env
DEBUG=False              # Always False in production
ALLOWED_HOSTS=yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### Optional
```env
DB_NAME=marketplace
DB_USER=marketplace_user
DB_HOST=db
DB_PORT=5432
TIME_ZONE=Asia/Tashkent
```

See `.env.example` for all options.

## Common Commands

### Container Management
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View running services
docker-compose ps

# View logs
docker-compose logs -f

# Restart service
docker-compose restart web
```

### Database
```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Database shell
docker-compose exec db psql -U marketplace_user -d marketplace

# Backup database
docker-compose exec db pg_dump -U marketplace_user marketplace > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T db psql -U marketplace_user -d marketplace
```

### Application
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Run tests
docker-compose exec web python manage.py test

# Access shell
docker-compose exec web bash

# Django shell
docker-compose exec web python manage.py shell
```

### Monitoring
```bash
# View resource usage
docker stats

# View specific service logs
docker-compose logs web
docker-compose logs db
docker-compose logs nginx

# Check health endpoint
curl http://localhost:8000/health/
```

## Production Deployment

### Using docker-compose.prod.yml

```bash
# Build with production config
docker-compose -f docker-compose.prod.yml build

# Start with production config
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### Key Differences
- DEBUG=False
- Logging configured
- Resource limits set
- Restart policies: always
- Health checks enabled
- SSL/TLS required

## SSL/TLS Setup

### Using Let's Encrypt

```bash
# Create ssl directory
mkdir -p ssl

# Generate certificate
docker run -it --rm \
  -v ./ssl:/etc/letsencrypt \
  certbot/certbot certonly --standalone \
  -d yourdomain.com -d www.yourdomain.com

# Certificates will be in ssl/live/yourdomain.com/
```

### Manual Certificate

```bash
# Copy your certificates
cp /path/to/cert.pem ssl/cert.pem
cp /path/to/key.pem ssl/key.pem
```

### Update nginx.conf

```nginx
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;
```

## Troubleshooting

### Database Connection Failed
```bash
# Check database status
docker-compose ps db

# View database logs
docker-compose logs db

# Test connection
docker-compose exec db psql -U marketplace_user -d marketplace
```

### Static Files Not Loading
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput --clear

# Check permissions
docker-compose exec web ls -la staticfiles/

# Check nginx logs
docker-compose logs nginx
```

### Port Already in Use
```bash
# Find process using port
lsof -i :8000

# Change port in docker-compose.yml
ports:
  - "8001:8000"
```

### Out of Memory
```bash
# Check memory usage
docker stats

# Increase memory limit in docker-compose.yml
services:
  web:
    mem_limit: 2g
```

## Performance Tips

1. **Database**
   - Use PostgreSQL (not SQLite)
   - Enable connection pooling
   - Index frequently queried fields
   - Regular VACUUM and ANALYZE

2. **Web Application**
   - Increase Gunicorn workers: `--workers 8`
   - Enable caching
   - Optimize database queries
   - Use CDN for static files

3. **Nginx**
   - Enable gzip compression
   - Cache static files
   - Use HTTP/2
   - Enable SSL session caching

4. **Docker**
   - Use Alpine images (smaller)
   - Multi-stage builds
   - Limit container resources
   - Use volumes for persistent data

## Security Checklist

- [ ] Change SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Use strong passwords
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS properly
- [ ] Use environment variables for secrets
- [ ] Regular backups
- [ ] Monitor logs
- [ ] Keep dependencies updated
- [ ] Use non-root user in container

## Next Steps

1. Read [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment guide
2. Review [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) before going live
3. Set up monitoring and alerting
4. Configure automated backups
5. Plan maintenance schedule

## Support

For issues:
1. Check logs: `docker-compose logs -f`
2. Review documentation
3. Check Docker/Django documentation
4. Create GitHub issue with logs and error messages
