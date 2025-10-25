from pydantic import BaseModel, Field

from tabletopmagnat.types.dialog import Dialog


class PrivateState(BaseModel):
    dialog: Dialog = Field(default=Dialog())
