from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from ..core.config import get_settings

cnf = get_settings()

# ? Password encryptor - argon2 is the most secure modern standard
pwd_context = CryptContext(schemes=["argon2", "pbkdf2_sha256"], deprecated="auto") 
# ? Bearer token for authentication 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT token with the provided data and an optional expiration date.
    Args:
        data (dict): Data to include in the token (e.g., {"sub": "username"})
        expires_delta (timedelta, optional): Token expiration time. The default is 15 minutes.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, cnf.security.jwt_secret, algorithm=cnf.security.algorithm)

def decode_access_token(token: str = Depends(oauth2_scheme)):
    """
    Decodes a JWT token and returns the username if it is valid. Otherwise, it throws an authentication exception.
    Args:
        token (str): JWT token to be decoded (obtained from the Authorization header)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="The token could not be validated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, cnf.security.jwt_secret, algorithms=[cnf.security.algorithm])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception


# TODO: Simulated users (you can connect it to a database later)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify the password against the hash using argon2 or pbkdf2_sha256."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a hash of the password using argon2 or pbkdf2_sha256."""
    return pwd_context.hash(password)


users_db = {
    cnf.security.auth_username: {
        "username": cnf.security.auth_username,
        "hashed_password": get_password_hash(cnf.security.auth_password),
    }
}


def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user
