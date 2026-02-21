# auth.py
# Responsible for:
#   - Hashing and verifying passwords (using bcrypt via passlib)
#   - Creating JWT access tokens
#   - Decoding and validating JWT tokens from incoming requests
#   - Providing a get_current_user dependency for protected routes

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
from schemas import TokenData

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# TODO: Replace this with a long random secret key before deploying.
# You can generate one by running: openssl rand -hex 32
SECRET_KEY = "your-secret-key-here"

# The algorithm used to sign JWT tokens. HS256 is the standard choice.
ALGORITHM = "HS256"

# How long a token stays valid (in minutes).
# TODO: Adjust this to fit your needs. 30 minutes is a common default.
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ---------------------------------------------------------------------------
# Password Hashing
# ---------------------------------------------------------------------------

# CryptContext handles password hashing using bcrypt.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer tells FastAPI where clients should send their token.
# The tokenUrl should match your login route.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(plain_password: str) -> str:
    """
    Takes a plain-text password and returns a hashed version.
    Store the hashed version in the database — never the plain text.

    TODO: Call this in your register route before saving the user.
    """
    # TODO: Use pwd_context to hash plain_password and return it
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if a plain-text password matches the stored hashed password.
    Returns True if they match, False otherwise.

    TODO: Call this in your login route to validate the user's credentials.
    """
    # TODO: Use pwd_context to verify and return the result
    pass


# ---------------------------------------------------------------------------
# JWT Token Creation
# ---------------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Creates a signed JWT token containing the provided data.
    The token will expire after ACCESS_TOKEN_EXPIRE_MINUTES by default.

    TODO: Call this in your login route after verifying the user's password.

    Example usage:
        token = create_access_token(data={"sub": user.username})
    """
    to_encode = data.copy()

    # TODO: Calculate the expiration time using expires_delta or the default
    # Hint: expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    # TODO: Add the expiration to to_encode under the key "exp"

    # TODO: Use jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) and return it
    pass


# ---------------------------------------------------------------------------
# JWT Token Decoding + Current User Dependency
# ---------------------------------------------------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    FastAPI dependency that reads the JWT token from the Authorization header,
    decodes it, and returns the matching User from the database.

    Use this in any route that requires the user to be logged in:
        @router.get("/posts")
        def get_posts(current_user = Depends(get_current_user)):
            ...

    TODO: Implement the full logic below.
    """
    # This is the error you'll raise if anything goes wrong with the token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # TODO: Decode the token using jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # TODO: Extract the username from payload using payload.get("sub")
        # TODO: If username is None, raise credentials_exception
        # TODO: Create a TokenData object: token_data = TokenData(username=username)
        pass
    except JWTError:
        raise credentials_exception

    # TODO: Query the database for a user where User.username == token_data.username
    # TODO: If no user found, raise credentials_exception
    # TODO: Return the user object

    pass
