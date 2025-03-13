from typing import List

from fastapi import Depends, Query, APIRouter, status
from sqlalchemy.orm import Session

from celery.result import AsyncResult
from celery_worker import parse_insta

from dependencies import get_db
from scrape.parser import scrape_insta
from schemas import PostResponseSchema, PostCreateSchema, PostListResponseSchema
from service import create_post, list_posts


router = APIRouter()


@router.get(
    "/posts",
    response_model=PostListResponseSchema,
    summary="Get a paginated list of posts",
    description=(
            "<h3>This endpoint retrieves a paginated list of posts from the database. <br>"
            "It can be specified : "
            "the `page` number and the number of items per page using `per_page`. <br>"
            "It can be filtered by: "
            "`hashtag` and the partial `post_url`. <br>"
            "The response includes details about the posts, total pages, and total items, "
            "along with links to the previous and next pages if applicable.</h3>"
    ),
)
def get_all_posts(
    page: int = Query(1, ge=1, description="Page number (1-based index)"),
    per_page: int = Query(10, ge=1, le=20, description="Number of items per page"),
    hashtag: str = Query(None, description="Hashtag to search for"),
    post_url: str = Query(None, description="partial URL to search for"),
    db: Session = Depends(get_db),
):
    return list_posts(db, page, per_page, hashtag, post_url)


@router.post(
    "/scrape",
    response_model=List[PostResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Scrape new posts from Insta",
    description=(
            "<h3>This endpoint allows to scrape automatically new posts to the database. </h3>"
    ),
)
def scrape_posts(db: Session = Depends(get_db)):
    return scrape_insta(db)


@router.post(
    "/add_post",
    response_model=PostResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new post manually",
    description=(
            "<h3>This endpoint allows to add manually a new post to the database. </h3>"
    ),
)
def add_post(post: PostCreateSchema, db: Session = Depends(get_db)):
    return create_post(db, post)


@router.post(
    "/background_scrape/",
    summary="Start background task to scrape new posts from insta",
    description=(
            "<h3>This endpoint starts background task to add new posts "
            "to the database. </h3>"
    ),
)
async def start_parse():
    """ Start parsing via Celery task.  """
    task = parse_insta.apply_async()
    return {"task_id": task.id, "status": "started"}


@router.get(
    "/task_status/{task_id}",
    summary="Check status of background task",
    description=(
            "<h3>This endpoint checks background task status."
            "Returns status or new posts as Result if task is completed. </h3>"
    ),
)
async def get_task_status(task_id: str):
    """ Get task status & result. """
    task = AsyncResult(task_id)

    if task.state == 'PENDING':
        return {"task_id": task.id, "status": "Task is pending"}

    if task.state == 'SUCCESS':
        return {"task_id": task.id, "status": "Task completed", "result": task.result}

    if task.state == 'FAILURE':
        return {"task_id": task.id, "status": "Task failed", "error": str(task.result)}

    return {"task_id": task.id, "status": "Unknown state"}
