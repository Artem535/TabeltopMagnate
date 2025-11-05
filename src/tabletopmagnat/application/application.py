from uuid import uuid4

from langfuse import Langfuse
from pocketflow import AsyncFlow

from tabletopmagnat.config.config import Config
from tabletopmagnat.node.assistant_node import AssistantNode
from tabletopmagnat.node.debug_node import DebugNode
from tabletopmagnat.node.docling_node import DoclingNode
from tabletopmagnat.node.echo_node import EchoNode
from tabletopmagnat.node.mcp_tool_node import MCPToolNode
from tabletopmagnat.node.security_llm_node import SecurityNode
from tabletopmagnat.node.summary_node import SummaryNode
from tabletopmagnat.node.task_classifier_node import TaskClassifier
from tabletopmagnat.services.openai_service import OpenAIService
from tabletopmagnat.structured_output.task_classifier import TaskClassifierOutput
from tabletopmagnat.types.dialog import Dialog
from tabletopmagnat.types.messages import UserMessage
from tabletopmagnat.types.tool import ToolHeader
from tabletopmagnat.types.tool.mcp import MCPServer, MCPServers, MCPTools


class Application:
    """Main application class that orchestrates nodes and tools to process user input using LLM and external APIs.

    Attributes:
        config (Config): Configuration object loaded from the application's config module.
        langfuse (Langfuse): Langfuse client for observability and tracing.
        llm (OpenAIService): Language model service used for message generation.
        task_classifier (TaskClassifier | None): Node responsible for classifying tasks based on input.
        tool_node (MCPToolNode | None): Node responsible for invoking external tools.
        debug_node (DebugNode | None): Final node for logging or debugging output.
        flow (AsyncFlow | None): Asynchronous workflow composed of connected nodes.
        shared_data (dict[str, Any]): Shared context between nodes, containing the dialog history.
    """

    def __init__(self) -> None:
        """Initialize the Application with configuration, services, and placeholder nodes."""
        self.config = Config()
        self.langfuse = Langfuse(
            host=self.config.langfuse.host,
            public_key=self.config.langfuse.public_key,
            secret_key=self.config.langfuse.secret_key,
        )

        # Service
        self.assistant_llm = OpenAIService(
            self.config.openai.assistant_model, self.config.openai
        )
        self.task_classifier_llm = OpenAIService(
            self.config.openai.general_model, self.config.openai
        )
        self.security_llm = OpenAIService(
            self.config.openai.security_model, self.config.openai
        )

        # Nodes
        self.assistant_node: AssistantNode | None = None
        self.task_classifier: TaskClassifier | None = None
        # self.tool_node: MCPToolNode | None = None
        self.debug_node: DebugNode | None = None
        self.security_node: SecurityNode | None = None
        self.summary_node1: SummaryNode | None = None
        self.summary_node2: SummaryNode | None = None
        self.summary_node3: SummaryNode | None = None
        self.docling_node: DoclingNode | None = None
        self.echo_node: EchoNode | None = None

        # Flow
        self.flow: AsyncFlow | None = None

        # Data
        self.shared_data = {"dialog": Dialog()}

    async def init_nodes(self):
        """Initialize application nodes if they have not been created yet.

        This method lazily initializes the `task_classifier`, `tool_node`, and `final_node` by calling their respective
        factory methods. Each node is initialized only once.
        """
        if self.assistant_node is None:
            self.assistant_node = AssistantNode("assistant", self.assistant_llm)

        if self.task_classifier is None:
            self.task_classifier_llm.bind_structured(TaskClassifierOutput)
            self.task_classifier = await self.get_task_classifier_node(
                self.task_classifier_llm
            )

        # if self.tool_node is None:
        #     self.tool_node = await self.get_tool_node()

        if self.debug_node is None:
            self.debug_node = DebugNode()

        if self.security_node is None:
            self.security_node = SecurityNode("security", self.security_llm)

        if self.summary_node1 is None:
            self.summary_node1 = SummaryNode("SummaryNode1")

        if self.summary_node2 is None:
            self.summary_node2 = SummaryNode("SummaryNode2")

        if self.summary_node3 is None:
            self.summary_node3 = SummaryNode("SummaryNode3")

        if self.echo_node is None:
            self.echo_node = EchoNode("EchoNode")

        if self.docling_node is None:
            self.docling_node = DoclingNode("DoclingNode")

    def get_tools(self):
        """Construct and return a set of external tools (e.g., MCP API).

        Returns:
            MCPTools: A collection of external tools configured for use in the application.
        """
        header = ToolHeader(Authorization="Bearer 1234567890")
        server = MCPServer(
            transport="http",
            url="http://localhost:8000/mcp",
            headers=header,
            auth="bearer",
        )
        mcp_servers = MCPServers(mcpServers={"mcp": server})
        return MCPTools(mcp_servers)

    async def get_task_classifier_node(self, llm: OpenAIService):
        """Create and configure a TaskClassifier node.

        Args:
            llm (OpenAIService): The language model service used by the classifier.

        Returns:
            TaskClassifier: A configured task classifier node bound to available tools.
        """
        # tools = self.get_tools()
        task_classifier = TaskClassifier("task_classifier", llm, 1, 0)
        # task_classifier.bind_tools(await tools.get_openai_tools())
        return task_classifier

    async def get_tool_node(self):
        """Create and configure a ToolNode.

        Returns:
            MCPToolNode: A configured tool node ready to invoke external tools.
        """
        tools = self.get_tools()
        _ = await tools.get_openai_tools()
        return MCPToolNode(tools, name="tool")

    def connect_nodes(self):
        """Connect the nodes into a workflow.

        This method defines the data flow between the task classifier, tool node, and final debug node.
        """
        (
            self.task_classifier - "search"
            >> self.summary_node1
            >> self.echo_node
            >> self.summary_node2
            >> self.security_node
            >> self.summary_node3
            >> self.assistant_node
        )

        (
            self.task_classifier - "adding"
            >> self.docling_node
            >> self.debug_node
        )
        # self.task_classifier - "search" >> self.debug_node

    async def init_flow(self):
        """Initialize the workflow by setting up nodes and connecting them.

        This method ensures all necessary nodes are initialized and then connects them into an `AsyncFlow`.
        """
        await self.init_nodes()
        self.connect_nodes()
        self.flow = AsyncFlow(start=self.task_classifier)

    async def run(self):
        """Run the application workflow with a sample user message.

        This method adds a user message to the dialog, initializes the workflow if it hasn't been created yet,
        and executes the workflow asynchronously. It also logs the input and output using Langfuse.
        """
        msg = "Добавь игру Ticket To Ride: https://hobbyworld.ru/download/rules/Exploding%20Kittens_Rules.pdf"

        dialog = self.shared_data["dialog"]
        dialog.add_message(UserMessage(content=msg))

        if self.flow is None:
            await self.init_flow()

        with self.langfuse.start_as_current_span(name=f"Span:{uuid4()}") as span:
            span.update(input=dialog)

            await self.flow.run_async(shared=self.shared_data)

            dialog.get_last_message()
            span.update(output=dialog.get_last_message())
