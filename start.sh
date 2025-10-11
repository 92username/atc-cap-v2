#!/bin/sh

# Start FastAPI backend in background
cd /app
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &

# Start Nginx in foreground
nginx -g "daemon off;"