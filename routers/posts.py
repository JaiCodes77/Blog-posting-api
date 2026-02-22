from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas import PostCreate, PostUpdate, PostOut
from auth import get_current_user  # type: ignore[import]
import models

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.get("/", response_model=List[PostOut])
def get_all_posts(db: Session = Depends(get_db)):
   return db.query(models.Post).all()


@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post


@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    new_post = models.Post(
        title=post_data.title,
        content=post_data.content,
        author_id=current_user.id,
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.put("/{post_id}", response_model=PostOut)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.author_id != current_user.id:  # type: ignore[operator]
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    if post_data.title is not None:
        post.title = post_data.title  # type: ignore[assignment]
    if post_data.content is not None:
        post.content = post_data.content  # type: ignore[assignment]
    db.commit()
    db.refresh(post)
    return post

    


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post.author_id != current_user.id:  # type: ignore[operator]
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    db.delete(post)
    db.commit()