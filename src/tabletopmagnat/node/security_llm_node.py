from typing import override

from langfuse import observe

from tabletopmagnat.node.llm_node import LLMNode
from tabletopmagnat.types.messages import SystemMessage


class SecurityNode(LLMNode):
    @override
    @observe(name="Security:get_prompt", as_type="guardrail")
    def get_prompt(self) -> SystemMessage:
        prompt = self.lf_client.get_prompt("security")
        return SystemMessage(content=prompt.prompt)
