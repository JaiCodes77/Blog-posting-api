# routers/auth.py
# Responsible for:
#   - POST /auth/register → create a new user account
#   - POST /auth/login    → verify credentials and return a JWT token

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from schemas import UserCreate, UserOut, Token
import models
import auth as auth_utils

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],  # groups these routes together in the /docs page
)


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user.

    What you need to implement:
    1. Check if a user with the same email or username already exists in the db.
       If so, raise an HTTPException with status 400 and a clear error message.
    2. Hash the plain-text password from user_data.password using auth_utils.hash_password().
    3. Create a new models.User object with the provided data and the hashed password.
    4. Add it to the db session, commit, and refresh it.
    5. Return the new user (Pydantic will convert it to UserOut automatically).
    """
    # TODO: Check for existing user by email
    # existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    # if existing:
    #     raise HTTPException(status_code=400, detail="Email already registered")

    # TODO: Hash the password
    # hashed_pw = auth_utils.hash_password(user_data.password)

    # TODO: Create a new User model instance
    # new_user = models.User(
    #     username=user_data.username,
    #     email=user_data.email,
    #     hashed_password=hashed_pw
    # )

    # TODO: Save to database
    # db.add(new_user)
    # db.commit()
    # db.refresh(new_user)

    # TODO: Return the new user
    pass


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Logs in a user and returns a JWT access token.

    Note: OAuth2PasswordRequestForm expects form fields: username and password
    (not JSON). This matches the OAuth2 standard that FastAPI's docs page uses.

    What you need to implement:
    1. Query the database for a user with form_data.username.
    2. If no user found, raise an HTTPException with status 401.
    3. Verify the password using auth_utils.verify_password().
    4. If the password is wrong, raise an HTTPException with status 401.
    5. Create a JWT token using auth_utils.create_access_token()
       with {"sub": user.username} as the payload.
    6. Return the token in the format: {"access_token": token, "token_type": "bearer"}
    """
    # TODO: Find user by username
    # user = db.query(models.User).filter(models.User.username == form_data.username).first()
    # if not user:
    #     raise HTTPException(status_code=401, detail="Invalid credentials")

    # TODO: Verify password
    # if not auth_utils.verify_password(form_data.password, user.hashed_password):
    #     raise HTTPException(status_code=401, detail="Invalid credentials")

    # TODO: Create and return the token
    # token = auth_utils.create_access_token(data={"sub": user.username})
    # return {"access_token": token, "token_type": "bearer"}
    pass
