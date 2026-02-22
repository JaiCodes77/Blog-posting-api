from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from schemas import UserCreate, UserOut, Token
import models
from auth import hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],  
)


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_pw = hash_password(user_data.password)  # type: ignore[operator]

    new_user = models.User(
        username = user_data.username,
        email = user_data.email,
        hashed_password = hashed_pw,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

    
    

# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password): # type: ignore[operator]
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username}) # type: ignore[operator]
    return {"access_token": access_token, "token_type": "bearer"}
