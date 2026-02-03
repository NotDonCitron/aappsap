# Custom Domain Setup for aappsap

## Current URL

Your app is live at: **https://test-shop-7zkm.onrender.com**

## Adding a Custom Domain

### Step 1: Add Domain in Render Dashboard

1. Go to https://dashboard.render.com/web/srv-d60pcm2qcgvc7382n5kg
2. Click **"Settings"** tab
3. Scroll to **"Custom Domains"**
4. Click **"Add Custom Domain"**
5. Enter your domain (e.g., `aappsap.com` or `api.aappsap.com`)
6. Click **"Add"**

### Step 2: Configure DNS

Add the following DNS records at your domain registrar:

#### Option A: Apex Domain (aappsap.com)

| Type | Name | Value |
|------|------|-------|
| A | @ | 76.76.21.21 |

#### Option B: Subdomain (api.aappsap.com)

| Type | Name | Value |
|------|------|-------|
| CNAME | api | test-shop-7zkm.onrender.com |

### Step 3: Verify SSL

Render automatically provisions SSL certificates. This may take a few minutes to a few hours.

---

## Environment Variables Reference

Your app has these environment variables set:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | (auto-generated) |
| `JWT_SECRET_KEY` | (auto-generated) |
| `FLASK_ENV` | `production` |
| `DATABASE_URL` | (from PostgreSQL) |
| `PYTHON_VERSION` | `3.11.0` |
| `SEED_ON_STARTUP` | `true` |

---

## Useful Commands

### Access Shell
```bash
ssh srv-d60pcm2qcgvc7382n5kg@ssh.oregon.render.com
```

### View Logs
```bash
# Via Render dashboard or API
curl -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.render.com/v1/services/srv-d60pcm2qcgvc7382n5kg/logs"
```

### Redeploy
```bash
# Push to main branch triggers auto-deploy
git add .
git commit -m "fix: update"
git push origin main

# Or trigger manually via API
curl -X POST -H "Authorization: Bearer YOUR_API_KEY" \
  "https://api.render.com/v1/services/srv-d60pcm2qcgvc7382n5kg/deploys"
```

---

## Service Info

| Setting | Value |
|---------|-------|
| Name | aappsap |
| Region | Oregon (US West) |
| Runtime | Python 3.11 |
| Plan | Free |
| Service ID | srv-d60pcm2qcgvc7382n5kg |
| Database | dpg-d60pccqqcgvc7382mqng-a |
