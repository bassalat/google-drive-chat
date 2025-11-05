# Google Drive Chat

A conversational AI interface to interact with your Google Drive files using Claude Agent SDK and a custom MCP (Model Context Protocol) server.

## Architecture

```
┌─────────────────┐
│  Next.js        │
│  Frontend       │
│  (Port 3000)    │
└────────┬────────┘
         │
         │ WebSocket
         ▼
┌─────────────────┐
│  FastAPI        │
│  Backend        │
│  (Port 8000)    │
└────────┬────────┘
         │
         │
         ▼
┌─────────────────┐
│  Claude Agent   │
│  SDK            │
└────────┬────────┘
         │
         │ MCP Protocol
         ▼
┌─────────────────┐
│  Custom MCP     │
│  Server         │
│  (Drive Tools)  │
└────────┬────────┘
         │
         │
         ▼
┌─────────────────┐
│  Google Drive   │
│  API            │
└─────────────────┘
```

## Features

- **Conversational Interface**: Talk to your Google Drive files in natural language
- **Real-time Streaming**: See AI responses as they're generated via WebSocket
- **Drive Operations**:
  - List files and folders
  - Search files by name
  - Get file metadata
  - Download files
  - Read file contents (with automatic export for Google Workspace files)
- **Modern UI**: Beautiful, responsive interface built with Next.js and Tailwind CSS
- **MCP Integration**: Custom Model Context Protocol server for Drive operations

## Project Structure

```
gdrive_talk/
├── backend/                # FastAPI backend
│   ├── main.py            # API endpoints & WebSocket
│   └── agent.py           # Claude Agent SDK integration
├── mcp-server/            # Custom MCP server
│   └── server.py          # Drive tools implementation
├── frontend/              # Next.js frontend
│   ├── app/
│   │   ├── page.tsx       # Main chat interface
│   │   ├── layout.tsx     # Root layout
│   │   └── globals.css    # Global styles
│   └── package.json
├── drive_client.py        # Google Drive client
├── .drive-data/           # OAuth credentials & tokens
├── drive_files/           # Downloaded files
└── requirements.txt       # Python dependencies
```

## Setup

### Quick Links

- **New User?** Follow the complete [**SETUP.md**](SETUP.md) guide for step-by-step instructions
- **Already configured?** Use the [**QUICKSTART.md**](QUICKSTART.md) for quick reference

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- Google Drive API credentials ([how to get them](SETUP.md#step-2-set-up-google-cloud-project))
- Anthropic API key ([how to get it](SETUP.md#step-1-get-anthropic-api-key))

### Quick Setup

```bash
# 1. Clone the repository
git clone https://github.com/bassalat/google-drive-chat.git
cd google-drive-chat

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install frontend dependencies
cd frontend && npm install && cd ..

# 4. Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 5. Add credentials.json (see SETUP.md for details)
# Download from Google Cloud Console and place in project root

# 6. Run the app
./start_backend.sh   # Terminal 1
./start_frontend.sh  # Terminal 2
```

For detailed instructions, see [**SETUP.md**](SETUP.md).

## Running the Application

### 1. Start the Backend

```bash
# From the project root
/Users/bassalat/opt/miniconda3/envs/venv_analysis/bin/python backend/main.py
```

The backend will start on `http://localhost:8000`

### 2. Start the Frontend

```bash
# In a new terminal
cd frontend
npm run dev
```

The frontend will start on `http://localhost:3000`

### 3. Open the App

Navigate to `http://localhost:3000` in your browser.

## Usage

### Example Queries

- "List all my files from Google Drive"
- "Find all PDF files"
- "Search for files about [topic]"
- "Show me files modified this week"
- "Get details about file [file_id]"
- "Download and summarize [filename]"

### How It Works

1. **You send a message** via the web interface
2. **Frontend sends** message to backend via WebSocket
3. **Backend** forwards to Claude Agent SDK
4. **Agent** uses MCP tools to interact with Google Drive
5. **Drive operations** execute via Google Drive API
6. **Response streams back** through the stack to your browser

## API Endpoints

### Backend (FastAPI)

- `GET /` - Health check
- `GET /api/health` - API health status
- `POST /api/chat` - Send message (non-streaming)
- `WS /api/ws` - WebSocket for streaming chat
- `GET /api/sessions` - List chat sessions
- `GET /api/sessions/{id}` - Get session details
- `DELETE /api/sessions/{id}` - Delete session

## MCP Tools

The custom MCP server exposes these tools to Claude:

### `list_drive_files`
List files in Google Drive, optionally filtered by folder.

### `get_file_info`
Get detailed metadata for a specific file.

### `download_drive_file`
Download a file from Drive (exports Google Workspace files automatically).

### `read_downloaded_file`
Read contents of a downloaded file.

### `search_drive_files`
Search for files by name.

## Development

### Testing the MCP Server

```bash
/Users/bassalat/opt/miniconda3/envs/venv_analysis/bin/python mcp-server/server.py
```

### Testing the Agent

```bash
/Users/bassalat/opt/miniconda3/envs/venv_analysis/bin/python backend/agent.py
```

### Backend API Testing

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "List my files"}'
```

## Configuration

### Python Environment

All Python code uses the `venv_analysis` environment as specified in `.claude/instructions.md`.

### API Keys

Set these environment variables:

- `ANTHROPIC_API_KEY` - Your Anthropic API key
- OAuth credentials are in `.drive-data/credentials.json`

### Google Drive Scopes

Current scope: `https://www.googleapis.com/auth/drive.readonly` (read-only)

To enable file modifications, update the scopes in `drive_client.py`.

## Troubleshooting

### WebSocket Connection Issues

- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify frontend is connecting to correct WebSocket URL

### Google Drive Authentication

- First run will open browser for OAuth
- Token is saved in `.drive-data/token.pickle`
- Delete token file to re-authenticate

### MCP Server Issues

- Verify MCP SDK is installed: `pip show mcp`
- Check server path in `backend/agent.py`
- Run server standalone to test: `python mcp-server/server.py`

## Future Enhancements

- [ ] File upload support
- [ ] Folder management
- [ ] Sharing and permissions
- [ ] Multi-file analysis
- [ ] File preview in chat
- [ ] Session persistence (database)
- [ ] User authentication
- [ ] Deployment guides

## Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- Claude Agent SDK - AI agent framework
- MCP - Model Context Protocol
- Google Drive API - File access

**Frontend:**
- Next.js 15 - React framework
- TypeScript - Type safety
- Tailwind CSS - Styling
- Lucide Icons - UI icons

## License

MIT

## Contributing

This is a personal productivity tool. Feel free to fork and customize for your needs!
