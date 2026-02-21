# database.py
# Responsible for:
#   - Creating the SQLite database connection
#   - Providing a reusable database session for each request
#   - Exposing a Base class that all models will inherit from

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This is the path to your local SQLite file.
# When you run the app, it will create a file called blog.db in the same folder.
DATABASE_URL = "sqlite:///./blog.db"

# Create the database engine.
# connect_args is required for SQLite to work properly with FastAPI's async threads.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal is a factory for creating new database sessions.
# Each request will get its own session and close it when done.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class for all your ORM models (User, Post, etc.)
Base = declarative_base()


# ---------------------------------------------------------------------------
# Dependency: get_db
# ---------------------------------------------------------------------------
# This function is used as a FastAPI dependency in your routes.
# It opens a database session, yields it to the route, then closes it.
#
# Usage in a route:
#   def my_route(db: Session = Depends(get_db)):
#       ...
#
# TODO: Nothing to implement here — this is ready to use as-is.
# ---------------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
