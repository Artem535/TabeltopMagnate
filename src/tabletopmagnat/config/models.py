from pydantic_settings import BaseSettings

class Models(BaseSettings):
    security_model: str = "gpt-oss:latest"
    task_classification_model: str = "gpt-oss:latest"
    task_splitter_model: str = "gpt-oss:latest"
    rags_model: str = "gpt-oss:latest"