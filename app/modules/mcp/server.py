# app/modules/mcp/server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Dezh", stateless_http=True)

@mcp.tool()
async def ping() -> str:
    """Check if Dezh MCP server is alive."""
    return "pong from Dezh"

def register_tools():
    """ثبت toolها. در startup صدا زده می‌شود."""
    # اینجا toolهای دیگر را import کن
    pass