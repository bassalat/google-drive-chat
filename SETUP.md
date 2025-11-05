# Complete Setup Guide

This guide will walk you through setting up the Google Drive Chat application from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step 1: Get Anthropic API Key](#step-1-get-anthropic-api-key)
3. [Step 2: Set Up Google Cloud Project](#step-2-set-up-google-cloud-project)
4. [Step 3: Install Dependencies](#step-3-install-dependencies)
5. [Step 4: Configure Environment](#step-4-configure-environment)
6. [Step 5: Set Up Google Drive Authentication](#step-5-set-up-google-drive-authentication)
7. [Step 6: Run the Application](#step-6-run-the-application)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10 or higher** installed
- **Node.js 18 or higher** and npm installed
- A **Google account** with access to Google Drive
- An **Anthropic account** (for Claude API access)

### Check Your Versions

```bash
python3 --version  # Should be 3.10+
node --version     # Should be 18+
npm --version
```

---

## Step 1: Get Anthropic API Key

### 1.1 Create Anthropic Account

1. Go to [https://console.anthropic.com/](https://console.anthropic.com/)
2. Click **"Sign Up"** if you don't have an account
3. Complete the registration process

### 1.2 Get Your API Key

1. Once logged in, go to [https://console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
2. Click **"Create Key"** or **"+ Create API Key"**
3. Give your key a name (e.g., "Google Drive Chat")
4. Copy the API key and save it securely (you'll need it later)

> **Important:** Your API key starts with `sk-ant-api03-...` and should be kept secret!

---

## Step 2: Set Up Google Cloud Project

This is required to access the Google Drive API.

### 2.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** at the top → **"NEW PROJECT"**
3. Enter project details:
   - **Project name:** `Google Drive Chat` (or any name)
   - **Organization:** Leave as default or select your organization
4. Click **"CREATE"**
5. Wait for the project to be created (takes a few seconds)

### 2.2 Enable Google Drive API

1. Make sure your new project is selected (check the project name at the top)
2. Go to [Google Drive API Library](https://console.cloud.google.com/apis/library/drive.googleapis.com)
   - Or navigate: **APIs & Services** → **Library** → Search "Google Drive API"
3. Click on **"Google Drive API"**
4. Click **"ENABLE"**
5. Wait for the API to be enabled

### 2.3 Create OAuth 2.0 Credentials

1. Go to [Credentials Page](https://console.cloud.google.com/apis/credentials)
   - Or navigate: **APIs & Services** → **Credentials**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**

3. **Configure OAuth Consent Screen** (if prompted):
   - Click **"CONFIGURE CONSENT SCREEN"**
   - Select **"External"** (unless you have a Google Workspace)
   - Click **"CREATE"**
   - Fill in required fields:
     - **App name:** `Google Drive Chat`
     - **User support email:** Your email
     - **Developer contact information:** Your email
   - Click **"SAVE AND CONTINUE"**
   - **Scopes:** Click **"ADD OR REMOVE SCOPES"**
     - Find and select: `.../auth/drive.readonly` (Read-only Drive access)
     - Click **"UPDATE"**
     - Click **"SAVE AND CONTINUE"**
   - **Test users:** Click **"+ ADD USERS"**
     - Add your Google email address
     - Click **"ADD"**
     - Click **"SAVE AND CONTINUE"**
   - Review and click **"BACK TO DASHBOARD"**

4. **Create the OAuth Client:**
   - Go back to [Credentials Page](https://console.cloud.google.com/apis/credentials)
   - Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
   - **Application type:** Select **"Desktop app"**
   - **Name:** `Google Drive Chat Client`
   - Click **"CREATE"**

5. **Download credentials.json:**
   - A dialog appears with your client ID and secret
   - Click **"DOWNLOAD JSON"**
   - Save this file - you'll need it in the next step

---

## Step 3: Install Dependencies

### 3.1 Clone the Repository

```bash
git clone https://github.com/bassalat/google-drive-chat.git
cd google-drive-chat
```

### 3.2 Install Python Dependencies

```bash
# Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Dependencies installed:**
- `anthropic` - Anthropic API client
- `claude-agent-sdk` - Claude Agent SDK
- `fastapi` - Backend framework
- `uvicorn` - ASGI server
- `websockets` - WebSocket support
- `google-auth`, `google-auth-oauthlib`, `google-api-python-client` - Google Drive API
- `mcp` - Model Context Protocol SDK

### 3.3 Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

---

## Step 4: Configure Environment

### 4.1 Create .env File

```bash
cp .env.example .env
```

### 4.2 Edit .env File

Open `.env` in your text editor and configure:

```bash
# Required: Add your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE

# Python path (change if needed)
PYTHON_PATH=python3

# Backend configuration (default values work fine)
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0

# Frontend configuration (default values work fine)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

**Replace `YOUR_KEY_HERE` with your actual Anthropic API key from Step 1!**

---

## Step 5: Set Up Google Drive Authentication

### 5.1 Prepare credentials.json

1. Take the `credentials.json` file you downloaded in Step 2.3
2. Copy it to the project root directory:

```bash
# From your downloads folder
cp ~/Downloads/client_secret_*.json credentials.json
```

Or manually copy the file to your project directory and rename it to `credentials.json`.

### 5.2 Test Google Drive Connection

Run the Drive client to authenticate:

```bash
python3 drive_client.py
```

**What happens:**
1. A browser window will open automatically
2. You'll see Google's OAuth consent screen
3. Sign in with your Google account (must be a test user you added)
4. Click **"Continue"** when you see the "unverified app" warning
5. Review the permissions and click **"Allow"**
6. You should see "The authentication flow has completed"
7. Close the browser window

**Result:** A `token.json` file is created with your authentication token. This allows the app to access your Drive without requiring login every time.

---

## Step 6: Run the Application

### 6.1 Start the Backend

In your terminal (with virtual environment activated):

```bash
# Using the convenient startup script
chmod +x start_backend.sh
./start_backend.sh
```

Or manually:

```bash
python3 backend/main.py
```

You should see:
```
🚀 Starting Google Drive Chat Backend...
======================================
✓ ANTHROPIC_API_KEY is set
Starting server on http://localhost:8000
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!**

### 6.2 Start the Frontend

Open a **new terminal** window/tab:

```bash
cd frontend
npm run dev
```

Or use the startup script:

```bash
chmod +x start_frontend.sh
./start_frontend.sh
```

You should see:
```
   ▲ Next.js 15.1.5
   - Local:        http://localhost:3000
   - Network:      http://xxx.xxx.xxx.xxx:3000
 ✓ Ready in 2s
```

### 6.3 Open the App

1. Open your web browser
2. Go to [http://localhost:3000](http://localhost:3000)
3. You should see the chat interface!

### 6.4 Try Your First Query

Type a message like:
- "List all my Drive files"
- "Show me my recent documents"
- "Find PDF files in my Drive"

The AI will use the Google Drive tools to fetch and display your files!

---

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not set"

**Solution:**
1. Check your `.env` file exists: `ls -la .env`
2. Verify the key is set: `cat .env | grep ANTHROPIC_API_KEY`
3. Make sure there are no quotes around the key value
4. Restart the backend server

### Issue: "credentials.json not found"

**Solution:**
1. Verify the file exists: `ls -la credentials.json`
2. If not, go back to [Step 2.3](#23-create-oauth-20-credentials) and download it again
3. Make sure it's in the project root directory
4. The file should be named exactly `credentials.json`

### Issue: "Browser doesn't open for Google OAuth"

**Solution:**
1. Look for a URL in the terminal output
2. Copy the URL manually and paste it in your browser
3. Complete the OAuth flow as described in Step 5.2

### Issue: "Access blocked: This app's request is invalid"

**Solution:**
1. Make sure you added yourself as a test user in the OAuth consent screen
2. Go back to [Google Cloud Console → OAuth Consent Screen](https://console.cloud.google.com/apis/credentials/consent)
3. Click **"ADD USERS"** and add your Google email
4. Delete `token.json` and run `python3 drive_client.py` again

### Issue: "Invalid Scope" error

**Solution:**
1. Make sure you enabled the Google Drive API (Step 2.2)
2. Check OAuth consent screen scopes include `drive.readonly`
3. Delete `token.json` and re-authenticate

### Issue: Port 8000 or 3000 already in use

**Solution:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

Then restart the servers.

### Issue: Frontend can't connect to backend

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check WebSocket in browser console (F12 → Console)
3. Ensure both servers are running on correct ports
4. Check firewall/antivirus isn't blocking connections

### Issue: "Module not found" errors

**Solution:**
```bash
# Reinstall Python dependencies
pip install -r requirements.txt

# Reinstall frontend dependencies
cd frontend
npm install
cd ..
```

### Need More Help?

- Check the [README.md](README.md) for detailed documentation
- Review [QUICKSTART.md](QUICKSTART.md) for quick reference
- Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for architecture details

---

## What's Next?

Once everything is running:

1. **Explore the features** - Try different queries to interact with your Drive
2. **Customize the agent** - Edit `backend/agent.py` to modify AI behavior
3. **Add more tools** - Extend `mcp-server/server.py` with new Drive operations
4. **Customize the UI** - Modify `frontend/app/page.tsx` for your preferred interface

**Enjoy chatting with your Google Drive!** 🚀
