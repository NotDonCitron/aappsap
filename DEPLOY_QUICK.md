# Quick Railway Deploy - 5 Minutes

## What You Need

1. **GitHub account** (free)
2. **Railway account** (free tier available)
3. **Node.js/npm** (for Railway CLI)

## Step-by-Step

### Step 1: Create GitHub Repo

Go to https://github.com/new and create a repository called `test-shop` (or any name).

### Step 2: Push Code to GitHub

```bash
cd ~/test_shop

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial deployment"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/test-shop.git

# Push
git push -u origin main
```

### Step 3: Install Railway CLI

```bash
npm install -g @railway/cli
```

### Step 4: Deploy with One Command

```bash
cd ~/test_shop
./deploy.sh
```

This script will:
- ✅ Login to Railway
- ✅ Create/link project
- ✅ Deploy the app
- ✅ Set environment variables
- ✅ Initialize database

### Step 5: Add PostgreSQL (Required)

If the script prompts you:
1. Go to https://railway.app/dashboard
2. Click your project
3. Click "New" → "Database" → "Add PostgreSQL"
4. Railway auto-sets `DATABASE_URL`
5. Redeploy: `railway up`

### Step 6: Test Your API

```bash
# Get your app URL
railway domain

# Test it
curl https://YOUR-APP.up.railway.app/api/v1/products
```

---

## Manual Setup (If Script Doesn't Work)

### Deploy via Railway Dashboard

1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `test-shop` repo
4. Railway auto-deploys!

### Set Environment Variables

In Railway Dashboard → Your Project → Variables:

```
SECRET_KEY=65c6f1d492d25e459e81525e40be7909a627f3851f836fe68aba89851879b923
JWT_SECRET_KEY=db42b0daa79a1791e6e86d530cc5ad0b516b0d9473c18b26e49afbc57a979494
FLASK_ENV=production
```

### Add PostgreSQL

Dashboard → New → Database → PostgreSQL

### Initialize Database

Dashboard → Your Project → Console:

```python
python -c "
from app import create_app, db
app = create_app('production')
with app.app_context():
    db.create_all()
    print('Done!')
"
```

---

## Troubleshooting

### "Error: Not authenticated"
```bash
railway login
```

### "Error: No project linked"
```bash
railway init  # Create new project
# OR
railway link  # Link existing
```

### "Database connection failed"
Make sure PostgreSQL is added and `DATABASE_URL` is set.

### Check logs
```bash
railway logs
```

---

## Your API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/register | Create account |
| POST | /api/v1/auth/login | Get JWT token |
| GET | /api/v1/products | List products |
| GET | /api/v1/cart | View cart |
| POST | /api/v1/cart/add | Add to cart |
| GET | /api/v1/shipping/calculate | Calculate shipping |

---

## Free Tier Limits

- 500 hours/month (~20 days continuous)
- 512 MB RAM
- 1 GB disk

**Pro tip:** Add a credit card (no charge) → get $5 credit = ~40 days continuous runtime.
