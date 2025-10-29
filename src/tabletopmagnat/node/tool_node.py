import json

from icecream import ic
from pocketflow import AsyncNode

from tabletopmagnat.types.dialog import Dialog
from tabletopmagnat.types.messages import AiMessage
from tabletopmagnat.types.messages.tool_message import ToolMessage
from tabletopmagnat.types.tool.mcp import MCPTools


class ToolNode(AsyncNode):
    def __init__(self, mcp_tool: MCPTools, max_retires: int = 1, wait: float = 0):
        super().__init__(max_retires, wait)
        self._mcp_tool = mcp_tool

    async def prep_async(self, shared):
        # TODO: Add check if last_msg is not None
        last_msg: AiMessage = shared["dialog"].get_last_message()
        tool_calls: list[ToolMessage] = (
            last_msg.tool_calls if last_msg.tool_calls is not None else []
        )
        return tool_calls

    async def exec_async(self, prep_res):
        tool_calls: list[ToolMessage] = prep_res

        for tool_call in tool_calls:
            res = await self._mcp_tool.call_tool(tool_call.name, tool_call.content)
            tool_call.content = (
                res.structured_content if res.structured_content is not None else ""
            )
            tool_call.content = json.dumps(tool_call.content)
            ic("ToolNode:exec_async|", res)

        ic("ToolNode:exec_async|", tool_calls)

        return tool_calls

    async def post_async(self, shared, prep_res, exec_res):
        tool_calls: list[ToolMessage] = exec_res
        dialog: Dialog = shared["dialog"]
        if tool_calls:
            for tool_call in tool_calls:
                dialog.add_message(tool_call)

        return "default"
