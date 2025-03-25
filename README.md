# Shortcut.com MCP Server

An implementation of a Model Context Protocol (MCP) server for accessing and searching tickets on Shortcut.com.

## Overview

This project implements an MCP server that allows Claude and other MCP-compatible AI assistants to interact with Shortcut.com's ticket management system. With this integration, AI assistants can:

- List and search for stories (tickets) in Shortcut
- Get detailed information about specific stories
- Create new stories
- Update existing stories
- Add comments to stories
- Retrieve workflow states and projects

## Prerequisites

- Python 3.10+
- Shortcut.com API token

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/mcp-server-shortcut.git
   cd mcp-server-shortcut
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   # Using uv (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh  # For Mac/Linux
   uv venv
   source .venv/bin/activate  # On Mac/Linux or .venv\Scripts\activate on Windows
   uv pip install -r requirements.txt
   
   # Using pip
   python -m venv venv
   source venv/bin/activate  # On Mac/Linux or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root directory with your Shortcut API token:
   ```
   SHORTCUT_API_TOKEN=your_token_here
   SERVER_PORT=5000
   SERVER_HOST=0.0.0.0
   DEBUG_MODE=True
   ```

## Running the Server

Start the MCP server using:

```bash
python -m src.server
```

## Configuring Claude Desktop

To use this MCP server with Claude Desktop:

1. Edit the Claude Desktop configuration file:
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the MCP server configuration:
   ```json
   {
     "mcpServers": {
       "shortcut": {
         "command": "python",
         "args": ["-m", "src.server"],
         "env": {
           "SHORTCUT_API_TOKEN": "your_token_here"
         }
       }
     }
   }
   ```

3. Restart Claude Desktop.

## Available MCP Capabilities

### Resources

- `shortcut://stories` - Access a list of stories
- `shortcut://story/{story_id}` - Access a specific story

### Tools

- `list_stories` - List stories with optional filtering
- `search_stories` - Search for stories using text queries
- `get_story_details` - Get detailed information about a specific story
- `create_story` - Create a new story
- `update_story` - Update an existing story
- `add_comment` - Add a comment to a story
- `list_workflow_states` - List all workflow states
- `list_projects` - List all projects

### Prompts

- `create_bug_report` - Generate a template for bug reports
- `create_feature_request` - Generate a template for feature requests

## Project Structure

- `src/` - Source code directory
  - `server.py` - Main MCP server implementation
  - `config.py` - Configuration management
  - `shortcut_client.py` - Client for the Shortcut API
  - `utils.py` - Utility functions and data models
- `requirements.txt` - Project dependencies
- `.env` - Environment variables (not tracked in git)

## Development

### Adding New Capabilities

To add a new capability to the MCP server:

1. Add any new API methods to `shortcut_client.py`
2. Define Pydantic models in `utils.py` if needed
3. Implement the MCP functionality using decorators in `server.py`:
   - Use `@mcp.resource()` for read-only resources
   - Use `@mcp.tool()` for actions that can modify data
   - Use `@mcp.prompt()` for generating templates or structured text

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)
