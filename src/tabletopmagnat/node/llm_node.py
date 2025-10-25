from logging import getLogger
from abc import ABC, abstractmethod
from typing import override

from langfuse import Langfuse, get_client, observe  # type: ignore
from pocketflow import Node  # type: ignore

from tabletopmagnat.services.openai_service import OpenAIService
from tabletopmagnat.state.private_state import PrivateState
from tabletopmagnat.types.dialog import Dialog
from tabletopmagnat.types.messages import (
    AiMessage,
    SystemMessage,
    UserMessage,
    BaseMessage,
)

logger = getLogger(__name__)

class LLMNode(Node, ABC):
    def __init__(
        self, llm_service: OpenAIService, max_retries=10, wait: int | float = 10
    ):
        super().__init__(max_retries=max_retries, wait=wait)
        self.llm = llm_service
        self.lf_client: Langfuse = get_client()

    @abstractmethod
    @observe(name="llm_node:prompt")
    def get_prompt(self) -> SystemMessage:
        raise NotImplementedError()

    @override
    @observe(name="llm_node:preparation")
    def prep(self, shared: PrivateState):
        return shared.dialog

    @override
    @observe(name="llm_node:execution")
    def exec(self, prepared_prep: Dialog) -> AiMessage:
        dialog = Dialog(messages=[self.get_prompt()])
        dialog += prepared_prep
        result: AiMessage = self.llm.generate(dialog)
        return result

    @override
    @observe(name="llm_node:postprocessing")
    def post(self, shared, prep_res, exec_res):
        logger.debug("LLMNode:post| exec_res: %s", exec_res)
        return "default"