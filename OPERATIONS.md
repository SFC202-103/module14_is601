# Production Operations Quick Reference

Quick commands for common production operations.

## 🚀 Deployment

### Quick Deploy
```bash
# Deploy latest changes
ssh deploy@your-server.com 'cd ~/app && git pull && docker compose -f docker-compose.prod.yml up -d --build'
```

### View Deployment Status
```bash
# Check running containers
ssh deploy@your-server.com 'docker compose ps'

# View recent logs
ssh deploy@your-server.com 'docker compose logs --tail=50 web'
```

## 🔍 Monitoring

### Check Application Health
```bash
# Health check
curl https://api.yourdomain.com/health

# Detailed API docs
curl https://api.yourdomain.com/docs
```

### View Logs
```bash
# Real-time logs
ssh deploy@your-server.com 'docker compose logs -f web'

# Last 100 lines
ssh deploy@your-server.com 'docker compose logs --tail=100 web'

# Filter errors
ssh deploy@your-server.com 'docker compose logs web | grep ERROR'
```

### System Resources
```bash
# Container stats
ssh deploy@your-server.com 'docker stats --no-stream'

# Disk usage
ssh deploy@your-server.com 'df -h'

# Memory usage
ssh deploy@your-server.com 'free -h'

# Running processes
ssh deploy@your-server.com 'htop'
```

## 🗄️ Database Operations

### Database Access
```bash
# Connect to PostgreSQL
ssh deploy@your-server.com 'docker compose exec db psql -U postgres -d fastapi_db'

# Run query
ssh deploy@your-server.com 'docker compose exec -T db psql -U postgres -d fastapi_db -c "SELECT COUNT(*) FROM users;"'

# List all tables
ssh deploy@your-server.com 'docker compose exec -T db psql -U postgres -d fastapi_db -c "\dt"'
```

### Database Backup
```bash
# Manual backup
ssh deploy@your-server.com 'cd ~/app && docker compose exec -T db pg_dump -U postgres fastapi_db > backups/manual_backup_$(date +%Y%m%d_%H%M%S).sql'

# List backups
ssh deploy@your-server.com 'ls -lh ~/app/backups/'

# Download backup
scp deploy@your-server.com:~/app/backups/backup_YYYYMMDD.sql ./local_backup.sql
```

### Database Restore
```bash
# Restore from backup
ssh deploy@your-server.com 'cd ~/app && docker compose exec -T db psql -U postgres fastapi_db < backups/backup_YYYYMMDD_HHMMSS.sql'

# Restore specific table
ssh deploy@your-server.com 'cd ~/app && docker compose exec -T db pg_restore -U postgres -d fastapi_db -t users backups/backup.dump'
```

## 🔄 Service Management

### Restart Services
```bash
# Restart web app only
ssh deploy@your-server.com 'docker compose restart web'

# Restart all services
ssh deploy@your-server.com 'docker compose restart'

# Full rebuild
ssh deploy@your-server.com 'cd ~/app && docker compose -f docker-compose.prod.yml up -d --build'
```

### Stop/Start Services
```bash
# Stop all
ssh deploy@your-server.com 'docker compose stop'

# Start all
ssh deploy@your-server.com 'docker compose start'

# Stop specific service
ssh deploy@your-server.com 'docker compose stop web'
```

### Update Services
```bash
# Pull latest images
ssh deploy@your-server.com 'docker compose pull'

# Apply updates
ssh deploy@your-server.com 'docker compose up -d'
```

## 🧹 Maintenance

### Clean Up Docker
```bash
# Remove unused images
ssh deploy@your-server.com 'docker image prune -af'

# Remove unused volumes
ssh deploy@your-server.com 'docker volume prune -f'

# Complete cleanup
ssh deploy@your-server.com 'docker system prune -af --volumes'
```

### Clean Up Logs
```bash
# Truncate Docker logs
ssh deploy@your-server.com 'sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log'

# Remove old backups (keep 30 days)
ssh deploy@your-server.com 'find ~/app/backups/ -name "*.sql" -mtime +30 -delete'
```

### Update System
```bash
# Update packages
ssh deploy@your-server.com 'sudo apt-get update && sudo apt-get upgrade -y'

# Update Docker
ssh deploy@your-server.com 'curl -fsSL https://get.docker.com | sh'
```

## 🔐 Security

### Check Security Status
```bash
# Fail2ban status
ssh deploy@your-server.com 'sudo fail2ban-client status'

# SSH failed attempts
ssh deploy@your-server.com 'sudo fail2ban-client status sshd'

# Firewall status
ssh deploy@your-server.com 'sudo ufw status verbose'
```

### Unban IP Address
```bash
# Unban from SSH jail
ssh deploy@your-server.com 'sudo fail2ban-client set sshd unbanip <IP_ADDRESS>'

# List banned IPs
ssh deploy@your-server.com 'sudo fail2ban-client status sshd | grep "Banned IP"'
```

### SSL Certificate
```bash
# Check certificate
ssh deploy@your-server.com 'docker compose exec caddy caddy trust'

# Renew certificate manually
ssh deploy@your-server.com 'docker compose restart caddy'
```

## 📊 Performance Analysis

### Slow Query Analysis
```bash
# Enable slow query log
ssh deploy@your-server.com 'docker compose exec -T db psql -U postgres -c "ALTER SYSTEM SET log_min_duration_statement = 1000;"'

# View slow queries
ssh deploy@your-server.com 'docker compose logs db | grep "duration:"'
```

### Connection Pool Status
```bash
# Active connections
ssh deploy@your-server.com 'docker compose exec -T db psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"'

# Detailed connection info
ssh deploy@your-server.com 'docker compose exec -T db psql -U postgres -c "SELECT datname, usename, state, query FROM pg_stat_activity;"'
```

### Application Metrics
```bash
# Request rate (if prometheus is set up)
curl http://your-server.com:9090/api/v1/query?query=rate(http_requests_total[5m])

# Error rate
curl http://your-server.com:9090/api/v1/query?query=rate(http_requests_total{status=~"5.."}[5m])
```

## 🐛 Debugging

### Check Environment Variables
```bash
# View container env vars
ssh deploy@your-server.com 'docker compose exec web printenv'

# Check specific variable
ssh deploy@your-server.com 'docker compose exec web printenv DATABASE_URL'
```

### Interactive Shell
```bash
# Shell into web container
ssh deploy@your-server.com 'docker compose exec web bash'

# Shell into database
ssh deploy@your-server.com 'docker compose exec db bash'

# Python REPL in web container
ssh deploy@your-server.com 'docker compose exec web python'
```

### Network Debugging
```bash
# Test internal connectivity
ssh deploy@your-server.com 'docker compose exec web curl http://db:5432'

# Check DNS resolution
ssh deploy@your-server.com 'docker compose exec web nslookup db'

# Network inspection
ssh deploy@your-server.com 'docker network inspect app_default'
```

## 🚨 Emergency Response

### Quick Rollback
```bash
# Rollback to previous commit
ssh deploy@your-server.com 'cd ~/app && git reset --hard HEAD~1 && docker compose up -d --build'
```

### Force Restart
```bash
# Nuclear option - full restart
ssh deploy@your-server.com 'cd ~/app && docker compose down && docker compose -f docker-compose.prod.yml up -d'
```

### View All Errors
```bash
# Last 500 error lines
ssh deploy@your-server.com 'docker compose logs --tail=500 | grep -i error'

# Today's errors
ssh deploy@your-server.com 'docker compose logs --since $(date +%Y-%m-%d) | grep -i error'
```

## 📈 Prometheus Queries

### Access Prometheus
```
http://your-server.com:9090
```

### Useful Queries
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])

# Average response time
rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])

# CPU usage
100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# Memory usage
(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100
```

## 📱 Monitoring Dashboards

### Grafana
```
http://your-server.com:3000
Default: admin/admin
```

### pgAdmin
```
https://api.yourdomain.com/pgadmin/
```

### Application Logs
```
https://api.yourdomain.com/docs (API Documentation)
```

## 💾 Backup Schedule

### Automated Backups
```bash
# View backup cron job
ssh deploy@your-server.com 'crontab -l | grep backup'

# Manual trigger
ssh deploy@your-server.com 'cd ~/app && ./scripts/backup.sh'
```

### Backup Verification
```bash
# Test latest backup
ssh deploy@your-server.com 'cd ~/app && pg_restore --list backups/$(ls -t backups/ | head -1)'
```

## 🔧 Configuration Updates

### Update Environment Variables
```bash
# Edit .env file
ssh deploy@your-server.com 'nano ~/app/.env'

# Restart to apply changes
ssh deploy@your-server.com 'docker compose restart web'
```

### Update Caddy Configuration
```bash
# Edit Caddyfile
ssh deploy@your-server.com 'nano ~/app/caddy/Caddyfile'

# Reload Caddy
ssh deploy@your-server.com 'docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile'
```

---

## 📞 Quick Contacts

- **Emergency**: [Your emergency number]
- **DevOps**: [devops@yourdomain.com]
- **Status Page**: [https://status.yourdomain.com]

## 🔗 Quick Links

- [Full Deployment Guide](DEPLOYMENT.md)
- [Production Checklist](PRODUCTION_CHECKLIST.md)
- [Development Guide](DEVELOPMENT.md)
- [API Documentation](https://api.yourdomain.com/docs)
