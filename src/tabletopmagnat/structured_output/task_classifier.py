from typing import Literal

from pydantic import BaseModel, Field


class TaskClassifierOutput(BaseModel):
    task: Literal["search", "adding", "default"] = Field(
        description="The task of the user. "
        "Search -- search for tabletop inforamtion. "
        "Adding -- add new data to the rag. Can be choosen only if user provide url to pdf file. "
        "default -- if task is not clear. "
    )
    content: str = Field(
        default="empty_content",
        description="The content of the task. Can be a question or a url fro adding new data in rag.",
    )
