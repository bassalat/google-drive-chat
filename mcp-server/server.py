#!/usr/bin/env python3
"""
Google Drive MCP Server
Exposes Google Drive operations as MCP tools for Claude Agent SDK
"""

import sys
import os
import json
from pathlib import Path
from typing import Any

# Add parent directory to path to import drive_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from drive_client import DriveClient
from mcp.server.stdio import stdio_server
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)


class DriveMCPServer:
    """MCP Server for Google Drive operations."""

    def __init__(self):
        self.server = Server("google-drive-server")
        self.drive_client = None
        self._setup_handlers()

    def _get_client(self) -> DriveClient:
        """Get or initialize the Drive client."""
        if self.drive_client is None:
            self.drive_client = DriveClient()
            self.drive_client.connect()
        return self.drive_client

    def _setup_handlers(self):
        """Set up MCP server request handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available Drive tools."""
            return [
                Tool(
                    name="list_drive_files",
                    description="List files in Google Drive. Returns file metadata including ID, name, type, and modification time. Optionally filter by folder ID.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "folder_id": {
                                "type": "string",
                                "description": "Optional: Google Drive folder ID to list files from. If not provided, lists from root."
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of files to return (default: 100)",
                                "default": 100
                            }
                        }
                    }
                ),
                Tool(
                    name="get_file_info",
                    description="Get detailed metadata for a specific Google Drive file by ID or URL. Returns file name, type, size, and modification time.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_id": {
                                "type": "string",
                                "description": "Google Drive file ID or full URL"
                            }
                        },
                        "required": ["file_id"]
                    }
                ),
                Tool(
                    name="download_drive_file",
                    description="Download a file from Google Drive to local storage. Google Workspace files (Docs, Sheets, Slides) are automatically exported to appropriate formats (markdown, CSV, text).",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_id": {
                                "type": "string",
                                "description": "Google Drive file ID or full URL"
                            }
                        },
                        "required": ["file_id"]
                    }
                ),
                Tool(
                    name="read_downloaded_file",
                    description="Read the contents of a previously downloaded file from local storage.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "Name of the downloaded file to read"
                            },
                            "max_chars": {
                                "type": "integer",
                                "description": "Maximum number of characters to return (default: 50000)",
                                "default": 50000
                            }
                        },
                        "required": ["filename"]
                    }
                ),
                Tool(
                    name="search_drive_files",
                    description="Search for files in Google Drive by name or content. Returns matching files with their metadata.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query string"
                            },
                            "max_results": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 50)",
                                "default": 50
                            }
                        },
                        "required": ["query"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """Handle tool execution requests."""
            try:
                client = self._get_client()

                if name == "list_drive_files":
                    folder_id = arguments.get("folder_id")
                    max_results = arguments.get("max_results", 100)
                    files = client.list_files(folder_id=folder_id, max_results=max_results)

                    if not files:
                        return [TextContent(
                            type="text",
                            text="No files found in Google Drive."
                        )]

                    result = f"Found {len(files)} files:\n\n"
                    for file in files:
                        mime_type = file['mimeType']
                        file_type = mime_type.split('.')[-1] if '.' in mime_type else mime_type
                        size = file.get('size', 'N/A')
                        modified = file.get('modifiedTime', 'Unknown')
                        result += f"• {file['name']}\n"
                        result += f"  ID: {file['id']}\n"
                        result += f"  Type: {file_type}\n"
                        result += f"  Size: {size}\n"
                        result += f"  Modified: {modified}\n\n"

                    return [TextContent(type="text", text=result)]

                elif name == "get_file_info":
                    file_id = client.extract_file_id(arguments["file_id"])
                    file_info = client.get_file_info(file_id)

                    if not file_info:
                        return [TextContent(
                            type="text",
                            text=f"Could not retrieve information for file ID: {file_id}"
                        )]

                    result = f"File Information:\n"
                    result += f"Name: {file_info['name']}\n"
                    result += f"ID: {file_info['id']}\n"
                    result += f"Type: {file_info['mimeType']}\n"
                    result += f"Size: {file_info.get('size', 'N/A')}\n"
                    result += f"Modified: {file_info.get('modifiedTime', 'Unknown')}\n"

                    return [TextContent(type="text", text=result)]

                elif name == "download_drive_file":
                    file_id = client.extract_file_id(arguments["file_id"])
                    success, file_info = client.download_file(file_id)

                    if success:
                        result = f"Successfully downloaded: {file_info['name']}\n"
                        result += f"File saved to: {client.output_dir}/{file_info['name']}\n"
                        result += f"You can now read this file using the read_downloaded_file tool."
                        return [TextContent(type="text", text=result)]
                    else:
                        return [TextContent(
                            type="text",
                            text=f"Failed to download file ID: {file_id}"
                        )]

                elif name == "read_downloaded_file":
                    filename = arguments["filename"]
                    max_chars = arguments.get("max_chars", 50000)
                    file_path = client.output_dir / filename

                    if not file_path.exists():
                        return [TextContent(
                            type="text",
                            text=f"File not found: {filename}. Please download it first using download_drive_file."
                        )]

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read(max_chars)

                        if len(content) == max_chars:
                            content += f"\n\n[Content truncated at {max_chars} characters]"

                        result = f"Content of {filename}:\n\n{content}"
                        return [TextContent(type="text", text=result)]
                    except UnicodeDecodeError:
                        return [TextContent(
                            type="text",
                            text=f"File {filename} appears to be binary and cannot be read as text."
                        )]

                elif name == "search_drive_files":
                    query = arguments["query"]
                    max_results = arguments.get("max_results", 50)

                    # Use Drive API search
                    files = client.list_files(max_results=max_results)

                    # Filter files by query (simple name matching)
                    matching_files = [
                        f for f in files
                        if query.lower() in f['name'].lower()
                    ]

                    if not matching_files:
                        return [TextContent(
                            type="text",
                            text=f"No files found matching query: {query}"
                        )]

                    result = f"Found {len(matching_files)} files matching '{query}':\n\n"
                    for file in matching_files:
                        result += f"• {file['name']} (ID: {file['id']})\n"
                        result += f"  Type: {file['mimeType'].split('.')[-1]}\n"
                        result += f"  Modified: {file.get('modifiedTime', 'Unknown')}\n\n"

                    return [TextContent(type="text", text=result)]

                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]

            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point."""
    import asyncio
    server = DriveMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
