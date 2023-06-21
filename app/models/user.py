from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

from .helper import PyObjectId

# base model for users
class UserBase(BaseModel):
    #id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    email: str
    first_name: str
    last_name: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    role_id: PyObjectId | None = None

    class Config:
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "email": "johndoe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "created_at": "2023-06-14T10:30:00Z",
                "updated_at": "2023-06-14T10:30:00Z",
                "role_id": "609c85460f7f781a234cdcf4"
            }
        }

# additional model for creating a user
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)