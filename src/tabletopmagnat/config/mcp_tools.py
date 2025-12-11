from pydantic_settings import BaseSettings


class MCPSettings(BaseSettings):
    url: str
