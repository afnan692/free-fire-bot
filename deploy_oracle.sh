#!/bin/bash

# ============================================
# ORACLE CLOUD DEPLOYMENT SCRIPT
# FreeFire Level Up Bot - Oracle Cloud Setup
# ============================================

set -e

echo "=========================================="
echo "ORACLE CLOUD DEPLOYMENT SCRIPT"
echo "FreeFire Level Up Bot Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Update system
echo "Updating system packages..."
apt update && apt upgrade -y
print_success "System updated"

# Install Python and dependencies
echo "Installing Python and dependencies..."
apt install -y python3 python3-pip python3-venv git nginx ufw fail2ban
print_success "Python and dependencies installed"

# Create bot directory
echo "Creating bot directory..."
mkdir -p /opt/toxic-bot
cd /opt/toxic-bot
print_success "Bot directory created"

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
print_success "Virtual environment created"

# Install Python packages
echo "Installing Python packages..."
pip install --upgrade pip
pip install aiohttp httpx google-play-scraper pycryptodome protobuf
print_success "Python packages installed"

# Create systemd service file
echo "Creating systemd service..."
cat > /etc/systemd/system/toxic-bot.service << 'EOF'
[Unit]
Description=FreeFire Level Up Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/toxic-bot
Environment="PATH=/opt/toxic-bot/venv/bin"
ExecStart=/opt/toxic-bot/venv/bin/python3 Main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

print_success "Systemd service created"

# Configure firewall
echo "Configuring firewall..."
ufw allow 22/tcp
ufw allow 20331/tcp
ufw --force enable
print_success "Firewall configured"

# Configure Nginx reverse proxy (optional)
echo "Configuring Nginx reverse proxy..."
cat > /etc/nginx/sites-available/toxic-bot << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:20331;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/toxic-bot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
print_success "Nginx configured"

# Setup log rotation
echo "Setting up log rotation..."
cat > /etc/logrotate.d/toxic-bot << 'EOF'
/opt/toxic-bot/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
EOF

print_success "Log rotation configured"

# Create monitoring script
echo "Creating monitoring script..."
cat > /opt/toxic-bot/monitor.sh << 'EOF'
#!/bin/bash
# Monitor script to check if bot is running
if ! systemctl is-active --quiet toxic-bot; then
    echo "Bot is not running, attempting to restart..."
    systemctl start toxic-bot
    echo "Bot restarted at $(date)" >> /opt/toxic-bot/restart.log
fi
EOF

chmod +x /opt/toxic-bot/monitor.sh

# Add cron job for monitoring
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/toxic-bot/monitor.sh") | crontab -
print_success "Monitoring configured"

# Print completion message
echo ""
echo "=========================================="
print_success "DEPLOYMENT COMPLETED!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Upload your bot files to /opt/toxic-bot"
echo "2. Make sure Main.py and dashboard_server.py are present"
echo "3. Create accounts.json with your account credentials"
echo "4. Start the service: systemctl start toxic-bot"
echo "5. Enable auto-start: systemctl enable toxic-bot"
echo "6. Check status: systemctl status toxic-bot"
echo ""
echo "Your bot will be accessible at:"
echo "  - Direct: http://YOUR_PUBLIC_IP:20331"
echo "  - Via Nginx: http://YOUR_PUBLIC_IP"
echo ""
echo "Default admin access key: TOXIC2"
echo ""
print_warning "IMPORTANT: Change the default admin key after first login!"
echo ""
