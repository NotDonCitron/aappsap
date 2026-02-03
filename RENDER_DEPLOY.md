# Deploy to Render (Easier than Railway!)

## Option 1: Deploy via Dashboard (Recommended)

### Step 1: Push to GitHub
```bash
cd ~/test_shop
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Click **"New Web Service"**

### Step 3: Configure
1. Select your **aappsap** repo
2. **Name:** `test-shop`
3. **Runtime:** Python 3
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 'app:create_app("production")'`
6. Click **"Create Web Service"**

### Step 4: Add PostgreSQL
1. Click **"New"** → **"PostgreSQL"**
2. **Name:** `test-shop-db`
3. **Plan:** Free
4. Wait for it to be created
5. Copy the **Internal Database URL**

### Step 5: Set Environment Variables
In your Web Service → **Environment** tab, add:
```
SECRET_KEY=65c6f1d492d25e459e81525e40be7909a627f3851f836fe68aba89851879b923
JWT_SECRET_KEY=db42b0daa79a1791e6e86d530cc5ad0b516b0d9473c18b26e49afbc57a979494
FLASK_ENV=production
DATABASE_URL=<paste-the-internal-db-url-here>
```

### Step 6: Deploy!
Click **"Manual Deploy"** → **"Clear build cache & deploy"**

---

## Option 2: Deploy via Blueprint (render.yaml)

Click this button:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/NotDonCitron/aappsap)

Then:
1. Sign in with GitHub
2. Review the settings
3. Click **"Apply"**
4. Render auto-creates database and deploys!

---

## Verify Deployment

```bash
# Your app will be at:
# https://test-shop.onrender.com

# Test it:
curl https://test-shop.onrender.com/api/v1/products
```

---

## Free Tier Limits

- Web Service: 512 MB RAM, sleeps after 15 min inactivity
- PostgreSQL: 1 GB storage, expires after 90 days (can recreate)
- Custom domains: Yes
- HTTPS: Auto-enabled

---

## Troubleshooting

### "Build failed"
- Check Python version (3.11 in requirements.txt)
- Check build logs in Render dashboard

### "Application Error"
- Check service logs
- Verify DATABASE_URL is set
- Check SECRET_KEY and JWT_SECRET_KEY are set

### Database connection failed
- Make sure PostgreSQL is created
- Copy the correct Internal URL (not External)
- Format: `postgresql://user:pass@host:5432/dbname`

---

## Your API Endpoints

Once live:
```
POST https://test-shop.onrender.com/api/v1/auth/register
POST https://test-shop.onrender.com/api/v1/auth/login
GET  https://test-shop.onrender.com/api/v1/products
GET  https://test-shop.onrender.com/api/v1/cart
POST https://test-shop.onrender.com/api/v1/shipping/calculate
```
