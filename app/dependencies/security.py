from datetime import datetime, timedelta
from typing import Annotated
#import aioredis
#import asyncio
import google_auth_oauthlib.flow

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from .database import users_collection
from ..config import SECRET_KEY, ALGORITHM
from ..models.token import TokenData
from ..serializers.userSerializers import userEntity, userEntityGoogle, userResponseEntity

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

"""async def redis_connection():
    redis = aioredis.from_url("redis://localhost")
    await redis.set("my-key", "value")
    value = await redis.get("my-key")
    print(value)"""

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# helper functions for passwords, users, and tokens
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# pwd_context already generates a salt
def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(email: str):
    result = users_collection.find_one({"email": email})
    if result != None:
        return result
    
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
    user = userResponseEntity(get_user(email=token_data.email))
    if user is None:
        raise credentials_exception
    return user


# token blacklist functions using Redis
"""async def revoke_token(token: str):
    redis = await get_redis_pool()
    await redis.set(token, "revoked")

async def is_token_revoked(token: str):
    redis = await get_redis_pool()
    result = await redis.get(token)
    return result is not None"""