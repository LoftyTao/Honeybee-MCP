from tools.mcp_context import mcp

import tools

if __name__ == "__main__":
    # Start the MCP server
    # This will listen for incoming MCP connections and handle tool requests
    mcp.run()