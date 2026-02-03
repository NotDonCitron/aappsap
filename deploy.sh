#!/bin/bash
# Railway Deployment Script for test_shop
# Usage: ./deploy.sh

set -e

echo "🚀 Railway Deployment Script for test_shop"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}Railway CLI not found. Installing...${NC}"
    npm install -g @railway/cli
fi

# Check if user is logged in
echo -e "\n📋 Checking Railway login status..."
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}Please login to Railway:${NC}"
    railway login
fi

echo -e "${GREEN}✅ Logged in to Railway${NC}"

# Check if project is linked
if [ ! -f .railway/config.json ]; then
    echo -e "\n${YELLOW}Project not linked to Railway.${NC}"
    echo "Options:"
    echo "1. Create new project"
    echo "2. Link to existing project"
    read -p "Choose (1/2): " choice
    
    if [ "$choice" = "1" ]; then
        echo -e "\n🆕 Creating new Railway project..."
        railway init
    else
        echo -e "\n🔗 Linking to existing project..."
        railway link
    fi
fi

# Deploy
echo -e "\n📦 Deploying to Railway..."
railway up

# Get project info
echo -e "\n📊 Getting deployment info..."
PROJECT_URL=$(railway domain 2>/dev/null || echo "Not available yet")
echo -e "${GREEN}🌐 App URL: ${PROJECT_URL}${NC}"

# Check if PostgreSQL is added
echo -e "\n🗄️  Checking for PostgreSQL database..."
if ! railway variables get DATABASE_URL &> /dev/null; then
    echo -e "${YELLOW}⚠️  No DATABASE_URL found.${NC}"
    echo "You need to add a PostgreSQL database:"
    echo "1. Go to Railway dashboard: https://railway.app/dashboard"
    echo "2. Click 'New' → 'Database' → 'Add PostgreSQL'"
    echo "3. The DATABASE_URL will be auto-set"
    echo ""
    read -p "Press Enter after adding PostgreSQL to continue..."
fi

# Set environment variables
echo -e "\n⚙️  Setting environment variables..."
if [ -f .env.deploy ]; then
    source .env.deploy
    railway variables set SECRET_KEY="$SECRET_KEY"
    railway variables set JWT_SECRET_KEY="$JWT_SECRET_KEY"
    railway variables set FLASK_ENV="production"
    echo -e "${GREEN}✅ Environment variables set${NC}"
else
    echo -e "${RED}❌ .env.deploy not found!${NC}"
    echo "Please set these manually in Railway dashboard:"
    echo "  - SECRET_KEY"
    echo "  - JWT_SECRET_KEY"
    echo "  - FLASK_ENV=production"
fi

# Initialize database
echo -e "\n🗃️  Initializing database..."
echo "Running: flask db upgrade (if migrations exist)"
railway run flask db upgrade 2>/dev/null || echo "No migrations found, creating tables..."

echo "Creating database tables..."
railway run python -c "
from app import create_app, db
app = create_app('production')
with app.app_context():
    db.create_all()
    print('✅ Database tables created!')
"

# Get final URL
echo -e "\n=========================================="
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo -e "=========================================="
PROJECT_DOMAIN=$(railway domain 2>/dev/null || echo "Check Railway dashboard")
echo -e "\n🌐 Your API is live at:"
echo -e "${GREEN}https://${PROJECT_DOMAIN}${NC}"
echo ""
echo "📚 API Endpoints:"
echo "  - GET  /api/v1/products          (List products)"
echo "  - POST /api/v1/auth/register     (Register user)"
echo "  - POST /api/v1/auth/login        (Login)"
echo "  - GET  /api/v1/cart              (View cart)"
echo ""
echo "🔧 Railway Dashboard:"
echo "  https://railway.app/dashboard"
echo ""
echo "⚠️  Next steps:"
echo "  1. Check logs: railway logs"
echo "  2. Test the API with the URLs above"
echo "  3. Add your own domain in Railway dashboard (optional)"
echo ""
