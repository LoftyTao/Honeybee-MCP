from tools.mcp_context import mcp

import tools
from tools.version_tools import register_version_tools

if __name__ == "__main__":
    register_version_tools(mcp)
    mcp.run()