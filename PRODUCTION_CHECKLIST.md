# Production Deployment Checklist

Complete this checklist before deploying to production.

## ✅ Pre-Deployment

### Server Setup
- [ ] Provision production server (minimum: 2GB RAM, 2 CPU cores, 40GB storage)
- [ ] Configure DNS records (A records for domain and API subdomain)
- [ ] Set up SSH key authentication
- [ ] Disable password authentication
- [ ] Configure firewall (ports 22, 80, 443)
- [ ] Install security updates
- [ ] Set timezone: `timedatectl set-timezone UTC`

### Security Hardening
- [ ] Run security script: `sudo bash scripts/security.sh`
- [ ] Configure SSH hardening
- [ ] Set up Fail2Ban
- [ ] Enable automatic security updates
- [ ] Configure audit logging
- [ ] Set up file integrity monitoring (AIDE)

### Docker Setup
- [ ] Install Docker Engine: `curl -fsSL https://get.docker.com | sh`
- [ ] Install Docker Compose: `apt-get install docker-compose-plugin`
- [ ] Add deploy user to docker group: `usermod -aG docker deploy`
- [ ] Enable Docker service: `systemctl enable docker`
- [ ] Configure Docker logging driver
- [ ] Set up log rotation for Docker logs

### Environment Configuration
- [ ] Copy `.env.production.example` to `.env`
- [ ] Generate secure JWT keys: `openssl rand -hex 32`
- [ ] Set strong database passwords
- [ ] Configure SMTP settings (if using email)
- [ ] Update domain names in `.env`
- [ ] Set up SSL certificate email in Caddy config
- [ ] Review and update CORS origins

### Database Setup
- [ ] Create database user with limited privileges
- [ ] Configure PostgreSQL connection limits
- [ ] Set up database backup schedule
- [ ] Test database connection
- [ ] Run database migrations
- [ ] Set up pgAdmin access (optional)

### Monitoring Setup
- [ ] Run monitoring script: `sudo bash scripts/monitoring.sh`
- [ ] Configure Prometheus
- [ ] Set up Grafana dashboards
- [ ] Configure alert notifications (email/Slack)
- [ ] Set up health check monitoring
- [ ] Configure log aggregation

### Backup Strategy
- [ ] Configure automated database backups
- [ ] Set up backup retention policy (30 days recommended)
- [ ] Test backup restoration process
- [ ] Configure off-site backup storage
- [ ] Document backup procedures

## 🚀 Deployment

### Initial Deployment
- [ ] Clone repository: `git clone https://github.com/yourusername/yourrepo.git ~/app`
- [ ] Copy `.env` file to `~/app/.env`
- [ ] Copy Caddyfile: `cp caddy/Caddyfile.example caddy/Caddyfile`
- [ ] Update Caddyfile with your domain
- [ ] Build and start services: `docker compose -f docker-compose.prod.yml up -d`
- [ ] Verify all containers are running: `docker compose ps`
- [ ] Check logs: `docker compose logs`

### Application Verification
- [ ] Test health endpoint: `curl https://api.yourdomain.com/health`
- [ ] Test API documentation: `https://api.yourdomain.com/docs`
- [ ] Create test user account
- [ ] Test authentication flow
- [ ] Test calculator operations
- [ ] Verify database persistence
- [ ] Test Redis session management

### SSL/TLS Configuration
- [ ] Verify Caddy automatic HTTPS is working
- [ ] Check SSL certificate validity: `curl -vI https://api.yourdomain.com`
- [ ] Test SSL Labs rating: https://www.ssllabs.com/ssltest/
- [ ] Verify security headers are present
- [ ] Test HTTP to HTTPS redirect
- [ ] Verify HSTS header

### Performance Testing
- [ ] Run load test with realistic traffic
- [ ] Monitor CPU and memory usage
- [ ] Check database connection pool
- [ ] Verify caching is working
- [ ] Test response times under load
- [ ] Monitor error rates

## 🔄 CI/CD Setup

### GitHub Secrets Configuration
- [ ] Add `PROD_SERVER_HOST` secret
- [ ] Add `PROD_SERVER_USER` secret  
- [ ] Add `PROD_SERVER_SSH_KEY` secret
- [ ] Add `PROD_SERVER_PORT` secret (if non-standard)
- [ ] Test SSH connection from GitHub Actions

### Pipeline Testing
- [ ] Push to feature branch and verify tests run
- [ ] Create pull request and verify checks pass
- [ ] Merge to main and verify deployment triggers
- [ ] Verify deployment succeeds
- [ ] Test automatic rollback on failure

### Continuous Monitoring
- [ ] Set up deployment notifications (Slack/email)
- [ ] Configure error tracking (Sentry)
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Enable application performance monitoring (APM)
- [ ] Configure log aggregation and analysis

## 📊 Post-Deployment

### Immediate Actions (Day 1)
- [ ] Monitor application logs for errors
- [ ] Check system resource usage
- [ ] Verify all health checks passing
- [ ] Test all critical user flows
- [ ] Monitor error rates
- [ ] Check database performance
- [ ] Verify backup execution

### First Week
- [ ] Review security logs
- [ ] Analyze performance metrics
- [ ] Check SSL certificate expiration dates
- [ ] Review database growth
- [ ] Test backup restoration
- [ ] Update documentation with production URLs
- [ ] Train team on production access procedures

### Ongoing Maintenance
- [ ] Weekly security updates: `apt-get update && apt-get upgrade`
- [ ] Monthly SSL certificate check
- [ ] Monthly backup restoration test
- [ ] Quarterly security audit
- [ ] Review and rotate secrets every 90 days
- [ ] Monitor disk space and plan capacity
- [ ] Review and optimize database queries

## 🆘 Emergency Procedures

### Rollback Procedure
```bash
# SSH into production server
ssh deploy@your-server.com

# Navigate to app directory
cd ~/app

# Roll back to previous commit
git log --oneline -10  # Find the commit to rollback to
git reset --hard <commit-hash>

# Redeploy
docker compose -f docker-compose.prod.yml up -d --no-deps --build web

# Verify
curl http://localhost:8000/health
```

### Database Restoration
```bash
# List available backups
ls -lh ~/app/backups/

# Restore from backup
docker compose exec -T db psql -U postgres fastapi_db < backups/backup_YYYYMMDD_HHMMSS.sql

# Verify restoration
docker compose exec db psql -U postgres -d fastapi_db -c "SELECT COUNT(*) FROM users;"
```

### Service Recovery
```bash
# Check container status
docker compose ps

# View logs
docker compose logs --tail=100 web

# Restart specific service
docker compose restart web

# Full restart
docker compose down
docker compose -f docker-compose.prod.yml up -d
```

## 📞 Contact Information

### Team Contacts
- **DevOps Lead**: [Name] - [email@domain.com]
- **Backend Lead**: [Name] - [email@domain.com]
- **Security Team**: [security@domain.com]
- **On-Call Schedule**: [Link to PagerDuty/Opsgenie]

### Service Providers
- **Hosting**: [Provider name and support contact]
- **DNS**: [Provider name and support contact]
- **Monitoring**: [Provider name and support contact]
- **Backup Storage**: [Provider name and support contact]

### Emergency Contacts
- **24/7 Support**: [Phone number]
- **Escalation Email**: [escalation@domain.com]
- **Status Page**: [https://status.yourdomain.com]

## 📚 Documentation Links

- [Deployment Guide](DEPLOYMENT.md)
- [Development Guide](DEVELOPMENT.md)
- [API Documentation](https://api.yourdomain.com/docs)
- [Architecture Diagram](docs/architecture.md)
- [Runbook](docs/runbook.md)

---

**Last Updated**: [Date]
**Checklist Version**: 1.0
**Next Review**: [Date]
