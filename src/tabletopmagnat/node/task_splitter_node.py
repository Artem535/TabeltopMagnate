from typing import override

from langfuse import observe

from tabletopmagnat.node.llm_node import LLMNode
from tabletopmagnat.state.private_state import PrivateState
from tabletopmagnat.types.messages import AiMessage, SystemMessage, UserMessage


class TaskSplitterNode(LLMNode):
    @override
    @observe(as_type="chain")
    def get_prompt(self) -> SystemMessage:
        name = f"{self._name}:get_prompt"
        self._lf_client.update_current_span(name=name)

        prompt = self._lf_client.get_prompt("task_splitter")
        return SystemMessage(content=prompt.prompt)

    @override
    async def post_async(self, shared: PrivateState, prep_res, exec_res: AiMessage):
        assert "task_for_expert1" in exec_res.metadata, "No task for expert1 found"
        msg = f"Here is your task: {exec_res.metadata['task_for_expert1']}"
        msg += "\n---\n Always use tools to get information for task."
        shared.expert_1.add_message(UserMessage(content=msg))

        return "default"
