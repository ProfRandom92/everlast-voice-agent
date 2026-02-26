#!/bin/bash
# Startup script for Everlast Voice Agent API

cd /app/api || cd api || true
exec python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
