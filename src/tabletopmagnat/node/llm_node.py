from abc import abstractmethod
from typing import Any

from icecream import ic
from langfuse import observe

from tabletopmagnat.node.abstract_node import AbstractNode
from tabletopmagnat.services.openai_service import OpenAIService
from tabletopmagnat.state.private_state import PrivateState
from tabletopmagnat.types.dialog import Dialog
from tabletopmagnat.types.messages import AiMessage
from tabletopmagnat.types.tool.openai_tool_params import OpenAIToolParams


class LLMNode(AbstractNode):
    def __init__(
        self,
        name: str,
        llm_service: OpenAIService,
        max_retries=10,
        wait: float = 10,
    ):
        super().__init__(name, max_retries=max_retries, wait=wait)
        self.llm = llm_service

    def bind_tools(self, tools: list[OpenAIToolParams]):
        self.llm.add_mcp_tools(tools)

    @abstractmethod
    def get_prompt(self):
        raise NotImplementedError

    # ---------- PREP ----------
    @observe(as_type="chain")
    async def prep_async(self, shared: PrivateState):
        name = f"{self._name}:prep"
        self._lf_client.update_current_span(name=name)
        return shared.dialog

    # ---------- EXEC ----------
    @observe(as_type="generation")
    async def exec_async(self, prepared_prep: Dialog) -> AiMessage:
        name = f"{self._name}:exec"
        self._lf_client.update_current_generation(name=name)

        dialog = Dialog(messages=[self.get_prompt()])
        dialog += prepared_prep
        result: AiMessage = await self.llm.generate(dialog)
        return result

    # ---------- POST ----------
    @observe(as_type="chain")
    async def post_async(self, shared, prep_res, exec_res):
        name = f"{self._name}:post"
        self._lf_client.update_current_span(name=name)

        ic("LLMNode:post | exec_res:", exec_res)
        shared.dialog.add_message(exec_res)
        if exec_res.tool_calls:
            return "tools"
        return "default"
