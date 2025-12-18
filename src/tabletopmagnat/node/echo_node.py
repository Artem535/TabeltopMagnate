from typing import override

from langfuse import observe

from tabletopmagnat.node.abstract_node import AbstractNode
from tabletopmagnat.state.private_state import PrivateState
from tabletopmagnat.types.dialog import Dialog
from tabletopmagnat.types.messages import AiMessage


class EchoNode(AbstractNode):
    def __init__(self, name: str, echo_text: str, max_retries=10, wait: int | float = 10):
        super().__init__(name, max_retries, wait)
        self._echo_text = echo_text

    @observe(as_type="chain")
    async def prep_async(self, shared: PrivateState):
        name = f"{self._name}:prep"
        self._lf_client.update_current_span(name=name)
        return None

    @observe(as_type="chain")
    async def exec_async(self, prep_res):
        name = f"{self._name}:exec"
        self._lf_client.update_current_span(name=name)
        return AiMessage(content=self._echo_text)

    @observe(as_type="chain")
    async def post_async(self, shared: PrivateState, prep_res, exec_res):
        name = f"{self._name}:post"
        self._lf_client.update_current_span(name=name)
        shared.dialog.add_message(exec_res)
        return "default"
