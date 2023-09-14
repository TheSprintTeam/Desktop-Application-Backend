from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId

from .helper import PyObjectId

# base model for users
class UserBase(BaseModel):
    email: str
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    user: str | None = None
    ip: str | None = None
    ssh_password: str | None = None

    class Config:
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "email": "johndoe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "created_at": "2023-06-14T10:30:00Z",
                "updated_at": "2023-06-14T10:30:00Z",
                "user": "john",
                "ip": "0.0.0.0",
                "ssh_password": "test_pass"
            }
        }

# additional model for creating a user
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    otp_code: str | None = None
    verified: bool | None = None

class UserCreateGoogle(UserBase):
    verified: bool | None = None

# model for changing password
class UserChangePass(BaseModel):
    old_password: str
    new_password: str

# model for inviting a user to a team
class UserInvite(BaseModel):
    email: str
    role_id: PyObjectId
    name: str | None = None

    class Config:
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "email": "johndoe1@example.com",
                "role_id": "649e1e3e45463b7a2cd13e0c",
                "name": "My Name"
            }
        }