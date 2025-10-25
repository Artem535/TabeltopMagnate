from typing import override

from langfuse import observe

from tabletopmagnat.node.llm_node import LLMNode
from tabletopmagnat.types.messages import SystemMessage


class TaskClassifier(LLMNode):
    @override
    @observe(name="task_classifier:get_prompt")
    def get_prompt(self) -> SystemMessage:
        prompt = self.lf_client.get_prompt("task_classifier")
        return SystemMessage(content=prompt.prompt)
