from pydantic import BaseModel, Field
from typing import List

from .helper import PyObjectId

class TeamBase(BaseModel):
    name: str
    description: str
    team_lead: str
    invites: dict | None = None
    members: List[PyObjectId] | None = None
    technologies: List[PyObjectId] | None = None