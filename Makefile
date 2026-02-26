# Everlast Voice Agent - Deployment Makefile

.PHONY: install deploy-backend deploy-dashboard deploy-db deploy-vapi deploy-all test clean

# Default target
all: install deploy-all

# Installation
install:
	@echo "Installing dependencies..."
	npm install -g @railway/cli vercel supabase
	cd api && pip install -r requirements.txt
	cd dashboard && npm install

# Deploy Backend to Railway
deploy-backend:
	@echo "Deploying to Railway..."
	cd api && railway login
	cd api && railway up

# Deploy Dashboard to Vercel
deploy-dashboard:
	@echo "Deploying to Vercel..."
	cd dashboard && vercel login
	cd dashboard && vercel --prod

# Push Supabase Schema
deploy-db:
	@echo "Pushing database schema..."
	supabase login
	supabase db push

# Import Vapi Assistant
deploy-vapi:
	@echo "Importing Vapi Assistant..."
	curl -X POST https://api.vapi.ai/assistant \
		-H "Authorization: Bearer $(VAPI_API_KEY)" \
		-H "Content-Type: application/json" \
		-d @vapi/assistant.json

# Full deployment
deploy-all: deploy-db deploy-backend deploy-dashboard deploy-vapi
	@echo "🎉 Full deployment complete!"

# Run tests
test:
	@echo "Running tests..."
	cd api && pytest
	cd dashboard && npm test

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf api/__pycache__
	rm -rf dashboard/.next
	rm -rf dashboard/node_modules
	rm -rf checkpoints.db

# Development
dev-backend:
	cd api && uvicorn main:app --reload

dev-dashboard:
	cd dashboard && npm run dev

# Health checks
health-backend:
	curl http://localhost:8000/health

health-production:
	curl https://everlast-api.up.railway.app/health
