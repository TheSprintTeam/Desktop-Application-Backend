from typing import Annotated
import google_auth_oauthlib.flow

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from bson import ObjectId

from .database import find_one_data
from ..config import SECRET_KEY, ALGORITHM
from ..helpers.user_helpers import get_user
from ..helpers.team_helpers import get_all_user_teams
from ..models.user import UserBase
from ..models.token import TokenData, OAuth2PasswordBearerCookie
from ..serializers.userSerializers import userResponseEntity
from ..serializers.teamSerializers import teamEntity

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

# dependency to get the current user and checks token
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

# dependency to check if user is unverfied
async def user_unverified(current_user: Annotated[UserBase, Depends(get_current_user)]):
    if current_user["verified"] is True:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is already verified.",
        )
    return current_user

# dependency to check if a user is in a team given a team_id
async def is_user_in_team(team_id, current_user: Annotated[UserBase, Depends(get_current_user)]):
    user_id = current_user["id"]
    check = find_one_data("teams", {"_id": ObjectId(team_id)})
    if check is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There is no team with this team ID.",
        )
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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not in this team team",
        )
    return result

# dependency that checks if user is a team lead or co lead for team
async def user_has_perms(team_id, current_user: Annotated[UserBase, Depends(get_current_user)]):
    user_id = current_user["id"]
    result = find_one_data("teams",
        {"$and": [
            {"_id": ObjectId(team_id)},
            {"$or": [
                {"team_lead": ObjectId(user_id)},
                {"$and": [
                    {"members.user_id": ObjectId(user_id)},
                    {"members.role": ObjectId("649e1e7e45463b7a2cd13e0d")}
                ]}
            ]}
        ]})
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not have high enough permissions.",
        )
    return teamEntity(result)

# dependency that get's all of the user's teams
async def get_user_teams(current_user: Annotated[UserBase, Depends(get_current_user)]):
    user_id = current_user["id"]
    teams = get_all_user_teams(ObjectId(user_id))
    if teams is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User is not in any teams",
    )
    return teams