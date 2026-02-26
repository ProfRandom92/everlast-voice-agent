# Simple test app for Railway deployment
from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Test App")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Test deployment successful"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
