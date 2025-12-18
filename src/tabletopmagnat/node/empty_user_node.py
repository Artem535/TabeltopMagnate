from langfuse import get_client, observe
from pocketflow import AsyncNode
from tabletopmagnat.types.dialog import Dialog

from tabletopmagnat.types.messages import UserMessage


class EmptyUserNode(AsyncNode):
    def __init__(self, name: str):
        super().__init__()
        self._name = name
        self._lf_client = get_client()

    @observe(as_type="chain")
    async def exec_async(self, prep_res):
        name = f"{self._name}:exec"
        self._lf_client.update_current_span(name=name)
        return UserMessage(content="")

    @observe(as_type="chain")
    async def post_async(self, shared, prep_res, exec_res):
        name = f"{self._name}:post"
        self._lf_client.update_current_span(name=name)
        dialog: Dialog = shared["dialog"]
        dialog.add_message(exec_res)
        return "default"
