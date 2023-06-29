from datetime import datetime, timedelta
from typing import Annotated
import google_auth_oauthlib.flow
import math, random

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from bson import ObjectId

from .database import find_one_data, find_data
from ..config import SECRET_KEY, ALGORITHM
from ..models.token import TokenData, OAuth2PasswordBearerCookie
from ..models.user import UserBase
from ..serializers.userSerializers import userEntity, userEntityGoogle, userResponseEntity
from ..serializers.teamSerializers import teamResponseEntity

# Use the client_secret.json file to identify the application requesting authorization. The client ID (from that file) and access scopes are required.
flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    "client_secret.json",
    scopes=["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile", "openid"])

# Indicate where the API server will redirect the user after the user completes the authorization flow.
flow.redirect_uri = "http://localhost:8000/google-callback"

# Generate URL for request to Google's OAuth 2.0 server.
authorization_url, state = flow.authorization_url(
    # Enable offline access so that you can refresh an access token without
    # re-prompting the user for permission. Recommended for web server apps.
    access_type='offline',
    # Enable incremental authorization. Recommended as a best practice.
    include_granted_scopes='true')

# Create an OAuth2 scheme (username and password)
oauth2_scheme = OAuth2PasswordBearerCookie(tokenUrl="/users/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# helper functions for passwords, users, and tokens
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(email: str):
    result = find_one_data("users", {"email": email})
    if result is not None:
        return result
    return None

def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return userEntity(user)

def authenticate_user_email(email: str):
    user = get_user(email)
    if not user:
        return False
    return userEntityGoogle(user)

def change_user_pass(user: userResponseEntity, password: str):
    if not verify_password(password, user["password"]):
        return False
    return True

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    return userResponseEntity(user)


# helper functions for user/team stuff
def get_all_user_teams(user_id):
    users_teams = []

    result_team_lead = find_data("teams",
        {"$or": [
            {"team_lead": user_id},
            {"members": user_id}
        ]})
    if result_team_lead is not Exception:
        for team in result_team_lead:
            users_teams.append(teamResponseEntity(team))

    if users_teams is not None:
        return users_teams
    return None

async def is_user_in_team(team_id, current_user: Annotated[UserBase, Depends(get_current_user)]):
    user_id = current_user["id"]
    result = find_one_data("teams",
        {"$and": [
            {"_id": ObjectId(team_id)},
            {"$or": [
                {"team_lead": ObjectId(user_id)},
                {"members": ObjectId(user_id)}
            ]}
        ]})
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="User is not in this team team",
        )
    return teamResponseEntity(result)

async def get_user_teams(current_user: Annotated[UserBase, Depends(get_current_user)]):
    user_id = current_user["id"]
    teams = get_all_user_teams(ObjectId(user_id))
    if teams is None:
        raise HTTPException(
        status_code=status.HTTP_406_NOT_ACCEPTABLE,
        detail="User is not in any teams",
    )
    return teams

# helper function to generate 6 digit passcode
def generate_otp_code():
    digits = "0123456789"
    otp = ""

    for i in range(6) :
        otp += digits[math.floor(random.random() * 10)]
 
    return otp