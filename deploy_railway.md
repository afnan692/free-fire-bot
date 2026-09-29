# Railway.app Deployment Guide (No Payment Required)

## 🚀 Why Railway.app?

- ✅ **No credit card required** (initially)
- ✅ **$5 free credit/month**
- ✅ **24/7 uptime** (PC can be off)
- ✅ **Easy GitHub deployment**
- ✅ **Public URL automatically**
- ✅ **SSL certificate included**

---

## Step 1: Create Railway Account

1. Go to: https://railway.app/
2. Click **"Start for Free"**
3. Sign up with:
   - GitHub (recommended)
   - OR Google account
   - OR Email
4. **No credit card needed initially!**

---

## Step 2: Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `toxic-bot`
3. Make it **Private** (important!)
4. Click **"Create repository"**

---

## Step 3: Upload Your Files

### Option A: Using Git (Recommended)

```bash
# In your project folder
cd "C:\Users\fakel\Downloads\BR+CS+LW_UDP_FIXED_BY_SAYEED_KHAN"

# Initialize git
git init
git add .
git commit -m "Initial commit"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/toxic-bot.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Option B: Using GitHub Website

1. Go to your new repository
2. Click **"uploading an existing file"**
3. Drag and drop all files:
   - Main.py
   - dashboard_server.py
   - message_ids.py
   - thunderFF_pb2.py
   - StartMatch_pb2.py
   - templates/ folder
   - requirements.txt
4. Click **"Commit changes"**

---

## Step 4: Deploy to Railway

1. Go to: https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select your `toxic-bot` repository
4. Railway will detect it's a Python project
5. Click **"Deploy"**

Railway will automatically:
- Install Python dependencies
- Start your bot
- Give you a public URL

---

## Step 5: Configure Environment Variables (Optional)

If needed, add environment variables in Railway:
1. Go to your project in Railway
2. Click **"Variables"** tab
3. Add any needed variables

---

## Step 6: Access Your Bot

Railway will give you a URL like:
```
https://toxic-bot.up.railway.app
```

This is your public URL! Share it with anyone.

**Default Admin Key**: `TOXIC2`

---

## Important Notes

### About $5 Credit:
- You get $5 free credit every month
- Your bot uses very little resources
- Should be enough for your use case
- If you need more, you can add payment later

### Uptime:
- Your bot runs 24/7 on Railway servers
- Your PC can be off
- Bot will keep running

### Updates:
- Push changes to GitHub
- Railway auto-redeploys
- Or click "Redeploy" in Railway dashboard

---

## Troubleshooting

### Build Fails
- Check `requirements.txt` has all dependencies
- Check Python version (Railway uses Python 3.9+)
- Check logs in Railway dashboard

### Service Not Starting
- Check logs in Railway dashboard
- Make sure Main.py is the entry point
- Check for missing files

### URL Not Working
- Wait a few minutes for deployment
- Check if service is running in Railway
- Try Railway's built-in preview

---

## Cost Summary

- **Monthly free credit**: $5
- **Your bot usage**: ~$0.10-0.50/month
- **Out of pocket**: $0 (as long as you stay within $5)

---

## Next Steps

1. ✅ Create Railway account
2. ✅ Create GitHub repository
3. ✅ Upload files
4. ✅ Deploy to Railway
5. ✅ Get your public URL
6. ✅ Share with users
7. ✅ Change default admin key

---

**Your bot will now run 24/7 even when your PC is off! 🎉**
