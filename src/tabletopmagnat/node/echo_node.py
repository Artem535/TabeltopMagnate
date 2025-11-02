from typing import override

from tabletopmagnat.node.abstract_node import AbstractNode
from tabletopmagnat.types.dialog import Dialog
from tabletopmagnat.types.messages import AiMessage


class EchoNode(AbstractNode):
    async def prep_async(self, shared):
        return shared

    async def exec_async(self, prep_res):
        text = self._lf_client.get_prompt("test_rules")
        return AiMessage(content=text.prompt)

    async def post_async(self, shared, prep_res, exec_res):
        dialog: Dialog = shared["dialog"]
        dialog.add_message(exec_res)

        return "default"
