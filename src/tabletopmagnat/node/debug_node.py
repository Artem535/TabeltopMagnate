from icecream import ic
from langfuse import get_client, observe
from pocketflow import AsyncNode


class DebugNode(AsyncNode):
    def __init__(self, name: str):
        super().__init__()
        self._name = name
        self._lf_client = get_client()

    @observe(as_type="chain")
    async def prep_async(self, shared):
        name = f"{self._name}:prep"
        self._lf_client.update_current_span(name=name)
        ic("DebugNode:prep_async|", shared)
        return shared

    @observe(as_type="chain")
    async def run_async(self, shared):
        name = f"{self._name}:run"
        self._lf_client.update_current_span(name=name)
        ic("DebugNode:run_async|", shared)
        return None

    @observe(as_type="chain")
    async def post_async(self, shared, prep_res, exec_res):
        name = f"{self._name}:post"
        self._lf_client.update_current_span(name=name)
        ic("DebugNode:post_async|", shared, prep_res, exec_res)
        return "default"
