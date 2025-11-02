from abc import ABC, abstractmethod

from langfuse import get_client
from pocketflow import AsyncNode

from tabletopmagnat.types.messages import BaseMessage


class AbstractNode(AsyncNode, ABC):
    def __init__(self, name: str, max_retries=10, wait: int | float = 10):
        super().__init__(max_retries=max_retries, wait=wait)
        self._name = name
        self._lf_client = get_client()
