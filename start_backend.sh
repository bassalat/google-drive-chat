#!/bin/bash
# Start the FastAPI backend server

echo "🚀 Starting Google Drive Chat Backend..."
echo "======================================"

# Load .env file if it exists
if [ -f .env ]; then
    echo "📝 Loading environment from .env file..."
    export $(cat .env | grep -v '^#' | grep -v '^$' | xargs)
fi

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY environment variable not set"
    echo "Please add it to .env file or export it manually"
    exit 1
fi

echo "✓ ANTHROPIC_API_KEY is set (${ANTHROPIC_API_KEY:0:20}...)"
echo ""

# Start the backend
echo "Starting server on http://localhost:8000"
echo "WebSocket available at ws://localhost:8000/api/ws"
echo ""

/Users/bassalat/opt/miniconda3/envs/venv_analysis/bin/python backend/main.py
