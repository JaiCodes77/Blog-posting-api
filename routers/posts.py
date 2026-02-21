# routers/posts.py
# Responsible for:
#   - All blog post CRUD operations
#   - All routes here require the user to be authenticated (logged in)
#
# Routes:
#   GET    /posts        → list all posts
#   GET    /posts/{id}   → get a single post
#   POST   /posts        → create a new post
#   PUT    /posts/{id}   → update a post (only the author can do this)
#   DELETE /posts/{id}   → delete a post (only the author can do this)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas import PostCreate, PostUpdate, PostOut
from auth import get_current_user
import models

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


# ---------------------------------------------------------------------------
# GET /posts — list all posts
# ---------------------------------------------------------------------------
@router.get("/", response_model=List[PostOut])
def get_all_posts(db: Session = Depends(get_db)):
    """
    Returns a list of all blog posts. No authentication required.

    What you need to implement:
    1. Query the database for all posts using db.query(models.Post).all()
    2. Return the list (FastAPI will serialize each post using PostOut)

    TODO: Later you could add filtering, pagination, or sorting here.
    """
    # TODO: Query all posts and return them
    pass


# ---------------------------------------------------------------------------
# GET /posts/{post_id} — get a single post
# ---------------------------------------------------------------------------
@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """
    Returns a single post by its ID.

    What you need to implement:
    1. Query the db for a Post where Post.id == post_id
    2. If no post is found, raise HTTPException with status 404
    3. Return the post
    """
    # TODO: Query for the post by id
    # post = db.query(models.Post).filter(models.Post.id == post_id).first()
    # if not post:
    #     raise HTTPException(status_code=404, detail="Post not found")
    # return post
    pass


# ---------------------------------------------------------------------------
# POST /posts — create a new post
# ---------------------------------------------------------------------------
@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Creates a new blog post. The logged-in user becomes the author.

    What you need to implement:
    1. Create a new models.Post using post_data and current_user.id as author_id
    2. Add it to db, commit, and refresh
    3. Return the new post
    """
    # TODO: Create the post
    # new_post = models.Post(
    #     title=post_data.title,
    #     content=post_data.content,
    #     author_id=current_user.id
    # )
    # db.add(new_post)
    # db.commit()
    # db.refresh(new_post)
    # return new_post
    pass


# ---------------------------------------------------------------------------
# PUT /posts/{post_id} — update a post
# ---------------------------------------------------------------------------
@router.put("/{post_id}", response_model=PostOut)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Updates an existing post. Only the author of the post can do this.

    What you need to implement:
    1. Fetch the post by post_id — raise 404 if not found
    2. Check that post.author_id == current_user.id — raise 403 if not
    3. Update only the fields that were provided (check for None before updating)
    4. Commit and refresh, then return the updated post

    Hint for step 3 — only update fields that are not None:
        if post_data.title is not None:
            post.title = post_data.title
    """
    # TODO: Fetch the post
    # TODO: Ownership check
    # TODO: Apply updates
    # TODO: Commit and return
    pass


# ---------------------------------------------------------------------------
# DELETE /posts/{post_id} — delete a post
# ---------------------------------------------------------------------------
@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Deletes a post. Only the author of the post can do this.

    What you need to implement:
    1. Fetch the post by post_id — raise 404 if not found
    2. Check ownership — raise 403 if current_user is not the author
    3. Delete the post: db.delete(post)
    4. Commit the transaction
    5. Return nothing (204 No Content means no response body)
    """
    # TODO: Fetch the post
    # TODO: Ownership check
    # TODO: Delete and commit
    pass
