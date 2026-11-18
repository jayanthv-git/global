from typing import Literal
from pydantic import BaseModel, Field, StrictInt
class AssessmentInput(BaseModel):
    instrument: Literal['PHQ-9','GAD-7','WHO-5']
    responses: list[StrictInt]
    text: str = Field(default='',max_length=2000)
class CrisisInput(BaseModel):
    text: str = Field(default='',max_length=2000)
    urgent: bool = False
