from sqlalchemy import String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    post_url: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    raw_likes: Mapped[str] = mapped_column(String, default="")
    likes: Mapped[int] = mapped_column(default=0)
    comments: Mapped[int] = mapped_column(default=0)
    hashtags: Mapped[str] = mapped_column(String, default="")
    description: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __str__(self):
        return (f"Post(url={self.post_url} | created_at={self.created_at})"
                f"raw_likes={self.raw_likes}, likes={self.likes}, comments={self.comments}, "
                f"hashtags={self.hashtags}, description={self.description[:20]}...)")


# Base.metadata.create_all(bind=engine)
