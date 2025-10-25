from langfuse import Langfuse
from uuid import uuid4
from tabletopmagnat.config.config import Config
from tabletopmagnat.node.task_classifier import TaskClassifier
from tabletopmagnat.services.openai_service import OpenAIService
from tabletopmagnat.state.private_state import PrivateState
from tabletopmagnat.types.messages import UserMessage


class Application():
    def __init__(self):
        self.config = Config()
        self.langfuse = Langfuse(
            host=self.config.langfuse.host,
            public_key=self.config.langfuse.public_key,
            secret_key=self.config.langfuse.secret_key,
        )
        # Service
        self.llm = OpenAIService(self.config.openai)

        # Nodes
        self.task_classifier = TaskClassifier(self.llm, 1, 0)

        # Data
        self.shared_data = PrivateState()

    def run(self):
        with self.langfuse.start_as_current_span(name=f"Span:{uuid4()}") as span:
            span.update(input="Привет!")
            self.shared_data.dialog.add_message(UserMessage(content="Привет!"))
            self.task_classifier.run(self.shared_data)
