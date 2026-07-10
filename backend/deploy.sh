#!/bin/bash
cd "$(dirname "$0")" || exit
echo "🔄 Pulling latest updates from GitHub..."
git pull origin main

echo "📦 Installing backend requirements..."
pip install -r requirements.txt --user --no-warn-script-location

PORT=8000
echo "🧹 Clearing occupied ports..."
PID=$(lsof -t -i:$PORT)
if [ ! -z "$PID" ]; then
    kill -9 $PID
    sleep 2
fi

echo "🚀 Launching FastAPI server..."
nohup python -m uvicorn app:app --host 0.0.0.0 --port $PORT > backend_runtime.log 2>&1 &
echo "✅ Server running! View logs with: tail -f backend_runtime.log"