#!/usr/bin/env python3
"""
Claude Agent SDK Integration
Connects the Claude Agent with Google Drive MCP server
"""

import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Optional, Dict
import asyncio

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


try:
    from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, McpSdkServerConfig, AssistantMessage, TextBlock
except ImportError:
    print("Warning: claude_agent_sdk not properly imported. Using mock implementation.")
    ClaudeSDKClient = None
    ClaudeAgentOptions = None
    McpSdkServerConfig = None
    AssistantMessage = None
    TextBlock = None


class DriveAgent:
    """
    Google Drive Chat Agent using Claude Agent SDK and custom MCP server.
    Uses ClaudeSDKClient for persistent conversations across multiple messages.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Drive Agent.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.mcp_server_path = Path(__file__).parent.parent / "mcp-server" / "server.py"
        self.agent_options = None
        self.clients: Dict[str, ClaudeSDKClient] = {}  # Session ID -> Client
        self._initialize_agent_options()

    def _initialize_agent_options(self):
        """Initialize the Claude Agent options."""
        if ClaudeAgentOptions is None:
            print("Warning: Running in mock mode without actual Claude Agent SDK")
            return

        # Configure the agent options (reusable for all clients)
        self.agent_options = ClaudeAgentOptions(
            model="claude-sonnet-4-5-20250929",  # Latest Sonnet 4.5
            system_prompt=self._get_system_prompt(),
            # Auto-approve ALL tool usage without permission prompts
            permission_mode="bypassPermissions",
            # NO tool restrictions - agent has access to ALL tools
            # MCP server configuration (dict not list)
            mcp_servers={
                "google-drive": McpSdkServerConfig(
                    name="google-drive",
                    command="/Users/bassalat/opt/miniconda3/envs/venv_analysis/bin/python",
                    args=[str(self.mcp_server_path)],
                    env={}
                )
            },
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent."""
        return """You are a helpful assistant that helps users interact with their Google Drive files.

You have FULL access to ALL tools including:

**Google Drive Tools (MCP):**
- list_drive_files: List files in Google Drive
- get_file_info: Get detailed information about a specific file
- download_drive_file: Download a file from Google Drive
- read_downloaded_file: Read the contents of a downloaded file
- search_drive_files: Search for files by name

**File Processing Tools:**
- Read: Read any downloaded file (text, code, JSON, CSV, etc.)
- Bash: Execute commands to process files (e.g., convert formats, extract data)
- Grep: Search within file contents
- WebFetch: Fetch web content if needed

**Important Capabilities:**
- Google Drive files can be in ANY format: PDFs, Google Docs, Sheets, Slides, images, code, etc.
- When you download Google Workspace files (Docs, Sheets, Slides), they are auto-exported to readable formats
- PDFs: Can be read as text
- Images: Can be analyzed
- Spreadsheets/CSV: Can be parsed and analyzed
- Use ALL available tools to fully answer user questions

**Workflow:**
1. Use list_drive_files or search_drive_files to find files
2. Use get_file_info to get metadata
3. Use download_drive_file to download files
4. Use read_downloaded_file or Read tool to access contents
5. Use Bash/other tools if you need to process/convert files
6. Provide comprehensive, helpful summaries

You have unrestricted access to all tools - use whatever is needed to help the user!
Always explain what you're doing and provide clear, helpful responses."""

    async def _get_or_create_client(self, session_id: str) -> ClaudeSDKClient:
        """Get existing client or create a new one for the session."""
        if session_id not in self.clients:
            # Create new client for this session
            client = ClaudeSDKClient(self.agent_options)
            await client.connect()
            self.clients[session_id] = client
        return self.clients[session_id]

    async def query(self, message: str, session_id: Optional[str] = None, conversation_history: Optional[list] = None) -> str:
        """
        Send a query to the agent and get a response.
        Uses ClaudeSDKClient for conversation continuity.

        Args:
            message: User message/query
            session_id: Session ID for conversation continuity
            conversation_history: Not used (client maintains history automatically)

        Returns:
            Agent's response as a string
        """
        if self.agent_options is None:
            # Mock response for testing
            return f"Mock agent response to: {message}\n(Claude Agent SDK configured but using mock mode for testing)"

        try:
            # Use session ID or create a default one
            sid = session_id or "default"

            # Get or create client for this session
            client = await self._get_or_create_client(sid)

            # Send message to client (maintains conversation context automatically)
            await client.query(message)

            # Collect full response
            result = ""
            async for msg in client.receive_response():
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            result += block.text

            return result
        except Exception as e:
            return f"Error: {str(e)}"

    async def stream_query(
        self,
        message: str,
        session_id: Optional[str] = None,
        conversation_history: Optional[list] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a query response from the agent.
        Uses ClaudeSDKClient for conversation continuity.

        Args:
            message: User message/query
            session_id: Session ID for conversation continuity
            conversation_history: Not used (client maintains history automatically)

        Yields:
            Response chunks as they arrive
        """
        if self.agent_options is None:
            # Mock streaming response
            chunks = [
                "Mock ", "streaming ", "response ", "to: ", message,
                "\n\n(Claude Agent SDK configured but using mock mode for testing.)"
            ]
            for chunk in chunks:
                yield chunk
                await asyncio.sleep(0.1)
            return

        try:
            # Use session ID or create a default one
            sid = session_id or "default"

            # Get or create client for this session
            client = await self._get_or_create_client(sid)

            # Send message to client (maintains conversation context automatically)
            await client.query(message)

            # Stream response chunks
            async for msg in client.receive_response():
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            yield block.text
        except Exception as e:
            yield f"Error: {str(e)}"

    async def close(self, session_id: Optional[str] = None):
        """Clean up agent resources for a session or all sessions."""
        if session_id:
            # Close specific session
            if session_id in self.clients:
                await self.clients[session_id].disconnect()
                del self.clients[session_id]
        else:
            # Close all sessions
            for client in self.clients.values():
                await client.disconnect()
            self.clients.clear()


# Singleton instance
_agent_instance: Optional[DriveAgent] = None


def get_agent() -> DriveAgent:
    """Get or create the global agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = DriveAgent()
    return _agent_instance


async def main():
    """Test the agent."""
    agent = DriveAgent()

    print("Testing Drive Agent...")
    print("=" * 60)

    # Test query
    response = await agent.query("List my Drive files")
    print(f"Response: {response}")

    print("\n" * 60)
    print("Testing streaming...")

    # Test streaming
    print("Streaming response:")
    async for chunk in agent.stream_query("What files do I have in my Drive?"):
        print(chunk, end="", flush=True)
    print()

    await agent.close()


if __name__ == "__main__":
    asyncio.run(main())
