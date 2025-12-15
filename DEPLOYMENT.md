# Production Deployment Guide

This guide covers deploying the FastAPI Calculator application to a production environment with enterprise-grade infrastructure.

## 🏗️ Production Infrastructure Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Server                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  🔐 Multi-layer Security                             │  │
│  │  ├── SSH Key Authentication                          │  │
│  │  ├── UFW Firewall (ports 22, 80, 443, 5432)         │  │
│  │  ├── Fail2Ban (brute force protection)              │  │
│  │  └── Security Headers & Rate Limiting               │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  🐳 Docker Platform                                  │  │
│  │  ├── Docker Engine 24.0+                            │  │
│  │  ├── Docker Compose v2                              │  │
│  │  └── Container Orchestration                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  🌐 Caddy Reverse Proxy                             │  │
│  │  ├── Automatic HTTPS (Let's Encrypt)                │  │
│  │  ├── HTTP/2 & HTTP/3 Support                        │  │
│  │  ├── Auto SSL Certificate Renewal                   │  │
│  │  └── Load Balancing & Caching                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  🗄️ PostgreSQL Database                            │  │
│  │  ├── PostgreSQL 17                                   │  │
│  │  ├── pgAdmin 4 (Web Interface)                      │  │
│  │  ├── Persistent Volume Storage                      │  │
│  │  └── Automated Backups                              │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  🚀 FastAPI Application                             │  │
│  │  ├── FastAPI Backend (Python 3.12)                  │  │
│  │  ├── Static Files (HTML/CSS/JS)                     │  │
│  │  ├── Redis Cache (Optional)                         │  │
│  │  └── Health Checks & Monitoring                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  🔄 CI/CD Pipeline                                   │  │
│  │  ├── GitHub Actions                                  │  │
│  │  ├── Automated Testing                               │  │
│  │  ├── Docker Image Building                           │  │
│  │  └── Zero-Downtime Deployment                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Prerequisites

- **Server**: Ubuntu 22.04 LTS or later (2GB RAM minimum, 4GB recommended)
- **Domain**: Registered domain name pointing to your server
- **Access**: SSH access with sudo privileges
- **GitHub**: Repository with code and secrets configured

## 🔐 Step 1: Multi-layer Security Setup

### 1.1 SSH Key Authentication

```bash
# On your local machine, generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy public key to server
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@your-server-ip

# Disable password authentication on server
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart sshd
```

### 1.2 UFW Firewall Configuration

```bash
# Install and configure UFW
sudo apt update
sudo apt install ufw -y

# Set default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow essential services
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Enable firewall
sudo ufw enable
sudo ufw status verbose
```

### 1.3 Fail2Ban Installation

```bash
# Install Fail2Ban
sudo apt install fail2ban -y

# Create custom configuration
sudo nano /etc/fail2ban/jail.local
```

Add the following configuration:

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
```

```bash
# Start Fail2Ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
sudo fail2ban-client status
```

## 🐳 Step 2: Docker Platform Installation

### 2.1 Install Docker Engine

```bash
# Remove old versions
sudo apt remove docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt update
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

### 2.2 Docker Security Configuration

```bash
# Enable Docker security features
sudo nano /etc/docker/daemon.json
```

Add:

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true
}
```

```bash
sudo systemctl restart docker
```

## 🌐 Step 3: Caddy Reverse Proxy Setup

### 3.1 Create Caddyfile

```bash
mkdir -p ~/app/caddy
cd ~/app
nano caddy/Caddyfile
```

Add the following configuration:

```caddyfile
# Caddyfile for FastAPI Calculator

# Main application
api.yourdomain.com {
    reverse_proxy fastapi-app:8000 {
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }

    # Security headers
    header {
        # Enable HSTS
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        
        # Prevent clickjacking
        X-Frame-Options "SAMEORIGIN"
        
        # XSS Protection
        X-Content-Type-Options "nosniff"
        X-XSS-Protection "1; mode=block"
        
        # Referrer Policy
        Referrer-Policy "strict-origin-when-cross-origin"
        
        # CSP
        Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
    }

    # Rate limiting
    rate_limit {
        zone dynamic {
            key {remote_host}
            events 100
            window 1m
        }
    }

    # Logging
    log {
        output file /var/log/caddy/access.log
        format json
    }
}

# pgAdmin interface (optional)
pgadmin.yourdomain.com {
    reverse_proxy pgadmin:80
    
    # Basic auth for extra security
    basicauth {
        admin $2a$14$...your_bcrypt_hash_here
    }
}
```

### 3.2 Add Caddy to Docker Compose

Update your `docker-compose.yml`:

```yaml
services:
  caddy:
    image: caddy:2-alpine
    container_name: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./caddy/Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
      - caddy_config:/config
      - ./logs/caddy:/var/log/caddy
    networks:
      - app-network
    depends_on:
      - web

  web:
    build: .
    container_name: fastapi-app
    restart: unless-stopped
    expose:
      - "8000"
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@db:5432/fastapi_db
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      JWT_REFRESH_SECRET_KEY: ${JWT_REFRESH_SECRET_KEY}
      REDIS_URL: redis://redis:6379/0
    volumes:
      - ./logs/app:/app/logs
    networks:
      - app-network
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:17-alpine
    container_name: postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: fastapi_db
    expose:
      - "5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - app-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: pgadmin
    restart: unless-stopped
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_EMAIL}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_PASSWORD}
    expose:
      - "80"
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    networks:
      - app-network
    depends_on:
      - db

  redis:
    image: redis:7-alpine
    container_name: redis
    restart: unless-stopped
    expose:
      - "6379"
    volumes:
      - redis_data:/data
    networks:
      - app-network
    command: redis-server --appendonly yes

volumes:
  postgres_data:
  pgadmin_data:
  redis_data:
  caddy_data:
  caddy_config:

networks:
  app-network:
    driver: bridge
```

## 🔄 Step 4: CI/CD Pipeline with GitHub Actions

### 4.1 Create GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: fastapi_test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/fastapi_test_db
          JWT_SECRET_KEY: test-secret-key-min-32-characters-long
          JWT_REFRESH_SECRET_KEY: test-refresh-secret-key-min-32-chars
        run: |
          pytest tests/ -v --cov=app --cov-report=xml
          
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=sha
            type=raw,value=latest,enable={{is_default_branch}}
            
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:buildcache,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    
    steps:
      - name: Deploy to production server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.PROD_SERVER_HOST }}
          username: ${{ secrets.PROD_SERVER_USER }}
          key: ${{ secrets.PROD_SERVER_SSH_KEY }}
          script: |
            cd ~/app
            
            # Pull latest images
            docker compose pull
            
            # Backup database
            docker compose exec -T db pg_dump -U postgres fastapi_db > backups/backup_$(date +%Y%m%d_%H%M%S).sql
            
            # Deploy with zero downtime
            docker compose up -d --no-deps --build web
            
            # Clean up old images
            docker image prune -af
            
            # Verify deployment
            sleep 10
            curl -f http://localhost:8000/health || exit 1
```

### 4.2 Configure GitHub Secrets

In your GitHub repository, go to Settings → Secrets and variables → Actions, and add:

```
PROD_SERVER_HOST        # Your server IP or domain
PROD_SERVER_USER        # SSH username
PROD_SERVER_SSH_KEY     # Private SSH key content
DB_PASSWORD             # PostgreSQL password
JWT_SECRET_KEY          # Production JWT secret
JWT_REFRESH_SECRET_KEY  # Production refresh secret
PGADMIN_EMAIL          # pgAdmin email
PGADMIN_PASSWORD       # pgAdmin password
```

## 🚀 Step 5: Deploy Application

### 5.1 Prepare Production Environment

```bash
# Clone repository on server
cd ~
git clone https://github.com/yourusername/yourrepo.git app
cd app

# Create production .env file
nano .env.production
```

Add production environment variables:

```bash
# Database
DB_PASSWORD=your_secure_postgres_password

# JWT
JWT_SECRET_KEY=your_production_jwt_secret_min_32_characters
JWT_REFRESH_SECRET_KEY=your_production_refresh_secret_min_32_chars

# pgAdmin
PGADMIN_EMAIL=admin@yourdomain.com
PGADMIN_PASSWORD=secure_pgadmin_password

# Application
ENVIRONMENT=production
DEBUG=False
```

### 5.2 Initial Deployment

```bash
# Create necessary directories
mkdir -p logs/app logs/caddy backups

# Start services
docker compose up -d

# Check status
docker compose ps
docker compose logs -f

# Initialize database
docker compose exec web python -m app.database_init
```

### 5.3 Verify Deployment

```bash
# Check application health
curl https://api.yourdomain.com/health

# Check SSL certificate
curl -vI https://api.yourdomain.com

# View logs
docker compose logs -f web
```

## 📊 Step 6: Monitoring & Maintenance

### 6.1 Automated Database Backups

Create backup script `~/app/scripts/backup-db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/$USER/app/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Create backup
docker compose exec -T db pg_dump -U postgres fastapi_db > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Delete backups older than 7 days
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}.gz"
```

Add to crontab:

```bash
chmod +x ~/app/scripts/backup-db.sh
crontab -e
# Add: 0 2 * * * /home/user/app/scripts/backup-db.sh >> /home/user/app/logs/backup.log 2>&1
```

### 6.2 Log Rotation

```bash
sudo nano /etc/logrotate.d/fastapi-app
```

Add:

```
/home/user/app/logs/app/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 user user
    sharedscripts
}
```

### 6.3 Health Check Monitoring

Create `~/app/scripts/health-check.sh`:

```bash
#!/bin/bash
HEALTH_URL="https://api.yourdomain.com/health"
ALERT_EMAIL="your-email@example.com"

if ! curl -f -s "$HEALTH_URL" > /dev/null; then
    echo "Application health check failed" | mail -s "ALERT: App Down" "$ALERT_EMAIL"
    docker compose restart web
fi
```

## 🔒 Security Best Practices

### Environment Variables
- ✅ Never commit `.env` files to version control
- ✅ Use strong, unique passwords (32+ characters)
- ✅ Rotate JWT secrets periodically
- ✅ Use GitHub Secrets for CI/CD credentials

### SSL/TLS
- ✅ Caddy automatically manages SSL certificates
- ✅ Force HTTPS for all connections
- ✅ Enable HSTS headers
- ✅ Use HTTP/2 and HTTP/3

### Database Security
- ✅ Use strong PostgreSQL passwords
- ✅ Don't expose PostgreSQL port publicly
- ✅ Regular automated backups
- ✅ Encrypt backups

### Application Security
- ✅ Run containers as non-root user
- ✅ Use security headers
- ✅ Enable rate limiting
- ✅ Implement proper CORS policies
- ✅ Regular dependency updates

## 📈 Performance Optimization

### Caching
- Redis for session management
- HTTP caching with Caddy
- Database query optimization

### Scaling
- Horizontal scaling with multiple app instances
- Database connection pooling
- Load balancing with Caddy

## 🆘 Troubleshooting

### Application won't start
```bash
# Check logs
docker compose logs web

# Verify environment variables
docker compose exec web env | grep DATABASE_URL

# Test database connection
docker compose exec db psql -U postgres -c "\l"
```

### SSL Certificate Issues
```bash
# Check Caddy logs
docker compose logs caddy

# Verify DNS records
dig api.yourdomain.com

# Test SSL
curl -vI https://api.yourdomain.com
```

### Database Connection Issues
```bash
# Check PostgreSQL status
docker compose exec db pg_isready

# View PostgreSQL logs
docker compose logs db

# Test connection from app
docker compose exec web python -c "from app.database import engine; engine.connect()"
```

## 📚 Additional Resources

- [FastAPI Production Deployment](https://fastapi.tiangolo.com/deployment/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [Caddy Documentation](https://caddyserver.com/docs/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## 🎯 Deployment Checklist

- [ ] Server secured (SSH keys, firewall, Fail2Ban)
- [ ] Docker and Docker Compose installed
- [ ] Domain DNS configured
- [ ] Caddyfile created and configured
- [ ] Production `.env` file created
- [ ] GitHub Secrets configured
- [ ] GitHub Actions workflow added
- [ ] Application deployed and tested
- [ ] SSL certificate issued (automatic via Caddy)
- [ ] Database backups configured
- [ ] Monitoring and health checks set up
- [ ] Log rotation configured
- [ ] Security headers verified
- [ ] Rate limiting tested
- [ ] Application accessible via HTTPS

---

**Your application is now production-ready with enterprise-grade infrastructure!** 🚀
