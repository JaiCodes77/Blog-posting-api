# models.py
# Responsible for:
#   - Defining the shape of your database tables using SQLAlchemy ORM
#   - Each class here maps to one table in the SQLite database
#
# After adding or changing models, you need to call Base.metadata.create_all()
# in main.py to apply those changes to the database file.

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


# ---------------------------------------------------------------------------
# User model — maps to the "users" table
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship: one user can have many posts
    # After defining the Post model below, SQLAlchemy will link them automatically.
    posts = relationship("Post", back_populates="author")

    # TODO: You can add more fields later, for example:
    #   - is_active (Boolean) to allow banning users
    #   - bio (Text) for a user profile description


# ---------------------------------------------------------------------------
# Post model — maps to the "posts" table
# ---------------------------------------------------------------------------
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Foreign key: each post belongs to one user
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship: gives you access to post.author (returns the User object)
    author = relationship("User", back_populates="posts")

