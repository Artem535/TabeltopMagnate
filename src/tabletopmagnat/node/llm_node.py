# -*- coding: utf-8 -*-
"""LLM Node Module for TabletopMagnat.

This module provides the `LLMNode` class, an abstract base class that integrates a Language Model (LLM)
into an asynchronous processing pipeline. The node is designed to generate AI responses based on a system prompt
and a dialog history, using an LLM service such as OpenAI.

Key Features:
- Abstract class with required implementation of the system prompt.
- Integration with observability tools like Langfuse for tracking execution events.
- Uses `AsyncNode` from Pocketflow for asynchronous workflow execution.

Classes:
    LLMNode: Abstract base class for nodes utilizing a Language Model to generate AI responses.

Dependencies:
    - abc: For defining abstract base classes.
    - typing: For type annotations.
    - icecream: For debugging and logging.
    - langfuse: For observability and tracing.
    - pocketflow: For async node execution.
    - tabletopmagnat.services.openai_service: For interacting with the LLM service.
    - tabletopmagnat.types.dialog: For handling dialog data structures.
    - tabletopmagnat.types.messages: For message types used in dialog processing.
"""

from abc import ABC, abstractmethod
from typing import Any, override

from icecream import ic
from langfuse import Langfuse, get_client, observe  # type: ignore
from pocketflow import AsyncNode  # type: ignore

from tabletopmagnat.services.openai_service import OpenAIService
from tabletopmagnat.types.dialog import Dialog
from tabletopmagnat.types.messages import (
    AiMessage,
    SystemMessage,
)
from tabletopmagnat.types.tool.openai_tool_params import OpenAIToolParams


class LLMNode(AsyncNode, ABC):
    """Abstract base class for nodes that utilize a Language Model (LLM) to generate AI responses.

    This class inherits from `AsyncNode` and is designed to be extended by specific implementations
    that define the system prompt. It uses an LLM service to process dialog input and produce AI messages.

    Attributes:
        llm (OpenAIService): The language model service used for message generation.
        lf_client (Langfuse): Client for tracking observability events using Langfuse.
    """

    def __init__(
        self, llm_service: OpenAIService, max_retries=10, wait: int | float = 10
    ):
        """Initialize the LLMNode with an LLM service and optional retry settings.

        Args:
            llm_service (OpenAIService): The service used to interact with the LLM.
            max_retries (int, optional): Maximum number of retries on failure. Defaults to 10.
            wait (int | float, optional): Wait time between retries in seconds. Defaults to 10.
        """
        super().__init__(max_retries=max_retries, wait=wait)
        self.llm = llm_service
        self.lf_client: Langfuse = get_client()

    def bind_tools(self, tools: list[OpenAIToolParams]):
        self.llm.add_mcp_tools(tools)

    @abstractmethod
    @observe(name="llm_node:prompt")
    def get_prompt(self) -> SystemMessage:
        """Abstract method to retrieve the system prompt for the LLM.

        Must be implemented by subclasses to return a `SystemMessage` instance that defines
        the context or instructions for the LLM.

        Returns:
            SystemMessage: The system prompt for the LLM.
        """
        raise NotImplementedError()

    @override
    @observe(name="llm_node:preparation")
    async def prep_async(self, shared: dict[str, Any]):
        """Prepares the dialog data for execution.

        Retrieves the 'dialog' key from the shared dictionary for use in the execution phase.

        Args:
            shared (dict[str, Any]): Shared context containing the dialog.

        Returns:
            Dialog: The dialog retrieved from the shared context.
        """
        return shared["dialog"]

    @override
    @observe(name="llm_node:execution")
    async def exec_async(self, prepared_prep: Dialog) -> AiMessage:
        """Generates an AI message using the LLM based on the provided dialog.

        Combines the system prompt (obtained via `get_prompt`) with the dialog data and
        sends it to the LLM service for message generation.

        Args:
            prepared_prep (Dialog): The dialog data to be processed.

        Returns:
            AiMessage: The generated AI message.
        """
        dialog = Dialog(messages=[self.get_prompt()])
        dialog += prepared_prep
        result: AiMessage = self.llm.generate(dialog)
        return result

    @override
    @observe(name="llm_node:postprocessing")
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
        ic("LLMNode:post| exec_res:", exec_res)
        msg: AiMessage = exec_res
        dialog: Dialog = shared["dialog"]
        dialog.add_message(msg)

        if msg.tool_calls:
            return "tools"

        return "default"