import os

from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Secret Key for Auth
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 # 1 day expiration token

# MongoDB Database
MONGODB_URL = os.getenv("MONGODB_URL")

# Google Login
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SWAP_TOKEN_ENDPOINT = "/swap_token"
API_LOCATION = "http://127.0.0.1:8000"

# Email Service (using Gmail)
EMAIL_SENDER = "sprintteam12@gmail.com"
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")