from typing import Annotated
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from ..models.user import UserBase, UserCreate
from ..dependencies.database import users_collection
from ..dependencies.security import oauth2_scheme, get_password_hash, get_current_user
from ..serializers.userSerializers import userResponseEntity

from ..config import ACCESS_TOKEN_EXPIRE_MINUTES
from ..dependencies.security import authenticate_user, create_access_token

from ..models.token import Token


router = APIRouter(
    prefix="/users",
    tags=["users"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)

# API Endpoint for creating an account
@router.post("/register")
async def create_user(form_data: UserCreate):
    # check if user exists
    user = users_collection.find_one({"email": form_data.email.lower()})
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists.")

    # hash the password
    hashed_password = get_password_hash(form_data.password)

    # set user created object password to the hashed password
    form_data.password = hashed_password
    form_data.email = form_data.email.lower()
    form_data.created_at = datetime.utcnow()
    form_data.updated_at = form_data.created_at
    # role to be done
    
    # insert user into database
    result = users_collection.insert_one(form_data.dict())
    user_result = userResponseEntity(users_collection.find_one({"_id": result.inserted_id}))

    # Return the created user
    return {"user": user_result}

# API Endpoint for logging in to an account
@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # authenticate user with helper functions and dependencies
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# API Endpoint for logging out of an account
"""@router.post("/logout/")
async def logout_user(token: str = Depends(oauth2_scheme)):
    if await is_token_revoked(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided",
        )
    
    await revoke_token(token)

    return {"message": "Logged out successfully."}"""


# API Endpoint for getting account details
@router.get("/me")
async def read_users_me(current_user: Annotated[UserBase, Depends(get_current_user)]):
    return current_user
# can have thousands of endpoints using the same security system (all of them can take advantage of re-using these dependencies/any other dependencies created)
# path operations to get user: 