import os

os.environ.setdefault("FASTMCP_CHECK_FOR_UPDATES", "off")

from tools.mcp_context import mcp

import tools

if __name__ == "__main__":
    mcp.run()
