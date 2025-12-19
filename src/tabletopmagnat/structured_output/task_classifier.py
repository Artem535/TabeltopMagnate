from typing import Literal

from pydantic import BaseModel, Field


class TaskClassifierOutput(BaseModel):
    task: Literal["explanation", "clarification", "general"] = Field(
        description="The task of the user. "
        "explanation -- explain the **FULL** rules of the tabletop game. Explanation will be from begin to end. "
        "clarification -- ask for clarification on the rules of the tabletop game. Answer will be contains the 1-2 sentence. "
        "general -- ask for general questions that can be clarified as explanation or clarification. It can be hello-msg, goodbye-msg, or other similiar."
    )
