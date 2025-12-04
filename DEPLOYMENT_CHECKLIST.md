# Deployment Checklist

## Pre-Deployment

### Security
- [ ] Change `SECRET_KEY` in `.env` (minimum 50 characters)
- [ ] Set `DEBUG=False` in `.env`
- [ ] Generate strong database password (minimum 20 characters)
- [ ] Generate strong Telegram bot token
- [ ] Review and update `ALLOWED_HOSTS`
- [ ] Configure `CORS_ALLOWED_ORIGINS` (not `*`)
- [ ] Set up SSL/TLS certificates
- [ ] Review security headers in nginx.conf
- [ ] Enable HTTPS redirect

### Database
- [ ] Verify PostgreSQL version (15+)
- [ ] Create database backup plan
- [ ] Set up automated backups
- [ ] Test database connection
- [ ] Verify database credentials

### Environment
- [ ] Create `.env` file from `.env.example`
- [ ] Set all required environment variables
- [ ] Verify no hardcoded secrets in code
- [ ] Review all configuration values
- [ ] Test environment variables loading

### Infrastructure
- [ ] Verify Docker installation (20.10+)
- [ ] Verify Docker Compose installation (1.29+)
- [ ] Check disk space (minimum 10GB recommended)
- [ ] Check available memory (minimum 2GB)
- [ ] Configure firewall rules
- [ ] Set up domain DNS records
- [ ] Reserve ports (80, 443, 5432)

## Deployment

### Initial Setup
- [ ] Clone repository
- [ ] Copy `.env.example` to `.env`
- [ ] Update `.env` with production values
- [ ] Create SSL directory: `mkdir -p ssl`
- [ ] Place SSL certificates in `ssl/` directory
- [ ] Build Docker images: `docker-compose build`
- [ ] Start services: `docker-compose up -d`

### Database Setup
- [ ] Run migrations: `docker-compose exec web python manage.py migrate`
- [ ] Create superuser: `docker-compose exec web python manage.py createsuperuser`
- [ ] Collect static files: `docker-compose exec web python manage.py collectstatic --noinput`
- [ ] Verify database connection
- [ ] Test database queries

### Application Verification
- [ ] Check all services running: `docker-compose ps`
- [ ] Test health endpoint: `curl http://localhost:8000/health/`
- [ ] Access admin panel: `/admin`
- [ ] Access API docs: `/docs`
- [ ] Test API endpoints
- [ ] Verify static files loading
- [ ] Verify media files accessible

### Telegram Bot
- [ ] Set bot token in `.env`
- [ ] Update bot webhook (if applicable)
- [ ] Test bot `/start` command
- [ ] Verify authentication flow
- [ ] Test user registration via bot

### Monitoring & Logging
- [ ] Check application logs: `docker-compose logs web`
- [ ] Check database logs: `docker-compose logs db`
- [ ] Check nginx logs: `docker-compose logs nginx`
- [ ] Set up log rotation
- [ ] Configure monitoring alerts
- [ ] Set up uptime monitoring

## Post-Deployment

### Verification
- [ ] Verify HTTPS working
- [ ] Test all API endpoints
- [ ] Test user registration
- [ ] Test product creation
- [ ] Test messaging system
- [ ] Test cart functionality
- [ ] Verify email notifications (if configured)
- [ ] Test admin panel access

### Performance
- [ ] Monitor CPU usage
- [ ] Monitor memory usage
- [ ] Monitor disk usage
- [ ] Check response times
- [ ] Monitor database performance
- [ ] Test under load

### Backups
- [ ] Create initial database backup
- [ ] Test backup restoration
- [ ] Set up automated backup schedule
- [ ] Document backup procedure
- [ ] Store backups securely

### Documentation
- [ ] Document deployment steps
- [ ] Document environment variables
- [ ] Document SSL certificate renewal
- [ ] Document backup procedures
- [ ] Document troubleshooting steps
- [ ] Create runbooks for common tasks

## Maintenance

### Regular Tasks
- [ ] Monitor logs daily
- [ ] Check disk space weekly
- [ ] Verify backups weekly
- [ ] Update dependencies monthly
- [ ] Review security updates monthly
- [ ] Audit access logs monthly

### Updates
- [ ] Plan update schedule
- [ ] Test updates in staging
- [ ] Create backup before updates
- [ ] Update Docker images
- [ ] Update Python packages
- [ ] Update system packages
- [ ] Verify application after updates

### Security
- [ ] Rotate secrets quarterly
- [ ] Review user access quarterly
- [ ] Audit security logs quarterly
- [ ] Update SSL certificates (before expiry)
- [ ] Review CORS configuration
- [ ] Review firewall rules

## Troubleshooting

### Common Issues

**Database Connection Failed**
- [ ] Verify database is running: `docker-compose ps db`
- [ ] Check database logs: `docker-compose logs db`
- [ ] Verify credentials in `.env`
- [ ] Test connection: `docker-compose exec db psql -U user -d marketplace`

**Static Files Not Loading**
- [ ] Collect static files: `docker-compose exec web python manage.py collectstatic --noinput`
- [ ] Check nginx configuration
- [ ] Verify file permissions
- [ ] Check nginx logs

**Application Crashes**
- [ ] Check application logs: `docker-compose logs web`
- [ ] Check error messages
- [ ] Verify environment variables
- [ ] Check database connection
- [ ] Restart service: `docker-compose restart web`

**High Memory Usage**
- [ ] Check running processes: `docker stats`
- [ ] Review application logs for memory leaks
- [ ] Increase container memory limit
- [ ] Optimize database queries
- [ ] Clear cache: `docker-compose exec web python manage.py clear_cache`

**Slow Response Times**
- [ ] Check database performance
- [ ] Review slow query logs
- [ ] Check CPU usage
- [ ] Increase worker count
- [ ] Enable caching
- [ ] Optimize queries

## Rollback Procedure

If deployment fails:

1. Stop current services: `docker-compose down`
2. Restore database from backup: `cat backup.sql | docker-compose exec -T db psql -U user -d marketplace`
3. Checkout previous version: `git checkout <previous-version>`
4. Rebuild images: `docker-compose build`
5. Start services: `docker-compose up -d`
6. Verify application: `curl http://localhost:8000/health/`

## Emergency Contacts

- [ ] Document support contact information
- [ ] Document escalation procedures
- [ ] Document incident response procedures
- [ ] Document communication channels

## Sign-Off

- [ ] Deployment completed successfully
- [ ] All tests passed
- [ ] All monitoring configured
- [ ] Documentation updated
- [ ] Team notified
- [ ] Date: _______________
- [ ] Deployed by: _______________
