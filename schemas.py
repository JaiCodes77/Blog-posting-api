# schemas.py
# Responsible for:
#   - Defining the shape of data going IN (requests) and OUT (responses) via the API
#   - These are Pydantic models — separate from the SQLAlchemy models in models.py
#   - FastAPI uses these for automatic validation and documentation
#
# Naming convention used here:
#   - <Model>Create  → data the client sends when creating something
#   - <Model>Update  → data the client sends when updating something
#   - <Model>Out     → data the API sends back to the client

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# User Schemas
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    """Used when a new user registers. Client sends this."""
    username: str
    email: EmailStr
    password: str  # plain text — you will hash this in your route logic

    # TODO: Add any extra fields you want users to provide at signup
    # For example: bio: Optional[str] = None


class UserOut(BaseModel):
    """Returned to the client after creating or fetching a user."""
    id: int
    username: str
    email: str
    created_at: datetime

    # This tells Pydantic to read data from SQLAlchemy model attributes
    model_config = {"from_attributes": True}

    # TODO: Add more fields here if you add them to the User model
    # Never expose hashed_password in a response schema


# ---------------------------------------------------------------------------
# Token Schemas (for login / JWT)
# ---------------------------------------------------------------------------

class Token(BaseModel):
    """Returned to the client after a successful login."""
    access_token: str
    token_type: str  # will always be "bearer"


class TokenData(BaseModel):
    """Used internally to hold the data decoded from a JWT token."""
    username: Optional[str] = None

    # TODO: You can add more claims here later, like user_id or role


# ---------------------------------------------------------------------------
# Post Schemas
# ---------------------------------------------------------------------------

class PostCreate(BaseModel):
    """Used when a user creates a new blog post. Client sends this."""
    title: str
    content: str

    # TODO: Add optional fields if needed, e.g.:
    # tags: Optional[str] = None


class PostUpdate(BaseModel):
    """Used when a user updates an existing post. All fields are optional."""
    title: Optional[str] = None
    content: Optional[str] = None

    # TODO: Add any other fields the user should be allowed to update


class PostOut(BaseModel):
    """Returned to the client when fetching one or many posts."""
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    # TODO: You could nest the author's info here instead of just author_id
    # For example: author: UserOut
    # That would require adding a relationship in the Post model and loading it
