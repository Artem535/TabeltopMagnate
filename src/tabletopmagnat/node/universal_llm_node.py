from typing import override

from langfuse import observe

from tabletopmagnat.node.llm_node import LLMNode
from tabletopmagnat.services.openai_service import OpenAIService
from tabletopmagnat.types.messages import SystemMessage


class UniversalLLMNode(LLMNode):
    def __init__(
        self,
        name: str,
        prompt_name: str,
        llm_service: OpenAIService,
        max_retries=10,
        wait: float = 10,
    ):
        super().__init__(name, llm_service, max_retries, wait)
        self._prompt_name = prompt_name


    @override
    @observe(as_type="chain")
    def get_prompt(self) -> SystemMessage:
        name = f"{self._name}:get_prompt"
        self._lf_client.update_current_span(name=name)

        prompt = self._lf_client.get_prompt(self._prompt_name)
        return SystemMessage(content=prompt.prompt)
