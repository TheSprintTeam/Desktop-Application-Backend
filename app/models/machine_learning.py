from pydantic import BaseModel, Field
from typing import List
from bson import ObjectId

from .helper import PyObjectId

# base model for users
class MachineLearningBase(BaseModel):
    team_id: PyObjectId
    prompt: str
    recommendation: List | None = None

    class Config:
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "team_id": "64a23c8261ee4bd7098fa6fa",
                "prompt": "testing 123"
            }
        }