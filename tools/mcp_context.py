try:
    from fastmcp import FastMCP
except ImportError:
    class FastMCP:  # pragma: no cover - lightweight fallback for local testing
        def __init__(self, name):
            self.name = name

        def tool(self):
            def decorator(func):
                return func
            return decorator

        def run(self):
            raise RuntimeError("fastmcp is not installed in the current Python environment.")


mcp = FastMCP("Honeybee-MCP")
