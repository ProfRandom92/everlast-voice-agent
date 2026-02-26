FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY everlast_voice_agents/ ./everlast_voice_agents/

# Expose port
EXPOSE 8000

# Start the application using Railway's dynamic PORT
CMD ["sh", "-c", "python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
