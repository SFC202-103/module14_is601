#!/bin/bash

# Production Server Security Hardening Script
# This script sets up SSH hardening, firewall rules, and fail2ban

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Server Security Hardening Script    ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# ============================================
# 1. SSH HARDENING
# ============================================
echo -e "${GREEN}[1/5] Hardening SSH Configuration...${NC}"

# Backup original SSH config
if [ ! -f /etc/ssh/sshd_config.bak ]; then
    cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
    echo "✅ Backed up original SSH config"
fi

# SSH hardening settings
cat > /etc/ssh/sshd_config.d/99-hardening.conf << 'EOF'
# SSH Security Hardening Configuration

# Disable root login
PermitRootLogin no

# Use SSH key authentication only
PubkeyAuthentication yes
PasswordAuthentication no
PermitEmptyPasswords no
ChallengeResponseAuthentication no

# Disable X11 forwarding
X11Forwarding no

# Limit authentication attempts
MaxAuthTries 3
MaxSessions 2

# Set login grace time
LoginGraceTime 30

# Allow only specific users (uncomment and modify)
# AllowUsers deploy your_username

# Use strong ciphers and MACs
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group16-sha512

# Disable unused features
AllowAgentForwarding no
AllowTcpForwarding no
PermitTunnel no

# Set client alive interval (5 minutes)
ClientAliveInterval 300
ClientAliveCountMax 2

# Log verbosely
LogLevel VERBOSE

# Enable strict mode
StrictModes yes
EOF

# Test SSH configuration
sshd -t && echo "✅ SSH configuration valid" || echo "❌ SSH configuration has errors"

# Restart SSH service
systemctl restart sshd
echo "✅ SSH service restarted with hardened configuration"

# ============================================
# 2. FIREWALL SETUP (UFW)
# ============================================
echo -e "${GREEN}[2/5] Configuring Firewall (UFW)...${NC}"

# Install UFW if not present
if ! command -v ufw &> /dev/null; then
    apt-get update && apt-get install -y ufw
fi

# Reset UFW to default
ufw --force reset

# Set default policies
ufw default deny incoming
ufw default allow outgoing
echo "✅ Set default firewall policies"

# Allow SSH (IMPORTANT - don't lock yourself out!)
SSH_PORT=$(grep -E "^Port " /etc/ssh/sshd_config | awk '{print $2}')
SSH_PORT=${SSH_PORT:-22}
ufw allow ${SSH_PORT}/tcp comment 'SSH'
echo "✅ Allowed SSH on port ${SSH_PORT}"

# Allow HTTP and HTTPS
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
echo "✅ Allowed HTTP/HTTPS"

# Rate limit SSH connections
ufw limit ${SSH_PORT}/tcp
echo "✅ Rate limiting enabled for SSH"

# Enable UFW
ufw --force enable
echo "✅ Firewall enabled"

# Show status
ufw status verbose

# ============================================
# 3. FAIL2BAN INSTALLATION
# ============================================
echo -e "${GREEN}[3/5] Installing and Configuring Fail2Ban...${NC}"

# Install fail2ban
apt-get update && apt-get install -y fail2ban

# Create local configuration
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
# Ban hosts for 1 hour
bantime = 3600

# A host is banned after 5 failed attempts
maxretry = 5

# Check for failed attempts over 10 minutes
findtime = 600

# Email notifications (configure SMTP)
destemail = admin@yourdomain.com
sender = fail2ban@yourdomain.com
action = %(action_mwl)s

# Backend
backend = systemd

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
maxretry = 3
bantime = 86400

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
bantime = 86400

[docker-auth]
enabled = true
filter = docker-auth
port = all
logpath = /var/log/docker.log
maxretry = 3
EOF

# Create custom docker filter
cat > /etc/fail2ban/filter.d/docker-auth.conf << 'EOF'
[Definition]
failregex = ^.*Failed password for .* from <HOST>.*$
            ^.*authentication failure.*rhost=<HOST>.*$
ignoreregex =
EOF

# Enable and start fail2ban
systemctl enable fail2ban
systemctl restart fail2ban
echo "✅ Fail2Ban installed and configured"

# Show fail2ban status
fail2ban-client status

# ============================================
# 4. SYSTEM HARDENING
# ============================================
echo -e "${GREEN}[4/5] Applying System Hardening...${NC}"

# Update system
apt-get update && apt-get upgrade -y
echo "✅ System updated"

# Install security updates automatically
apt-get install -y unattended-upgrades apt-listchanges
dpkg-reconfigure -plow unattended-upgrades
echo "✅ Automatic security updates enabled"

# Disable unused services
systemctl disable bluetooth.service 2>/dev/null || true
systemctl disable cups.service 2>/dev/null || true
echo "✅ Disabled unused services"

# Set secure kernel parameters
cat > /etc/sysctl.d/99-security.conf << 'EOF'
# IP Forwarding (disable if not needed)
net.ipv4.ip_forward = 0
net.ipv6.conf.all.forwarding = 0

# Prevent SYN flood attacks
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2

# Disable ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0

# Disable source packet routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# Enable IP spoofing protection
net.ipv4.conf.all.rp_filter = 1

# Log suspicious packets
net.ipv4.conf.all.log_martians = 1

# Ignore ICMP pings
net.ipv4.icmp_echo_ignore_all = 0
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Ignore bogus ICMP error responses
net.ipv4.icmp_ignore_bogus_error_responses = 1
EOF

sysctl -p /etc/sysctl.d/99-security.conf
echo "✅ Kernel security parameters applied"

# Set proper file permissions
chmod 600 /etc/ssh/sshd_config
chmod 644 /etc/passwd
chmod 600 /etc/shadow
chmod 644 /etc/group
echo "✅ File permissions secured"

# ============================================
# 5. MONITORING & LOGGING
# ============================================
echo -e "${GREEN}[5/5] Setting up Monitoring & Logging...${NC}"

# Install monitoring tools
apt-get install -y auditd aide logwatch

# Enable auditd
systemctl enable auditd
systemctl start auditd
echo "✅ Audit daemon enabled"

# Configure aide
aideinit
echo "✅ File integrity monitoring initialized"

# Set up logwatch for daily reports
cat > /etc/cron.daily/00logwatch << 'EOF'
#!/bin/bash
/usr/sbin/logwatch --output mail --mailto admin@yourdomain.com --detail high
EOF
chmod +x /etc/cron.daily/00logwatch
echo "✅ Daily log monitoring configured"

# ============================================
# FINAL SUMMARY
# ============================================
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}   Security Hardening Complete! ✅      ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Summary of changes:${NC}"
echo "  ✅ SSH hardened (key auth only, no root login)"
echo "  ✅ Firewall configured (ports 22, 80, 443)"
echo "  ✅ Fail2Ban installed (SSH, Nginx, Docker)"
echo "  ✅ System hardened (kernel params, updates)"
echo "  ✅ Monitoring enabled (auditd, aide, logwatch)"
echo ""
echo -e "${YELLOW}Important next steps:${NC}"
echo "  1. Test SSH access from another terminal BEFORE closing this one"
echo "  2. Configure AllowUsers in /etc/ssh/sshd_config.d/99-hardening.conf"
echo "  3. Update fail2ban email in /etc/fail2ban/jail.local"
echo "  4. Set up log monitoring email in /etc/cron.daily/00logwatch"
echo "  5. Review firewall rules: ufw status verbose"
echo "  6. Check fail2ban status: fail2ban-client status"
echo ""
echo -e "${RED}⚠️  CRITICAL: Test SSH access before closing this session!${NC}"
echo ""
