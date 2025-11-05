# Quick Start Guide

Get your Google Drive Chat app running in 5 minutes!

> **First time setting up?** Follow the detailed [**SETUP.md**](SETUP.md) guide instead.
> This quick start assumes you already have credentials and dependencies installed.

## Step 1: Set Your API Key

```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

Get your key from: https://console.anthropic.com/

## Step 2: Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

## Step 3: Start the Backend

```bash
/Users/bassalat/opt/miniconda3/envs/venv_analysis/bin/python backend/main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Start the Frontend (New Terminal)

```bash
cd frontend
npm run dev
```

You should see:
```
  ▲ Next.js 15.1.5
  - Local:        http://localhost:3000
```

## Step 5: Open the App

Go to: **http://localhost:3000**

## Try These Queries

1. "List all my files from Google Drive"
2. "Find PDF files"
3. "Search for files about marketing"
4. "Show me my most recent files"

## First-Time Google Drive Auth

The first time you make a Drive query, a browser will open for Google OAuth authorization. After authorizing, the token is saved for future use.

## Troubleshooting

### Backend won't start
- Check ANTHROPIC_API_KEY is set: `echo $ANTHROPIC_API_KEY`
- Verify Python environment: `which python` should show venv_analysis

### Frontend won't connect
- Ensure backend is running on port 8000
- Check WebSocket connection in browser console

### Google Drive auth issues
- Delete `.drive-data/token.pickle` and try again
- Verify credentials in `.drive-data/credentials.json`

## What's Happening?

1. **Frontend** (Next.js) → Beautiful chat interface
2. **WebSocket** → Real-time communication
3. **Backend** (FastAPI) → Handles requests
4. **Claude Agent** → AI brain with tools
5. **MCP Server** → Google Drive operations
6. **Drive API** → Your actual files

## Next Steps

- Read [README.md](README.md) for full documentation
- Explore the code in `backend/` and `frontend/`
- Customize the system prompt in `backend/agent.py`
- Add new MCP tools in `mcp-server/server.py`

## Need Help?

Check the full [README.md](README.md) for detailed troubleshooting and configuration options.

---

**Happy chatting with your Drive files!** 🚀
