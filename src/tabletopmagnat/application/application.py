from uuid import uuid4

from langfuse import Langfuse

from tabletopmagnat.config.config import Config
from tabletopmagnat.node.echo_node import EchoNode
from tabletopmagnat.node.security_llm_node import SecurityNode
from tabletopmagnat.node.task_classifier_node import TaskClassifierNode
from tabletopmagnat.node.task_splitter_node import TaskSplitterNode
from tabletopmagnat.pocketflow import AsyncFlow
from tabletopmagnat.services.openai_service import OpenAIService
from tabletopmagnat.state.private_state import PrivateState
from tabletopmagnat.structured_output.security import SecurityOutput
from tabletopmagnat.structured_output.task_classifier import TaskClassifierOutput
from tabletopmagnat.structured_output.task_splitter import TaskSplitterOutput
from tabletopmagnat.subgraphs.rags import RASG
from tabletopmagnat.types.messages import UserMessage
from tabletopmagnat.types.tool import ToolHeader
from tabletopmagnat.types.tool.mcp import MCPServer, MCPServers, MCPTools


class Application:
    """Main application class that orchestrates nodes and tools to process user input using LLM and external APIs.

    Attributes:
        config (Config): Configuration object loaded from the application's config module.
        langfuse (Langfuse): Langfuse client for observability and tracing.
        _llm (OpenAIService): Language model service used for message generation.
        task_classifier (TaskClassifierNode | None): Node responsible for classifying tasks based on input.
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
        self.task_splitter_llm = OpenAIService(
            self.config.models.task_splitter_model, self.config.openai
        )
        self.task_splitter_llm.bind_structured(TaskSplitterOutput)
        # ---
        self.task_classifier_llm = OpenAIService(
            self.config.models.task_classification_model, self.config.openai
        )
        self.task_classifier_llm.bind_structured(TaskClassifierOutput)
        # ---
        self.security_llm = OpenAIService(
            self.config.models.security_model, self.config.openai
        )
        self.security_llm.bind_structured(SecurityOutput)
        # ---
        # TODO: FIX TYPOS
        self.rasg_llm = OpenAIService(self.config.models.rags_model, self.config.openai)

        # Nodes
        self.security_node: SecurityNode | None = None
        self.echo_node: EchoNode | None = None
        self.task_classifier_node: TaskClassifierNode | None = None
        self.task_splitter_node: TaskSplitterNode | None = None

        self.expert_1: AsyncFlow | None = None
        self.expert_2: AsyncFlow | None = None
        self.expert_3: AsyncFlow | None = None

        # Flow
        self.flow: AsyncFlow | None = None

        # Data
        self.shared_data = PrivateState()

    async def init_nodes(self):
        """Initialize application nodes if they have not been created yet.

        This method lazily initializes the `task_classifier`, `tool_node`, and `final_node` by calling their respective
        factory methods. Each node is initialized only once.
        """
        self.security_node = SecurityNode(
            name="security",
            llm_service=self.security_llm,
            prompt_name="security",
            dialog_selector=lambda x: x.dialog,
        )

        self.echo_node = EchoNode(name="echo", echo_text="Sorry, but I can't help you.")

        self.task_splitter_node = TaskSplitterNode(
            name="task_splitter",
            llm_service=self.task_splitter_llm,
            prompt_name="task_splitter",
            dialog_selector=lambda x: x.dialog,
        )

        self.task_classifier_node = TaskClassifierNode(
            name="task_classifier",
            llm_service=self.task_classifier_llm,
            prompt_name="task_classifier",
            dialog_selector=lambda x: x.dialog,
        )

        tools = self.get_tools()
        _ = await tools.get_tool_list()
        self.expert_1 = await RASG.create_subgraph(
            name="expert_1",
            prompt_name="expert_1",
            openai_service=self.rasg_llm,
            mcp_tools=tools,
            dialog_selector=lambda x: x.expert_1,
        )

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

    def connect_nodes(self):
        """Connect the nodes into a workflow.

        This method defines the data flow between the task classifier, tool node, and final debug node.
        """
        self.security_node - "unsafe" >> self.echo_node
        self.security_node - "safe" >> self.task_classifier_node

        self.task_classifier_node - "explanation" >> self.task_splitter_node
        self.task_splitter_node >> self.expert_1

    async def init_flow(self):
        """Initialize the workflow by setting up nodes and connecting them.

        This method ensures all necessary nodes are initialized and then connects them into an `AsyncFlow`.
        """
        await self.init_nodes()
        self.connect_nodes()
        self.flow = AsyncFlow(start=self.security_node)

    async def run(self, msg=""):
        """Run the application workflow with a sample user message.

        This method adds a user message to the dialog, initializes the workflow if it hasn't been created yet,
        and executes the workflow asynchronously. It also logs the input and output using Langfuse.
        """

        self.shared_data.dialog.add_message(UserMessage(content=msg))

        if self.flow is None:
            await self.init_flow()

        with self.langfuse.start_as_current_span(name=f"Span:{uuid4()}") as span:
            span.update(input=self.shared_data.dialog)

            await self.flow.run_async(shared=self.shared_data)

            last_msg = self.shared_data.dialog.get_last_message()
            span.update(output=last_msg)
