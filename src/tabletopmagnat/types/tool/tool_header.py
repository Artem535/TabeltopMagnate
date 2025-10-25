from pydantic import BaseModel, Field

class ToolHeader(BaseModel):
    authorization: str = Field(title="Authorization")

    def add_auth(self, token: str):
        self.authorization = f"Bearer {token}"
