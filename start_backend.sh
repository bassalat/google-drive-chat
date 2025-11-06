#!/bin/bash
# Start the FastAPI backend server

echo "🚀 Starting Google Drive Chat Backend..."
echo "======================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please create a .env file with ANTHROPIC_API_KEY and other required variables"
    echo "See .env.example for reference"
    exit 1
fi

echo "✓ Found .env file (environment variables will be loaded by Python)"
echo ""

# Start the backend
echo "Starting server on http://localhost:8000"
echo "WebSocket available at ws://localhost:8000/api/ws"
echo ""

/Users/bassalat/opt/miniconda3/envs/venv_analysis/bin/python backend/main.py
