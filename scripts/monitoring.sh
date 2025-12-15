#!/bin/bash

# Production Monitoring & Health Check Setup Script
# Sets up monitoring, logging, and alerting for production environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Production Monitoring Setup         ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script should be run as root or with sudo${NC}"
   exit 1
fi

# ============================================
# 1. INSTALL MONITORING TOOLS
# ============================================
echo -e "${GREEN}[1/5] Installing monitoring tools...${NC}"

apt-get update
apt-get install -y \
    prometheus \
    grafana \
    node-exporter \
    prometheus-postgres-exporter \
    htop \
    iotop \
    nethogs \
    sysstat

echo "✅ Monitoring tools installed"

# ============================================
# 2. CONFIGURE PROMETHEUS
# ============================================
echo -e "${GREEN}[2/5] Configuring Prometheus...${NC}"

# Backup original config
if [ -f /etc/prometheus/prometheus.yml ]; then
    cp /etc/prometheus/prometheus.yml /etc/prometheus/prometheus.yml.bak
fi

# Create Prometheus configuration
cat > /etc/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    monitor: 'fastapi-calculator'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          # - alertmanager:9093

rule_files:
  - "alerts.yml"

scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node Exporter (System metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']

  # PostgreSQL Exporter
  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  # FastAPI application (if you add prometheus endpoint)
  - job_name: 'fastapi'
    metrics_path: '/metrics'
    static_configs:
      - targets: ['localhost:8000']

  # Caddy metrics
  - job_name: 'caddy'
    static_configs:
      - targets: ['localhost:2019']

  # Docker metrics
  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:9323']
EOF

# Create alert rules
cat > /etc/prometheus/alerts.yml << 'EOF'
groups:
  - name: system_alerts
    interval: 30s
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for 5 minutes"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85%"

      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 15
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space"
          description: "Less than 15% disk space remaining"

      - alert: ServiceDown
        expr: up == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
          description: "{{ $labels.job }} is down for 2 minutes"

  - name: application_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 5%"

      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow response time"
          description: "95th percentile response time is above 1 second"
EOF

# Set proper permissions
chown -R prometheus:prometheus /etc/prometheus/
chmod 644 /etc/prometheus/*.yml

# Restart Prometheus
systemctl enable prometheus
systemctl restart prometheus
echo "✅ Prometheus configured and started"

# ============================================
# 3. CONFIGURE GRAFANA
# ============================================
echo -e "${GREEN}[3/5] Configuring Grafana...${NC}"

# Start Grafana
systemctl enable grafana-server
systemctl start grafana-server

# Wait for Grafana to start
sleep 5

# Configure Grafana datasource
cat > /tmp/grafana-datasource.json << 'EOF'
{
  "name": "Prometheus",
  "type": "prometheus",
  "url": "http://localhost:9090",
  "access": "proxy",
  "isDefault": true
}
EOF

# Add datasource (default credentials admin:admin)
curl -X POST -H "Content-Type: application/json" \
     -d @/tmp/grafana-datasource.json \
     http://admin:admin@localhost:3000/api/datasources 2>/dev/null || true

rm /tmp/grafana-datasource.json

echo "✅ Grafana configured"
echo "   Access at: http://localhost:3000 (admin/admin)"

# ============================================
# 4. SET UP LOG AGGREGATION
# ============================================
echo -e "${GREEN}[4/5] Setting up log aggregation...${NC}"

# Create logs directory
mkdir -p /var/log/fastapi-calculator
chown www-data:www-data /var/log/fastapi-calculator

# Set up logrotate for application logs
cat > /etc/logrotate.d/fastapi-calculator << 'EOF'
/var/log/fastapi-calculator/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload docker || true
    endscript
}
EOF

# Set up centralized logging with rsyslog
cat > /etc/rsyslog.d/30-fastapi.conf << 'EOF'
# FastAPI Calculator application logs
:programname, isequal, "fastapi" /var/log/fastapi-calculator/app.log
& stop
EOF

systemctl restart rsyslog
echo "✅ Log aggregation configured"

# ============================================
# 5. SET UP HEALTH CHECKS
# ============================================
echo -e "${GREEN}[5/5] Setting up health checks...${NC}"

# Create health check script
cat > /usr/local/bin/fastapi-health-check.sh << 'EOF'
#!/bin/bash

# FastAPI Health Check Script
# Checks application health and sends alerts if issues detected

set -e

APP_URL="http://localhost:8000/health"
ALERT_EMAIL="admin@yourdomain.com"
LOG_FILE="/var/log/fastapi-calculator/health-check.log"

check_service() {
    local service=$1
    if ! systemctl is-active --quiet "$service"; then
        echo "[$(date)] ERROR: $service is not running" >> "$LOG_FILE"
        return 1
    fi
    return 0
}

check_http() {
    local url=$1
    local timeout=5
    
    if ! curl -sf --max-time "$timeout" "$url" > /dev/null; then
        echo "[$(date)] ERROR: $url is not responding" >> "$LOG_FILE"
        return 1
    fi
    return 0
}

check_postgres() {
    if ! docker compose exec -T db pg_isready > /dev/null 2>&1; then
        echo "[$(date)] ERROR: PostgreSQL is not ready" >> "$LOG_FILE"
        return 1
    fi
    return 0
}

check_redis() {
    if ! docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo "[$(date)] ERROR: Redis is not responding" >> "$LOG_FILE"
        return 1
    fi
    return 0
}

check_disk_space() {
    local threshold=90
    local usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    
    if [ "$usage" -gt "$threshold" ]; then
        echo "[$(date)] WARNING: Disk usage at ${usage}%" >> "$LOG_FILE"
        return 1
    fi
    return 0
}

# Run checks
ERRORS=0

check_service docker || ((ERRORS++))
check_http "$APP_URL" || ((ERRORS++))
check_postgres || ((ERRORS++))
check_redis || ((ERRORS++))
check_disk_space || ((ERRORS++))

if [ "$ERRORS" -gt 0 ]; then
    echo "[$(date)] Health check failed with $ERRORS error(s)" >> "$LOG_FILE"
    
    # Send alert email if configured
    if command -v mail &> /dev/null; then
        tail -20 "$LOG_FILE" | mail -s "FastAPI Health Check Failed" "$ALERT_EMAIL"
    fi
    
    exit 1
else
    echo "[$(date)] Health check passed" >> "$LOG_FILE"
    exit 0
fi
EOF

chmod +x /usr/local/bin/fastapi-health-check.sh

# Set up cron job for health checks (every 5 minutes)
cat > /etc/cron.d/fastapi-health << 'EOF'
*/5 * * * * root /usr/local/bin/fastapi-health-check.sh
EOF

echo "✅ Health checks configured"

# ============================================
# CREATE MONITORING DASHBOARD
# ============================================
echo -e "${GREEN}Creating monitoring dashboard...${NC}"

cat > /usr/local/bin/monitor-dashboard.sh << 'EOF'
#!/bin/bash

# Simple monitoring dashboard script

clear
echo "======================================"
echo "   FastAPI Calculator - Monitor       "
echo "======================================"
echo ""

# System metrics
echo "=== SYSTEM ==="
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4"%"}')"
echo "Memory: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
echo "Disk: $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}')"
echo ""

# Docker containers
echo "=== DOCKER CONTAINERS ==="
docker compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null || echo "Docker not running"
echo ""

# Application health
echo "=== APPLICATION ==="
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "Status: ✅ Healthy"
else
    echo "Status: ❌ Unhealthy"
fi
echo ""

# Database connections
echo "=== DATABASE ==="
docker compose exec -T db psql -U postgres -c "SELECT count(*) as connections FROM pg_stat_activity;" 2>/dev/null || echo "Cannot connect"
echo ""

# Recent errors
echo "=== RECENT ERRORS ==="
tail -5 /var/log/fastapi-calculator/app.log 2>/dev/null || echo "No logs available"
echo ""

echo "======================================"
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000"
echo "======================================"
EOF

chmod +x /usr/local/bin/monitor-dashboard.sh

# ============================================
# FINAL SUMMARY
# ============================================
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}   Monitoring Setup Complete! ✅        ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Monitoring services configured:${NC}"
echo "  ✅ Prometheus (http://localhost:9090)"
echo "  ✅ Grafana (http://localhost:3000)"
echo "  ✅ Node Exporter (system metrics)"
echo "  ✅ PostgreSQL Exporter"
echo "  ✅ Health checks (every 5 minutes)"
echo "  ✅ Log rotation and aggregation"
echo ""
echo -e "${YELLOW}Commands:${NC}"
echo "  View dashboard: sudo /usr/local/bin/monitor-dashboard.sh"
echo "  Manual health check: sudo /usr/local/bin/fastapi-health-check.sh"
echo "  View logs: tail -f /var/log/fastapi-calculator/app.log"
echo "  Prometheus status: systemctl status prometheus"
echo "  Grafana status: systemctl status grafana-server"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Access Grafana at http://localhost:3000 (admin/admin)"
echo "  2. Change default Grafana password"
echo "  3. Import dashboards for FastAPI monitoring"
echo "  4. Configure alert notifications (email, Slack, etc.)"
echo "  5. Review /etc/prometheus/alerts.yml and customize"
echo ""
