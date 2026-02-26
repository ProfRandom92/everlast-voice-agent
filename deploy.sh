#!/bin/bash
# Deploy script for Everlast Voice Agent
# Usage: ./deploy.sh

set -e

echo "🚀 EVERLAST VOICE AGENT - DEPLOYMENT"
echo "====================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for required environment variables
check_env() {
    if [ -z "$1" ]; then
        echo -e "${RED}❌ Missing: $2${NC}"
        return 1
    else
        echo -e "${GREEN}✓ $2 set${NC}"
        return 0
    fi
}

echo "1️⃣ Checking Environment Variables..."
echo "--------------------------------------"

ENV_OK=true
check_env "$VAPI_API_KEY" "VAPI_API_KEY" || ENV_OK=false
check_env "$SUPABASE_URL" "SUPABASE_URL" || ENV_OK=false
check_env "$SUPABASE_SERVICE_KEY" "SUPABASE_SERVICE_KEY" || ENV_OK=false
check_env "$ANTHROPIC_API_KEY" "ANTHROPIC_API_KEY" || ENV_OK=false
check_env "$CALENDLY_API_KEY" "CALENDLY_API_KEY" || ENV_OK=false

if [ "$ENV_OK" = false ]; then
    echo ""
    echo -e "${RED}❌ Please set all required environment variables${NC}"
    echo "Copy .env.example to .env and fill in your values"
    exit 1
fi

echo ""
echo "2️⃣ Deploying to Railway (Backend)..."
echo "--------------------------------------"

cd api

# Link to railway project if not already linked
if [ ! -f ".railway/config.json" ]; then
    echo "Linking to Railway project..."
    railway link --project everlast-voice-agent
fi

# Set environment variables
echo "Setting environment variables..."
railway variables set VAPI_API_KEY="$VAPI_API_KEY"
railway variables set SUPABASE_URL="$SUPABASE_URL"
railway variables set SUPABASE_SERVICE_KEY="$SUPABASE_SERVICE_KEY"
railway variables set ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
railway variables set CALENDLY_API_KEY="$CALENDLY_API_KEY"
railway variables set ENVIRONMENT="production"
railway variables set CHECKPOINTER_BACKEND="supabase"

# Deploy
echo "Deploying..."
railway up --detach

# Get deployment URL
API_URL=$(railway domain)
echo -e "${GREEN}✓ Backend deployed to: $API_URL${NC}"

cd ..

echo ""
echo "3️⃣ Deploying to Vercel (Dashboard)..."
echo "--------------------------------------"

cd dashboard

# Set environment variables
vercel env add NEXT_PUBLIC_SUPABASE_URL production <<< "$SUPABASE_URL"
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production <<< "$SUPABASE_ANON_KEY"

# Deploy
echo "Deploying..."
vercel --prod --yes

cd ..

echo ""
echo "4️⃣ Pushing Supabase Schema..."
echo "--------------------------------------"

# Push schema
supabase link --project-ref "${SUPABASE_URL##*/}"
supabase db push

echo -e "${GREEN}✓ Database schema pushed${NC}"

echo ""
echo "5️⃣ Importing Vapi Assistant..."
echo "--------------------------------------"

# Update assistant.json with deployment URL
sed -i "s|https://everlast-api.railway.app|$API_URL|g" vapi/assistant.json

# Import assistant
curl -X POST https://api.vapi.ai/assistant \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d @vapi/assistant.json

echo -e "${GREEN}✓ Vapi Assistant imported${NC}"

echo ""
echo "======================================"
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo "======================================"
echo ""
echo "URLs:"
echo "  Backend: $API_URL"
echo "  Dashboard: https://everlast-dashboard.vercel.app"
echo ""
echo "Next steps:"
echo "  1. Configure Vapi webhook URL: $API_URL/vapi/webhook"
echo "  2. Test the voice agent with a call"
echo "  3. Monitor the dashboard"
echo ""
