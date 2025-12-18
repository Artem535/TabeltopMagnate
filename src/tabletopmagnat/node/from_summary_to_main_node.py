from typing import override

from langfuse import observe

from tabletopmagnat.node.abstract_node import AbstractNode
from tabletopmagnat.state.private_state import PrivateState
from tabletopmagnat.types.dialog import Dialog
from tabletopmagnat.types.messages import AiMessage


class FromSummaryToMain(AbstractNode):
    @observe(as_type="chain")
    @override
    async def prep_async(self, shared: PrivateState):
        name = f"{self._name}:prep"
        self._lf_client.update_current_span(name=name)
        return shared.summary

    @observe(as_type="chain")
    @override
    async def exec_async(self,prep_res: Dialog):
        name = f"{self._name}:exec"
        self._lf_client.update_current_span(name=name)
        last_msg = prep_res.get_last_message()
        return last_msg

    @observe(as_type="chain")
    @override
    async def post_async(self,shared: PrivateState,prep_res:Dialog,exec_res:AiMessage):
        name = f"{self._name}:post"
        self._lf_client.update_current_span(name=name)
        shared.dialog.add_message(exec_res)
        return "default"
