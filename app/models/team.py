from pydantic import BaseModel, Field
from typing import List
from bson import ObjectId

from .helper import PyObjectId

class TeamBase(BaseModel):
    name: str
    description: str
    team_lead: PyObjectId | None = None
    invites: dict | None = None
    members: List[PyObjectId] | None = None
    technologies: List[PyObjectId] | None = None

    class Config:
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "The Sprint Team",
                "description": "put description here"
            }
        }