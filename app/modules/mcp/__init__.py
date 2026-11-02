# app/modules/mcp/__init__.py
from framework.module import BaseModule


class MCPModule(BaseModule):
    name = "mcp"

    def register_di(self, container) -> None:
        pass

    def register_routes(self, app) -> None:
        from .server import mcp, register_tools

        register_tools()
        app.mount("/mcp", mcp.streamable_http_app())