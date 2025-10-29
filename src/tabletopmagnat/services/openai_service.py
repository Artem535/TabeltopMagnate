from langfuse.openai import OpenAI
from openai.types.chat import (
    ChatCompletion,
)

from tabletopmagnat.config.openai_config import OpenAIConfig
from tabletopmagnat.types.dialog import Dialog
from tabletopmagnat.types.messages import AiMessage
from tabletopmagnat.types.messages.tool_message import ToolMessage
from tabletopmagnat.types.tool.openai_tool_params import OpenAIToolParams


class OpenAIService:
    def __init__(self, model_config: OpenAIConfig) -> None:
        self.tools: list[OpenAIToolParams] = []
        self.model: str = model_config.model
        self.client = OpenAI(
            api_key=model_config.api_key,
            base_url=model_config.base_url,
        )

    def add_mcp_tool(self, tool: OpenAIToolParams) -> None:
        if tool not in self.tools:
            self.tools.append(tool)

    def add_mcp_tools(self, tools: list[OpenAIToolParams]) -> None:
        tmp_tools = [tool for tool in tools if tool not in self.tools]
        self.tools.extend(tmp_tools)

    def generate(self, dialog: Dialog) -> AiMessage:
        openai_tools = [tool.model_dump(by_alias=True) for tool in self.tools]

        response: ChatCompletion = self.client.chat.completions.create(
            messages=dialog.to_list(),
            model=self.model,
            tools=openai_tools,
        )

        content = response.choices[0].message.content
        content = "" if content is None else content.strip()

        tools_openai = response.choices[0].message.tool_calls
        tools = (
            [
                ToolMessage(
                    name=tool.function.name,
                    tool_call_id=tool.id,
                    content=tool.function.arguments,
                )
                for tool in tools_openai
            ]
            if tools_openai
            else []
        )

        response_msg = AiMessage(content=content, tool_calls=tools)
        return response_msg
