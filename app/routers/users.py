from typing import Annotated
from datetime import datetime, timedelta
from bson import ObjectId

from fastapi import APIRouter, Response, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from ..config import ACCESS_TOKEN_EXPIRE_MINUTES
from ..models.token import Token
from ..models.user import UserBase, UserCreate, UserChangePass
from ..dependencies.database import delete_data, insert_data, find_data, update_data
from ..dependencies.security import get_password_hash, get_current_user, authenticate_user, create_access_token
from ..serializers.userSerializers import userResponseEntity

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
    user = find_data("users", "email", form_data.email.lower())
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
    # user_name to be done
    # ip_address to be done
    # user_password to be done
    
    # insert user into database
    result = insert_data("users", form_data.dict())
    if result is Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not insert user into database",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_result = userResponseEntity(find_data("users", "_id", result.inserted_id))
    return {"user": user_result}

# API Endpoint for logging in to an account
@router.post("/login", response_model=Token)
async def login_for_access_token(response: Response, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
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

    # set the token in a cookie
    response.set_cookie(
        key = "session_token",
        value = f"Bearer {access_token}",
        httponly = True,
        max_age = 86400,
        expires = 86400
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# API Endpoint for logging out of an account
@router.post("/logout/")
async def logout_user(response: Response):
    # delete the session_token cookie
    response.delete_cookie(key="session_token")
    return {"message": "Logged out successfully."}

# API Endpoint for getting account details
@router.get("/me")
async def read_users_me(current_user: Annotated[UserBase, Depends(get_current_user)]):
    return current_user

# API Endpoint for Changing a User's password (PUT Request)
@router.put("/change_password/")
async def change_password(form_data: UserChangePass, current_user: Annotated[UserBase, Depends(get_current_user)]):
    # first verify the user put in the correct password in database
    email = current_user["email"]
    check_password = authenticate_user(email, form_data.old_password)
    if not check_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # hash the new password and update document
    hashed_password = get_password_hash(form_data.new_password)
    result = update_data(
        {"email": email},
        { "$set": {"password": hashed_password}}
    )
    if result is Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"result": result}

# API Endpoint for Deleting a User's Account
@router.delete("/delete_user")
async def delete_user(current_user: Annotated[UserBase, Depends(get_current_user)]):
    user_id = current_user["id"]
    result = delete_data("users", "_id", ObjectId(user_id))
    if result is Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete account",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"result": result}    

# API Endpoint for Updating Account Details (PUT Request)