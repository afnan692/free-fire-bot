# 🚀 Quick Start Guide - FreeFire Level Up Bot

## What's Been Added

✅ **Access Key Authentication System**
- Default admin key: `TOXIC2`
- Secure API authentication
- Multiple user support

✅ **Admin Panel**
- Create new access keys
- Manage existing keys
- Admin privileges control

✅ **Oracle Cloud Deployment**
- Automated deployment script
- 24/7 hosting setup
- Nginx reverse proxy
- Systemd service management
- Auto-restart monitoring

✅ **Updated Dashboard**
- Login system with access key validation
- Admin panel for key management
- Logout functionality
- Secure API calls

---

## Local Testing (Before Deployment)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Bot
```bash
python Main.py
```

### 3. Access Dashboard
- Open browser: `http://localhost:20331`
- Login with: `TOXIC2`

### 4. Test Features
- Add accounts via dashboard
- Create new access keys (Admin Panel)
- Test pause/resume functionality

---

## Oracle Cloud Deployment (5 Steps)

### Step 1: Create Oracle Cloud Account
1. Go to https://www.oracle.com/cloud/free/
2. Sign up (credit card required but not charged)
3. Wait for activation (1-2 hours)

### Step 2: Create VM
1. Go to Compute → Instances → Create Instance
2. Name: `toxic-bot`
3. Shape: Always Free (VM.Standard.E2.1.Micro or VM.Standard.A1.Flex)
4. OS: Ubuntu 22.04 Minimal
5. Add your SSH key
6. Click Create

### Step 3: Deploy
```bash
# Upload deployment script
scp -i your_key.pem deploy_oracle.sh ubuntu@YOUR_PUBLIC_IP:/home/ubuntu/

# SSH into VM
ssh -i your_key.pem ubuntu@YOUR_PUBLIC_IP

# Run deployment script
sudo bash deploy_oracle.sh
```

### Step 4: Upload Bot Files
```bash
# From your local machine
scp -i your_key.pem Main.py ubuntu@YOUR_PUBLIC_IP:/opt/toxic-bot/
scp -i your_key.pem dashboard_server.py ubuntu@YOUR_PUBLIC_IP:/opt/toxic-bot/
scp -i your_key.pem message_ids.py ubuntu@YOUR_PUBLIC_IP:/opt/toxic-bot/
scp -i your_key.pem thunderFF_pb2.py ubuntu@YOUR_PUBLIC_IP:/opt/toxic-bot/
scp -i your_key.pem StartMatch_pb2.py ubuntu@YOUR_PUBLIC_IP:/opt/toxic-bot/
scp -r -i your_key.pem templates ubuntu@YOUR_PUBLIC_IP:/opt/toxic-bot/
```

### Step 5: Start Bot
```bash
# On the VM
sudo systemctl start toxic-bot
sudo systemctl enable toxic-bot
sudo systemctl status toxic-bot
```

---

## Access Your Dashboard

**URL**: `http://YOUR_PUBLIC_IP` or `http://YOUR_PUBLIC_IP:20331`

**Default Admin Key**: `TOXIC2`

⚠️ **Change the default key after first login!**

---

## Admin Panel Usage

### Create New Access Key
1. Login with admin key
2. Click "Admin Panel" button
3. Enter user name
4. Check "Admin privileges" if needed
5. Click "Create Key"
6. Share the generated key with user

### Delete Access Key
1. Open Admin Panel
2. Find the key
3. Click "Delete"
4. Confirm

---

## File Summary

### New Files Created:
- `deploy_oracle.sh` - Oracle Cloud deployment script
- `DEPLOYMENT_GUIDE.md` - Complete deployment documentation
- `QUICK_START.md` - This quick start guide
- `requirements.txt` - Python dependencies

### Modified Files:
- `dashboard_server.py` - Added access key system and admin API
- `templates/index.html` - Added login UI and admin panel

---

## Key Features

### 🔐 Security
- Access key authentication for all API endpoints
- Admin-only key management
- Secure session storage (localStorage)
- Default key protection (cannot be deleted)

### 👥 Multi-User Support
- Create unlimited access keys
- Admin vs regular user permissions
- User-specific access control

### 🚀 24/7 Hosting
- Oracle Cloud Free Tier integration
- Automated deployment
- Systemd service management
- Auto-restart on failure
- Nginx reverse proxy

### 🎛️ Admin Control
- Create/delete access keys
- Monitor all keys
- Grant admin privileges
- View key creation details

---

## Troubleshooting

### Deployment Issues
```bash
# Check script permissions
chmod +x deploy_oracle.sh

# Run with verbose output
bash -x deploy_oracle.sh
```

### Service Not Starting
```bash
# Check status
sudo systemctl status toxic-bot

# View logs
sudo journalctl -u toxic-bot -f

# Restart
sudo systemctl restart toxic-bot
```

### Dashboard Not Accessible
```bash
# Check firewall
sudo ufw status
sudo ufw allow 20331/tcp

# Check if service is running
sudo systemctl status toxic-bot

# Check port
sudo netstat -tlnp | grep 20331
```

---

## Next Steps

1. ✅ Test locally first
2. ✅ Create Oracle Cloud account
3. ✅ Deploy to Oracle Cloud
4. ✅ Upload bot files
5. ✅ Start the service
6. ✅ Access dashboard
7. ✅ Change default admin key
8. ✅ Create user keys
9. ✅ Add accounts
10. ✅ Monitor performance

---

## Support

For detailed instructions, see `DEPLOYMENT_GUIDE.md`

For Oracle Cloud issues, check:
- Oracle Cloud Console logs
- Instance console output
- Network security rules

---

**Ready to deploy? Start with Step 1 above! 🚀**
