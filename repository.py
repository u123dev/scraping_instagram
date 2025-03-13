from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Post
from schemas import PostCreateSchema


class PostRepository:
    @staticmethod
    def create_post(db: Session, post_data: PostCreateSchema) -> Post:
        """ Add a post to the database"""
        new_post = Post(**post_data.model_dump())
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        return new_post

    @staticmethod
    def get_posts(db: Session, page: int, per_page: int, hashtag: str, post_url: str):
        """ Get all posts"""
        offset = (page - 1) * per_page

        query = db.query(Post)
        if hashtag:
            query = query.filter(Post.hashtags.ilike(f"%{hashtag}%"))
        if post_url:
            query = query.filter(Post.post_url.ilike(f"%{post_url}%"))
        total_items = query.count()
        posts = query.offset(offset).limit(per_page).all()

        return posts, total_items

    @staticmethod
    def check_post(db: Session, post_url: str) -> bool:
        """ Check if a post exists in the database:
            Return False if it doesn't'"""
        return db.execute(select(Post).filter_by(post_url=post_url)).scalar() is not None

    @staticmethod
    def get_post_by_id(db: Session, post_id: int) -> Post | None:
        """ Find post by ID """
        return db.query(Post).filter(Post.id == post_id).first()

    # @staticmethod
    # def save_post(db: Session, post: Post) -> Post:
    #     """Save updated fields, e.g.  description, likes, comments, #hashtags """
    #
    #     print(f"... check {post} ...")
    #     # if db.object_session(post) is None:
    #     #     print("Object is not in session, ...")
    #
    #     # db.merge(post)
    #     print(f"... try commit {post} ...")
    #     db.commit()
    #     print(f"... try refresh {post} ...")
    #     # db.refresh(post)
    #     print(f"... refreshed {post} ...")
    #     return post

    @staticmethod
    def save_post(db: Session, post: Post) -> Post:
        """Find the post by its ID, update its fields and save changes"""
        existing_post = db.query(Post).filter(Post.id == post.id).first()

        if not existing_post:
            raise ValueError(f"Post with ID {post.id} not found")

        existing_post.description = post.description
        existing_post.likes = post.likes
        existing_post.comments = post.comments
        existing_post.hashtags = post.hashtags

        db.commit()
        db.refresh(existing_post)
        return existing_post
