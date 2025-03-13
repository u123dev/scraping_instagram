import os
from dotenv import load_dotenv

from notifications.services import bot
from scrape.instascraper import InstaScraper
from models import Post

from database import db

from scrape.tags_settings import *


load_dotenv()


INSTA_USERNAME = os.getenv("INSTA_USERNAME")
INSTA_PASSWORD = os.getenv("INSTA_PASSWORD")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def scrape_insta(db):
    """Run scraping Insta into database """

    if INSTA_USERNAME is None or INSTA_PASSWORD is None:
        print("Missing credentials")
        return None

    scraper = InstaScraper(INSTA_USERNAME, INSTA_PASSWORD, TARGET_NAME, HASHTAG)
    posts_obj = scraper.get_insta_posts(TARGET_NAME, HASHTAG)

    result = scraper.get_detail_posts(posts_obj)
    scraper.close_driver()
    print("Scraping Complete")

    #  notification by telegram bot
    message = scraper.filter_posts_by_hashtag(result, hashtag=HASHTAG)
    if message:
        message = f"New Scraping for '{HASHTAG}': \n {message}"
        bot.send_message(message)

    return result


if __name__ == "__main__":
    scrape_insta(db)
