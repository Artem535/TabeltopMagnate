from typing import override

from langfuse import observe

from tabletopmagnat.node.llm_node import LLMNode
from tabletopmagnat.types.messages import SystemMessage


class SecurityNode(LLMNode):
    @override
    @observe(as_type="guardrail")
    def get_prompt(self) -> SystemMessage:
        name = f"{self._name}:get_prompt"
        self._lf_client.update_current_span(name=name)

        prompt = self._lf_client.get_prompt("security")
        return SystemMessage(content=prompt.prompt)
