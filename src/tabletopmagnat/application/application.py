from uuid import uuid4

from langfuse import Langfuse
from pocketflow import AsyncFlow

from tabletopmagnat.config.config import Config
from tabletopmagnat.node.debug_node import DebugNode
from tabletopmagnat.node.task_classifier import TaskClassifier
from tabletopmagnat.node.tool_node import ToolNode
from tabletopmagnat.services.openai_service import OpenAIService
from tabletopmagnat.types.dialog import Dialog
from tabletopmagnat.types.messages import UserMessage
from tabletopmagnat.types.tool import ToolHeader
from tabletopmagnat.types.tool.mcp import MCPServer, MCPServers, MCPTools


class Application:
    def __init__(self):
        self.config = Config()
        self.langfuse = Langfuse(
            host=self.config.langfuse.host,
            public_key=self.config.langfuse.public_key,
            secret_key=self.config.langfuse.secret_key,
        )

        # Service
        self.llm = OpenAIService(self.config.openai)

        # Nodes
        self.task_classifier = TaskClassifier(self.llm, 1, 0)

        # Data
        self.shared_data = {"dialog": Dialog()}

        header = ToolHeader(Authorization="Bearer 1234567890")
        server = MCPServer(
            transport="http",
            url="http://localhost:8000/mcp",
            headers=header,
            auth="bearer",
        )
        mcp_servers = MCPServers(mcpServers={"mcp": server})
        self.tools = MCPTools(mcp_servers)

        self.tool_node = ToolNode(self.tools)

        self.final_node = DebugNode()

    async def run(self):
        msg = "Сложи два числа через интсурмент: 0919283848, 32819384482"
        self.llm.add_mcp_tools(await self.tools.get_openai_tools())
        with (self.langfuse.start_as_current_span(name=f"Span:{uuid4()}") as span):
            span.update(input=msg)
            self.shared_data["dialog"].add_message(UserMessage(content=msg))

            self.task_classifier - "tools" >> self.tool_node
            self.task_classifier - "default" >> self.final_node
            self.tool_node >> self.task_classifier

            flow = AsyncFlow(start=self.task_classifier)

            await flow.run_async(shared=self.shared_data)
