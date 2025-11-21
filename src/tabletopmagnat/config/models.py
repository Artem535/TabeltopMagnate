from pydantic_settings import BaseSettings

class Models(BaseSettings):
    security_model: str = "gpt-oss:latest"
    general_model: str = "gpt-oss:latest"
    rags_model: str = "gpt-oss:latest"