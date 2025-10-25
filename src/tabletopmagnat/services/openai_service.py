from langfuse.openai import OpenAI
from openai.types.chat import ChatCompletion

from tabletopmagnat.config.openai_config import OpenAIConfig
from tabletopmagnat.types.dialog import Dialog
from tabletopmagnat.types.messages import AiMessage


class OpenAIService:
    def __init__(self, model_config: OpenAIConfig):
        self.model: str = model_config.model
        self.tools = []
        self.client = OpenAI(
            api_key=model_config.api_key,
            base_url=model_config.base_url,
        )

    def add_mcp_tool(self, tool):
        raise NotImplementedError()

    def generate(self, dialog: Dialog) -> AiMessage:
        response: ChatCompletion = self.client.chat.completions.create(
            messages=dialog.to_list(), model=self.model
        )
        content = response.choices[0].message.content
        content = "" if content is None else content.strip()

        response_msg = AiMessage(content=content)
        return response_msg
