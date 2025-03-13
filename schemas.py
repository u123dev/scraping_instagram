import datetime
from typing import List

from pydantic import BaseModel


class PostCreateSchema(BaseModel):
    post_url: str
    raw_likes: str = ""
    likes: int = 0
    comments: int = 0
    hashtags: str = ""
    description: str = ""


class PostResponseSchema(PostCreateSchema):
    id: int
    created_at: datetime.datetime

    model_config = {"from_attributes": True, }

    def __str__(self):
        return (f"Post(id={self.id} | {self.post_url} | created_at={self.created_at})"
                f"raw_likes={self.raw_likes}, likes={self.likes}, comments={self.comments}, "
                f"hashtags={self.hashtags}, description={self.description[:20]}...)")


class PostListResponseSchema(BaseModel):
    posts: List[PostResponseSchema]
    prev_page: str | None
    next_page: str | None
    total_pages: int
    total_items: int

    model_config = {"from_attributes": True, }
