from datetime import timedelta, datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.encoders import jsonable_encoder

from ..config import ACCESS_TOKEN_EXPIRE_MINUTES, SWAP_TOKEN_ENDPOINT, GOOGLE_CLIENT_ID
from ..helpers.user_helpers import authenticate_user_email, create_access_token
from ..models.user import UserCreateGoogle
from ..dependencies.security import authorization_url, flow
from ..dependencies.database import users_collection
from ..serializers.userSerializers import userResponseEntity

from google.oauth2 import id_token
from google.auth.transport import requests

router = APIRouter()

"""@router.get("/google_login_client", tags=["security"])
def google_login_client():
    return HTMLResponse(google_login_javascript_client)

@router.post(f"{SWAP_TOKEN_ENDPOINT}", response_model=Token, tags=["security"])
async def swap_token(request: Request = None):
    if not request.headers.get("X-Requested-With"):
        raise HTTPException(status_code=400, detail="Incorrect headers")

    google_client_type = request.headers.get("X-Google-OAuth2-Type")

    if google_client_type == 'client':
        body_bytes = await request.body()
        auth_code = jsonable_encoder(body_bytes)

        try:
            idinfo = id_token.verify_oauth2_token(auth_code, requests.Request(), GOOGLE_CLIENT_ID)

            # Or, if multiple clients access the backend server:
            # idinfo = id_token.verify_oauth2_token(token, requests.Request())
            # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
            #     raise ValueError('Could not verify audience.')

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            # If auth request is from a G Suite domain:
            # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
            #     raise ValueError('Wrong hosted domain.')

            if idinfo['email'] and idinfo['email_verified']:
                email = idinfo.get('email')

            else:
                raise HTTPException(status_code=400, detail="Unable to validate social login")

        except:
            raise HTTPException(status_code=400, detail="Unable to validate social login")

    user = authenticate_user_email(email)
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
    print(access_token)
    return {"access_token": access_token, "token_type": "bearer"}"""

@router.get("/google-signin")
def google_signin():
    # Redirect the user to the Google Sign-In page
    return RedirectResponse(url=authorization_url)

@router.get("/google-callback")
async def google_callback(code: str):
    # Obtain access token for user sign in
    flow.fetch_token(code=code)
    credentials = flow.credentials

    # Verify the access token
    id_info = id_token.verify_oauth2_token(
        credentials.id_token, requests.Request(), GOOGLE_CLIENT_ID)
    
    # Check if external authenticator is a Google account or not
    if id_info["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong issuer.")
    
    # Check if email is provided for Google account
    if id_info["email"] and id_info["email_verified"]:
        user_email = id_info["email"]
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to validate social login.")

    # Add user to database if already doesn't exist
    user = authenticate_user_email(user_email)
    if user is None:
        user_data = UserCreateGoogle(
            email = user_email.lower(),
            first_name = id_info["name"],
            last_name = "",
            created_at = datetime.utcnow(),
            updated_at = datetime.utcnow(),
            verified = True
            # role to be done
        )

        result = users_collection.insert_one(user_data.dict())
        user = userResponseEntity(users_collection.find_one({"_id": result.inserted_id}))
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}