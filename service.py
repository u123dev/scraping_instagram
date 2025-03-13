from typing import List

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from fastapi import status

from models import Post
from repository import PostRepository
from schemas import PostCreateSchema, PostResponseSchema, PostListResponseSchema


def create_post(db: Session, post_data: PostCreateSchema) -> PostResponseSchema:
    """Create a new post """
    try:
        new_post = PostRepository.create_post(db, post_data)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the request.",
        )
    return PostResponseSchema.model_validate(new_post)


def list_posts(
        db: Session,
        page: int,
        per_page: int,
        hashtag: str,
        post_url: str
) -> PostListResponseSchema:
    """Paginated List all posts """

    posts, total_items = PostRepository.get_posts(db, page, per_page, hashtag, post_url)

    if not posts:
        raise HTTPException(status_code=404, detail="No posts found.")

    post_list = [PostResponseSchema.model_validate(post) for post in posts]
    total_pages = (total_items + per_page - 1) // per_page

    response = PostListResponseSchema(
        posts=post_list,
        prev_page=f"/posts/?page={page - 1}&per_page={per_page}" if page > 1 else None,
        next_page=f"/posts/?page={page + 1}&per_page={per_page}" if page < total_pages else None,
        total_pages=total_pages,
        total_items=total_items,
    )

    return response


def patch_post(db: Session, post: Post) -> None:
    """Обновляет существующий объект Post в базе данных"""
    try:
        PostRepository.save_post(db, post)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the request.",
        )
