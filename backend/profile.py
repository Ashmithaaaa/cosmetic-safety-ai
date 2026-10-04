from pydantic import BaseModel, Field
from typing import List


class UserProfile(BaseModel):
    skin_type: str = "normal"

    sensitive_skin: bool = False

    concerns: List[str] = Field(
        default_factory=list
    )

    allergies: List[str] = Field(
        default_factory=list
    )

    sensitivities: List[str] = Field(
        default_factory=list
    )

    skin_conditions: List[str] = Field(
        default_factory=list
    )