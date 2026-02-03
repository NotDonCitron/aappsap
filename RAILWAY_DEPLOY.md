# Railway Deployment Guide

## Quick Deploy (5 minutes)

### Step 1: Push to GitHub

```bash
cd ~/test_shop
git init  # if not already
git add .
git commit -m "Ready for Railway deployment"
# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/test_shop.git
git push -u origin main
```

### Step 2: Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `test_shop` repository
4. Railway auto-detects Python and deploys!

### Step 3: Add PostgreSQL Database

1. In your Railway project, click **"New"** → **"Database"** → **"Add PostgreSQL"**
2. Railway automatically sets `DATABASE_URL` environment variable
3. Redeploy happens automatically

### Step 4: Set Environment Variables

Go to your project **Variables** tab and add:

```
SECRET_KEY = <generate-with-secrets-token_hex(32)>
JWT_SECRET_KEY = <different-secret-key>
FLASK_ENV = production
```

**Generate secrets:**
```python
import secrets
print(secrets.token_hex(32))
```

### Step 5: Initialize Database

Once deployed, open Railway **Console** tab and run:

```bash
python -c "
from app import create_app, db
app = create_app('production')
with app.app_context():
    db.create_all()
    print('✅ Database tables created!')
"
```

---

## Alternative: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up

# Set variables
railway variables set SECRET_KEY="your-secret"
railway variables set JWT_SECRET_KEY="your-jwt-secret"

# Run commands
railway run python -c "from app import create_app, db; app = create_app('production'); db.create_all()"
```

---

## Verify Deployment

```bash
# Get your Railway URL (e.g., https://testshop-production.up.railway.app)
# Test the API:

curl https://YOUR_APP.railway.app/api/v1/products

# Should return: {"products": [...]}
```

---

## Troubleshooting

### Build Fails
```
# Check Python version in runtime.txt matches Railway's supported versions
# Current: python-3.11.6
```

### Database Connection Error
```
# Make sure PostgreSQL plugin is added
# Check DATABASE_URL is auto-set
```

### App Crashes
```bash
# Check logs in Railway dashboard "Deploy" tab
# Or via CLI:
railway logs
```

---

## Production Checklist

- [ ] PostgreSQL database connected
- [ ] SECRET_KEY is strong/random
- [ ] JWT_SECRET_KEY is different from SECRET_KEY
- [ ] FLASK_ENV=production set
- [ ] Database tables created
- [ ] Test user created (optional)
- [ ] Firebase credentials uploaded (optional)

---

## Free Tier Limits

- 500 hours/month runtime (~20 days continuous)
- 512 MB RAM
- 1 GB disk
- $5 credit/month

**Tip:** Add a credit card (no charge) to get $5 more credit = ~40 days continuous.
