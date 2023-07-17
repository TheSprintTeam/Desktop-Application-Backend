from pydantic import BaseModel, Field
from typing import List
from bson import ObjectId

from .helper import PyObjectId

# base model for the teams
class TeamBase(BaseModel):
    name: str
    description: str
    team_lead: PyObjectId | None = None
    invites: List | None = None
    members: List | None = None
    technologies: List | None = None

    class Config:
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "The Sprint Team",
                "description": "put description here",
                "invites": [],
                "members": [],
                "technologies": []
            }
        }

# model for all teams
class AllTeamBase(BaseModel):
    TeamBase: dict | None = None