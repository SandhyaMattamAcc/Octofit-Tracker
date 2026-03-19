#!/bin/bash
# AMS Dashboard Startup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🤖 Agentic AMS Dashboard"
echo "================================"

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 is required"
    exit 1
fi

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install Python deps
echo "📦 Installing Python dependencies..."
pip install -q -r requirements.txt

# Start backend
echo ""
echo "🚀 Starting FastAPI backend on http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""

if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run backend
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "✅ Backend started (PID: $BACKEND_PID)"
echo ""
echo "📊 Frontend:"
echo "   cd frontend && npm install && npm run dev"
echo "   Then open http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop"

wait $BACKEND_PID
