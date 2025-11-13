# Railway Deployment Guide

**Deploy WordPress SEO Publishing API to Railway in 15 minutes**

Railway provides free hosting with automatic HTTPS, making it perfect for internal tools.

---

## 🎯 Why Railway?

✅ **Free Tier** - $5 credit/month (enough for this API)
✅ **Automatic HTTPS** - Free SSL certificates
✅ **Easy Deployment** - Git push to deploy
✅ **Environment Variables** - Built-in secrets management
✅ **Persistent Volumes** - Database storage
✅ **Zero Config** - Detects Python automatically

---

## 📋 Prerequisites

1. **GitHub Account** - To connect repository
2. **Railway Account** - Sign up at [railway.app](https://railway.app)
3. **API Keys Generated** - Run: `python api/core/security.py`
4. **Google OAuth Credentials** - `client_secret.json` file ready

---

## 🚀 Deployment Steps

### Step 1: Push Code to GitHub (5 minutes)

```bash
cd agno_agent_seo_posting

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Add FastAPI backend for Railway deployment"

# Create GitHub repo and push
# (Replace with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/wordpress-seo-api.git
git branch -M main
git push -u origin main
```

**Important**: Make sure `.gitignore` is in place so sensitive files aren't committed!

---

### Step 2: Create Railway Project (2 minutes)

1. **Go to Railway**: https://railway.app/dashboard
2. **Click "New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Authorize GitHub** if first time
5. **Select your repository**: `wordpress-seo-api`
6. **Click "Deploy Now"**

Railway will automatically:
- Detect Python application
- Install dependencies from `requirements.txt`
- Use `Procfile` or auto-detect start command
- Assign a public URL

---

### Step 3: Configure Environment Variables (5 minutes)

In Railway dashboard:

1. **Click on your service**
2. **Go to "Variables" tab**
3. **Add these variables**:

#### Required Variables

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=$PORT
API_SECRET_KEY=<generate-secure-random-string>
API_KEYS=<your-generated-api-keys-comma-separated>

# Anthropic API
ANTHROPIC_API_KEY=<your-anthropic-api-key>

# Database Path
CLIENT_DB_PATH=/app/data/clients.db

# Google OAuth Paths
GOOGLE_CLIENT_SECRETS=/app/credentials/client_secret.json
GOOGLE_TOKEN_PATH=/app/credentials/token.json

# CORS (optional - restrict in production)
ALLOWED_ORIGINS=*
ENABLE_CORS=true

# Logging
LOG_LEVEL=INFO
```

#### Optional Variables (WordPress defaults)

```env
WP_BASE_URL=https://your-wordpress-site.com
WP_USERNAME=your_username
WP_APP_PASS=xxxx xxxx xxxx xxxx
```

**How to add**:
- Click "New Variable"
- Enter name and value
- Click "Add"
- Repeat for all variables

---

### Step 4: Configure Persistent Volume (3 minutes)

Railway provides persistent storage for your database:

1. **In Railway dashboard**, go to your service
2. **Click "Settings" tab**
3. **Scroll to "Volumes"**
4. **Click "Add Volume"**
5. **Configure**:
   - **Mount Path**: `/app/data`
   - **Size**: 1 GB (more than enough)
6. **Click "Add Volume"**

This ensures your database persists across deployments!

---

### Step 5: Upload Google OAuth Credentials (Important!)

Railway doesn't support file uploads directly, so we need to use environment variables:

**Option A: Base64 Encode (Recommended)**

```bash
# On your local machine

# 1. Encode client_secret.json
base64 -w 0 credentials/client_secret.json > client_secret_base64.txt

# 2. Copy the content
cat client_secret_base64.txt
```

In Railway Variables:
```env
GOOGLE_CLIENT_SECRET_BASE64=<paste-base64-content>
```

Then update `api/core/config.py` to decode on startup (see Option A code below).

**Option B: Manual Entry (Simpler but less secure)**

Copy content of `client_secret.json` and paste as Railway variable:

```env
GOOGLE_CLIENT_SECRET_JSON={"installed":{"client_id":"...","client_secret":"...",...}}
```

**Option C: Railway CLI (Advanced)**

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# Upload file
railway run --service api bash -c "mkdir -p credentials && cat > credentials/client_secret.json" < credentials/client_secret.json
```

**For now, I'll add code to handle Option A (Base64)**:

---

### Step 6: Update Code for Railway (if using Base64)

Add to `api/core/config.py` after Settings class:

```python
# Add after settings = Settings()

import os
import json
import base64
from pathlib import Path

# Decode Google credentials from environment if provided
if os.getenv("GOOGLE_CLIENT_SECRET_BASE64"):
    print("Decoding Google credentials from environment...")
    credentials_dir = Path("/app/credentials")
    credentials_dir.mkdir(parents=True, exist_ok=True)

    # Decode and write client_secret.json
    encoded = os.getenv("GOOGLE_CLIENT_SECRET_BASE64")
    decoded = base64.b64decode(encoded)

    with open(credentials_dir / "client_secret.json", "wb") as f:
        f.write(decoded)

    print("✓ Google credentials decoded successfully")

elif os.getenv("GOOGLE_CLIENT_SECRET_JSON"):
    print("Loading Google credentials from JSON environment...")
    credentials_dir = Path("/app/credentials")
    credentials_dir.mkdir(parents=True, exist_ok=True)

    # Write JSON directly
    json_content = os.getenv("GOOGLE_CLIENT_SECRET_JSON")

    with open(credentials_dir / "client_secret.json", "w") as f:
        f.write(json_content)

    print("✓ Google credentials loaded successfully")
```

Commit and push:
```bash
git add api/core/config.py
git commit -m "Add Railway environment credentials support"
git push
```

Railway will auto-deploy!

---

### Step 7: Verify Deployment (2 minutes)

1. **Check Deployment Logs**:
   - In Railway dashboard, go to "Deployments" tab
   - Click on latest deployment
   - Watch logs for errors

2. **Test Health Check**:
   ```bash
   # Replace with your Railway URL
   curl https://your-app.railway.app/api/v1/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "version": "1.0.0",
     "timestamp": "2025-11-13T..."
   }
   ```

3. **Test Authenticated Endpoint**:
   ```bash
   curl -H "X-API-Key: your-api-key" \
        https://your-app.railway.app/api/v1/projects
   ```

4. **Visit Interactive Docs**:
   ```
   https://your-app.railway.app/api/v1/docs
   ```

---

## 🌐 Custom Domain (Optional)

### Railway Provides Free Domain

Railway automatically provides:
- `https://your-app.railway.app` (free)
- Automatic HTTPS
- No configuration needed

### Add Custom Domain

1. **In Railway dashboard**, go to "Settings"
2. **Scroll to "Domains"**
3. **Click "Add Domain"**
4. **Enter your domain**: `api.yourdomain.com`
5. **Add CNAME record** to your DNS:
   ```
   CNAME api -> your-app.railway.app
   ```
6. **Wait for DNS propagation** (5-30 minutes)
7. **Railway automatically provisions SSL**

---

## 📊 Monitoring & Logs

### View Logs

**Railway Dashboard**:
1. Go to your service
2. Click "Logs" tab
3. Real-time logs streaming

**CLI**:
```bash
railway logs
```

### Metrics

Railway provides:
- **CPU usage**
- **Memory usage**
- **Network traffic**
- **Request count**

View in "Metrics" tab.

### Health Checks

Railway automatically monitors:
- `/api/v1/health` endpoint
- Restarts on failure
- Configured in `railway.toml`

---

## 💰 Cost Estimation

### Railway Free Tier

- **$5 credit/month** (free)
- Enough for ~500 hours of runtime
- **This API uses ~$3-4/month** (24/7)

### If You Need More

**Hobby Plan**: $5/month
- 500 hours execution
- 500 GB bandwidth
- More resources

**Pro Plan**: $20/month
- Unlimited execution
- Unlimited bandwidth
- Priority support

**Your usage**: API + Database = ~$3-4/month → **Free tier is enough!**

---

## 🔐 Security Checklist

### Before Going Live

- [ ] API keys generated and stored in Railway Variables
- [ ] `API_SECRET_KEY` is a strong random string
- [ ] `.gitignore` includes sensitive files
- [ ] No credentials in git repository
- [ ] Google OAuth credentials uploaded securely
- [ ] CORS origins restricted (not `*`)
- [ ] Environment variables double-checked

### After Deployment

- [ ] Test all endpoints work
- [ ] Verify database persists (create project, redeploy, check it exists)
- [ ] Test batch publishing works
- [ ] Monitor logs for errors
- [ ] Set up alerts (Railway can notify on failures)

---

## 🐛 Troubleshooting

### "Application failed to start"

**Check**:
1. **Build logs** - Look for dependency installation errors
2. **Environment variables** - Ensure all required vars are set
3. **Port** - Railway injects `$PORT`, we use it in `Procfile`

**Fix**:
```bash
# Check Procfile is correct
cat Procfile
# Should be: web: uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

---

### "502 Bad Gateway"

**Cause**: App not listening on correct port

**Fix**: Ensure using `$PORT` from Railway:
```python
# In api/core/config.py
API_PORT: int = int(os.getenv("PORT", os.getenv("API_PORT", "8000")))
```

---

### "Database not persisting"

**Cause**: Volume not configured

**Fix**:
1. Check volume is mounted at `/app/data`
2. Check `CLIENT_DB_PATH=/app/data/clients.db` in variables
3. Redeploy after adding volume

---

### "Google Docs conversion fails"

**Cause**: Credentials not loaded

**Check**:
1. `GOOGLE_CLIENT_SECRET_BASE64` or `GOOGLE_CLIENT_SECRET_JSON` is set
2. Check logs for "Google credentials decoded successfully"
3. Try Option C (Railway CLI) to upload file directly

---

### "Import errors"

**Cause**: Dependencies not installed

**Fix**:
```bash
# Ensure requirements.txt is up to date
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push
```

---

## 🔄 Updates & Redeployment

### Automatic Deployment

Railway watches your GitHub repo:
1. Push to `main` branch
2. Railway automatically rebuilds
3. Zero downtime deployment

```bash
# Make changes
git add .
git commit -m "Update API"
git push

# Railway deploys automatically!
```

### Manual Deployment

In Railway dashboard:
1. Go to "Deployments"
2. Click "Deploy" button
3. Select commit to deploy

---

## 📱 Lark Base Configuration

Once deployed, update Lark Base automations:

**HTTP Request URLs**:
```
# Change from:
http://localhost:8000/api/v1/publish

# To:
https://your-app.railway.app/api/v1/publish
```

**Headers**:
```json
{
  "X-API-Key": "your-api-key-from-railway",
  "Content-Type": "application/json"
}
```

---

## ✅ Post-Deployment Checklist

- [ ] Health check returns 200 OK
- [ ] Can list projects via API
- [ ] Can publish single content
- [ ] Can batch publish (test with 2-3 docs)
- [ ] Database persists across redeploys
- [ ] Lark Base can connect to API
- [ ] Team members have API keys
- [ ] Documentation updated with Railway URL

---

## 🚀 Quick Start (TL;DR)

```bash
# 1. Push to GitHub
git init && git add . && git commit -m "Initial commit"
git remote add origin https://github.com/YOU/wordpress-seo-api.git
git push -u origin main

# 2. Deploy on Railway
# - Go to railway.app
# - New Project → Deploy from GitHub
# - Select your repo

# 3. Add Environment Variables
# - API_KEYS=<your-keys>
# - ANTHROPIC_API_KEY=<your-key>
# - GOOGLE_CLIENT_SECRET_BASE64=<base64-encoded>

# 4. Add Volume
# - Settings → Volumes → Add Volume
# - Mount Path: /app/data

# 5. Test
curl https://your-app.railway.app/api/v1/health
```

---

## 📚 Resources

- **Railway Docs**: https://docs.railway.app
- **Railway CLI**: https://docs.railway.app/develop/cli
- **Nixpacks**: https://nixpacks.com
- **FastAPI on Railway**: https://docs.railway.app/guides/fastapi

---

## 🎉 Success!

Your API is now deployed on Railway with:
- ✅ Automatic HTTPS
- ✅ Persistent database storage
- ✅ Auto-deployment from GitHub
- ✅ Free hosting ($5/month credit)
- ✅ Professional domain

**Next**: Set up Lark Base to use your new Railway URL!

---

**Deployment Time**: 15 minutes
**Cost**: Free (with $5/month credit)
**Status**: Production Ready
**Last Updated**: 2025-11-13
