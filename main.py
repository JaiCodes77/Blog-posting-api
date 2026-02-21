# main.py
# Responsible for:
#   - Creating the FastAPI app instance
#   - Registering all routers (auth, posts)
#   - Creating database tables on startup
#
# To run the server:
#   uvicorn main:app --reload
#
# Once running, visit http://127.0.0.1:8000/docs to see and test all routes.

from fastapi import FastAPI

from database import engine, Base
from routers import auth, posts

# Create all database tables defined in models.py.
# This runs once when the server starts. If the tables already exist, it skips them.
# NOTE: You must import your models before this line so SQLAlchemy knows about them.
import models  # noqa: F401 — import needed so Base knows about User and Post
Base.metadata.create_all(bind=engine)

# Create the FastAPI app
app = FastAPI(
    title="Blog Posting API",
    description="A simple blog API with user authentication and post management.",
    version="1.0.0",
)

# Register routers
# Each router handles a group of related routes.
app.include_router(auth.router)
app.include_router(posts.router)


# ---------------------------------------------------------------------------
# Root route — just a health check
# ---------------------------------------------------------------------------
@app.get("/")
def root():
    """Simple health check. Visit this to confirm the server is running."""
    return {"message": "Blog Posting API is running. Visit /docs to explore the API."}


# ---------------------------------------------------------------------------
# What to implement next:
# ---------------------------------------------------------------------------
# 1. Open auth.py and implement:
#      - hash_password()
#      - verify_password()
#      - create_access_token()
#      - get_current_user()
#
# 2. Open routers/auth.py and implement:
#      - register() route
#      - login() route
#
# 3. Open routers/posts.py and implement:
#      - get_all_posts()
#      - get_post()
#      - create_post()
#      - update_post()
#      - delete_post()
#
# Run the server with: uvicorn main:app --reload
# Then test everything at: http://127.0.0.1:8000/docs
