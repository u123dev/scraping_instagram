from celery import Celery

from notifications.services import bot
from scrape.parser import scrape_insta

from database import db


app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

app.conf.update(
    result_expires=3600,  # update every 3600s
)

app.conf.beat_schedule = {
    "parse_insta_every_10_minutes": {
        "task": "celery_worker.parse_insta",
        "schedule": 600,  # run every 10m=600s
    },
}

app.conf.timezone = "UTC"


@app.task
def test1():
    print("test1")
    message = "test-bot"
    if message:
        bot.send_message(message)
    return {"my_result": "My success"}


@app.task
def parse_insta():
    """ Background task for scraping instagram posts"""
    posts = scrape_insta(db)
    posts_dict = [post.dict() for post in posts]
    return posts_dict
