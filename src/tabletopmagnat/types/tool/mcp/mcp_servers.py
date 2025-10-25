from pydantic import BaseModel


class MCPServer(BaseModel):
    mcp_server: str