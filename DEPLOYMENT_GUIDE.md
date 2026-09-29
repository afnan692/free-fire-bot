# FreeFire Level Up Bot - Oracle Cloud Deployment Guide

## 🚀 Complete Deployment Instructions

### Prerequisites
- Oracle Cloud Free Tier account
- Basic knowledge of SSH and Linux commands
- Your bot files (Main.py, dashboard_server.py, templates/)

---

## Step 1: Create Oracle Cloud Account

1. Go to [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
2. Sign up with your email (credit card required but won't be charged)
3. Verify your email and phone number
4. Wait for account activation (usually 1-2 hours)

---

## Step 2: Create Virtual Machine

1. Login to Oracle Cloud Console
2. Go to **Compute** → **Instances**
3. Click **Create Instance**
4. Configure:
   - **Name**: toxic-bot
   - **Compartment**: (your compartment)
   - **Shape**: Always Free Eligible → **VM.Standard.E2.1.Micro** (or **VM.Standard.A1.Flex** for better performance)
   - **Operating System**: Ubuntu 22.04 Minimal
   - **SSH Keys**: Upload your public SSH key or create new
5. Click **Create**

---

## Step 3: Connect to Your VM

### Windows (PowerShell):
```bash
ssh -i path/to/your/key.pem ubuntu@YOUR_PUBLIC_IP
```

### Linux/Mac:
```bash
ssh -i path/to/your/key.pem ubuntu@YOUR_PUBLIC_IP
```

---

## Step 4: Run Deployment Script

1. Upload the deployment script to your VM:
```bash
# From your local machine
scp -i path/to/your/key.pem deploy_oracle.sh ubuntu@YOUR_PUBLIC_IP:/home/ubuntu/
```

2. SSH into your VM and run the script:
```bash
ssh -i path/to/your/key.pem ubuntu@YOUR_PUBLIC_IP
sudo bash deploy_oracle.sh
```

3. The script will automatically:
   - Update system packages
   - Install Python and dependencies
   - Create bot directory at `/opt/toxic-bot`
   - Setup virtual environment
   - Configure systemd service
   - Setup firewall
   - Configure Nginx reverse proxy
   - Setup monitoring

---

## Step 5: Upload Bot Files

1. From your local machine, upload all bot files:
```bash
scp -i path/to/your/key.pem Main.py ubuntu@YOUR_PUBLIC_IP:/opt/toxic-bot/
scp -i path/to/your/key.pem dashboard_server.py ubuntu@YOUR_PUBLIC_IP:/opt/toxic-bot/
scp -i path/to/your/key.pem message_ids.py ubuntu@YOUR_PUBLIC_IP:/opt/toxic-bot/
scp -i path/to/your/key.pem thunderFF_pb2.py ubuntu@YOUR_PUBLIC_IP:/opt/toxic-bot/
scp -i path/to/your/key.pem StartMatch_pb2.py ubuntu@YOUR_PUBLIC_IP:/opt/toxic-bot/
scp -r -i path/to/your/key.pem templates ubuntu@YOUR_PUBLIC_IP:/opt/toxic-bot/
```

2. Create accounts.json file:
```bash
# On the VM
nano /opt/toxic-bot/accounts.json
```

Add your accounts:
```json
[
  {
    "uid": "YOUR_UID",
    "password": "YOUR_PASSWORD"
  }
]
```

---

## Step 6: Start the Bot

```bash
# Start the service
sudo systemctl start toxic-bot

# Enable auto-start on boot
sudo systemctl enable toxic-bot

# Check status
sudo systemctl status toxic-bot

# View logs
sudo journalctl -u toxic-bot -f
```

---

## Step 7: Access Your Dashboard

Your bot dashboard will be accessible at:

- **Direct access**: `http://YOUR_PUBLIC_IP:20331`
- **Via Nginx**: `http://YOUR_PUBLIC_IP`

### Default Admin Access Key: `TOXIC2`

⚠️ **IMPORTANT**: Change the default admin key after first login!

---

## Access Key Management

### Login
1. Open your dashboard URL
2. Enter access key: `TOXIC2`
3. Click "Unlock Command Center"

### Create New Access Keys (Admin Only)
1. Click "Admin Panel" button (top right)
2. Enter user name
3. Check "Admin privileges" if needed
4. Click "Create Key"
5. Copy the generated key and share with user

### Delete Access Keys (Admin Only)
1. Click "Admin Panel"
2. Find the key you want to delete
3. Click "Delete" button
4. Confirm deletion

---

## Managing Your Bot

### Add Account via Dashboard
1. Click "Add Account" button
2. Enter UID and Password OR Token
3. Click "Add"

### Pause/Resume Accounts
- Click pause button next to each account
- Or use "Pause All" to pause all accounts

### View Logs
- Logs are shown in the Console panel
- Auto-refreshes every 2 seconds

### Monitor Performance
- Check stats at the top of the dashboard
- Active accounts, matches, EXP gained, uptime

---

## Troubleshooting

### Bot not starting
```bash
# Check service status
sudo systemctl status toxic-bot

# View error logs
sudo journalctl -u toxic-bot -n 50

# Restart service
sudo systemctl restart toxic-bot
```

### Port 20331 not accessible
```bash
# Check firewall
sudo ufw status

# Allow port
sudo ufw allow 20331/tcp

# Check if port is listening
sudo netstat -tlnp | grep 20331
```

### Python dependencies missing
```bash
cd /opt/toxic-bot
source venv/bin/activate
pip install -r requirements.txt
```

### Files not uploading correctly
```bash
# Check file permissions
sudo chown -R root:root /opt/toxic-bot
sudo chmod -R 755 /opt/toxic-bot
```

---

## Security Best Practices

1. **Change default admin key** immediately after first login
2. **Use strong SSH keys** - never use password authentication
3. **Keep system updated** - run `sudo apt update && sudo apt upgrade` regularly
4. **Monitor logs** - check for suspicious activity
5. **Use firewall** - only open necessary ports
6. **Backup data** - regularly backup accounts.json and devices.json
7. **Limit admin keys** - only give admin access to trusted users

---

## Performance Optimization

### For better performance with many accounts:
1. Use **VM.Standard.A1.Flex** instead of E2.Micro (more CPU/RAM)
2. Increase `MAX_CONCURRENT_MATCHES` in Main.py
3. Monitor CPU and memory usage
4. Consider using multiple VMs for very large scale

---

## Maintenance

### Weekly tasks:
- Check system updates: `sudo apt update && sudo apt upgrade`
- Review logs for errors
- Backup configuration files

### Monthly tasks:
- Review and clean up old logs
- Check disk space usage
- Update Python packages: `pip install --upgrade <package>`

---

## Support

If you encounter issues:
1. Check the logs: `sudo journalctl -u toxic-bot -f`
2. Review this guide
3. Check Oracle Cloud documentation
4. Verify all files are uploaded correctly

---

## File Structure After Deployment

```
/opt/toxic-bot/
├── Main.py                    # Main bot script
├── dashboard_server.py        # Web dashboard
├── message_ids.py            # Message IDs
├── thunderFF_pb2.py          # Protobuf definitions
├── StartMatch_pb2.py         # Match protobuf
├── templates/
│   └── index.html           # Dashboard UI
├── accounts.json             # Account credentials
├── devices.json             # Device profiles (auto-generated)
├── token_cache.json          # Token cache (auto-generated)
├── access_keys.json          # Access keys (auto-generated)
├── venv/                     # Python virtual environment
├── deploy_oracle.sh         # Deployment script
└── monitor.sh               # Monitoring script
```

---

## Cost Summary

Oracle Cloud Free Tier includes:
- **2 ARM-based VMs** (24GB RAM, 4 OCPU each) - FREE
- **200GB storage** - FREE
- **10TB/month data transfer** - FREE
- **Public IP** - FREE

**Total cost: $0/month** (as long as you stay within free tier limits)

---

## Scaling Options

If you need more resources:
1. **Upgrade shape**: Use paid shapes for more CPU/RAM
2. **Multiple VMs**: Run multiple instances with load balancing
3. **Object Storage**: Use Oracle Object Storage for backups
4. **Database**: Use Oracle Autonomous Database for data persistence

---

## Success Checklist

- [ ] Oracle Cloud account created
- [ ] VM instance created and running
- [ ] SSH access working
- [ ] Deployment script executed successfully
- [ ] Bot files uploaded
- [ ] accounts.json created
- [ ] Service started and running
- [ ] Dashboard accessible via browser
- [ ] Default admin key changed
- [ ] Test account added and working
- [ ] Monitoring configured

---

**Congratulations! Your FreeFire Level Up Bot is now running 24/7 on Oracle Cloud! 🎉**
