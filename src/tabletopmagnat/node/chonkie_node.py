"""

"""
from langfuse import observe

from chonkie import MarkdownChef, MarkdownDocument

from tabletopmagnat.node.abstract_node import AbstractNode


class ChonkieNode(AbstractNode):
    def __init__(self, name: str, max_retries=10, wait: int | float = 10):
        super().__init__(name, max_retries, wait)
        self._chef: MarkdownChef = MarkdownChef()

    @observe(as_type="chain")
    async def prep_async(self, shared):
        name = f"{self._name}:prep"
        self._lf_client.update_current_span(name=name)
        doc = shared["document"]
        return doc

    @observe(as_type="tool")
    async def exec_async(self, prep_res):
        name = f"{self._name}:exec"
        self._lf_client.update_current_span(name=name)
        document = self._chef.parse(prep_res)
        return document

    @observe(as_type="chain")
    async def post_async(self, shared, prep_res, exec_res):
        name = f"{self._name}:post"
        self._lf_client.update_current_span(name=name)
        document: MarkdownDocument = exec_res
        original_document = shared["document"]

        for chunk in document.chunks:
            chunk.text = original_document["title"]

        shared["chunks"] = exec_res
        return "default"
