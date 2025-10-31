from typing import override

from icecream import ic
from langfuse import observe

from tabletopmagnat.node.llm_node import LLMNode
from tabletopmagnat.types.messages import DeveloperMessage, SystemMessage


class AssistantNode(LLMNode):
    @override
    @observe(name="AssistantLLM:get_prompt")
    def get_prompt(self) -> DeveloperMessage:
        prompt = self.lf_client.get_prompt("main")
        return SystemMessage(content=prompt.prompt)
