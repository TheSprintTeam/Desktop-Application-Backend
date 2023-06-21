from pydantic import BaseModel, Field
from typing import List
from bson import ObjectId

from .helper import PyObjectId

class Teams(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str
    invites: dict
    members: List[ObjectId]
    technologies: List[ObjectId]