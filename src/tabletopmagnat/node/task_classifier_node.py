from typing import override

from icecream import ic
from langfuse import observe

from tabletopmagnat.node.llm_node import LLMNode
from tabletopmagnat.types.messages import DeveloperMessage, SystemMessage


class TaskClassifier(LLMNode):
    @override
    @observe(name="TaskClassifier:get_prompt")
    def get_prompt(self) -> DeveloperMessage:
        self._lf_client.update_current_span(name=f"{self._name}:get_prompt")
        prompt = self._lf_client.get_prompt("task_classifier")
        return SystemMessage(content=prompt.prompt)

    @override
    @observe(name="TaskClassifier:post", as_type="chain")
    async def post_async(self, shared, prep_res, exec_res):
        """Handles post-processing after execution.

        Logs the AI response using `icecream`, adds the AI message to the dialog, and returns a status.

        Args:
            shared (dict[str, Any]): Shared context containing the dialog.
            prep_res (Dialog): The prepared dialog (not used here).
            exec_res (AiMessage): The AI-generated message from execution.

        Returns:
            str: A default return value ("default") indicating completion.
        """
        self._lf_client.update_current_span(name=f"{self._name}:post")

        ic("TaskClassifier:post| exec_res:", exec_res)
        msg: AiMessage = exec_res
        dialog: Dialog = shared["dialog"]

        assert "content" in msg.metadata
        msg.content = msg.metadata["content"]

        ic("TaskClassifier:post| msg:", msg)
        dialog.add_message(msg)

        return msg.metadata["task"]
