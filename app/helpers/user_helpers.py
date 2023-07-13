from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from ..config import SECRET_KEY, ALGORITHM
from ..dependencies.database import find_one_data
from ..serializers.userSerializers import userEntity, userEntityGoogle, userResponseEntity


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# helper function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# helper function to hash password
def get_password_hash(password):
    return pwd_context.hash(password)

# helper function to get user
def get_user(email: str):
    result = find_one_data("users", {"email": email})
    if result is not None:
        return result
    return None

# helper function to authenticate user email and pass
def authenticate_user(email: str, password: str):
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return userEntity(user)

# helper function to check if user has email
def authenticate_user_email(email: str):
    user = get_user(email)
    if not user:
        return None
    return userEntityGoogle(user)

# helper function to verify a user's password to the one in db
def change_user_pass(user: userResponseEntity, password: str):
    if not verify_password(password, user["password"]):
        return False
    return True

# helper function to create access token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt