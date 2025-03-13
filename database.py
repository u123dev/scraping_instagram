from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from models import Post, Base
from settings import DATABASE_URL


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()


Base.metadata.create_all(bind=engine)
