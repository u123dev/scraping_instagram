import random

from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium_stealth import stealth

from bs4 import BeautifulSoup


from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from models import Post
from schemas import PostCreateSchema
from service import create_post, patch_post
from repository import PostRepository
from scrape.tools import timeout, text2int, clean_text, is_docker

from database import db

from scrape.tags_settings import *


class InstaScraper:
    """ Scrape Instagram posts from Instagram """

    def __init__(self, username, password, target_name, hashtag):
        self.username = username
        self.password = password
        self.target_name = target_name
        self.hashtag = hashtag
        self.driver = self.init_driver()

    def init_driver(self):
        """Initialize Selenium WebDriver"""
        options = Options()
        # options.add_argument("--headless")  # background mode
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        options.add_argument("start-maximized")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        )
        # options.add_argument(
        #     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        # )
        # options.add_argument(
        #     "Accept-Language=ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3"
        # )
        # options.add_argument(
        #     "--user-agent=Mozilla/5.0 (Linux; Android 13; Samsung Galaxy S9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6289.194 Mobile Safari/537.36"
        # )

        if is_docker():
            print("Scraping in docker mode")
            # # Docker
            options.add_argument("--headless")  # background mode
            service = Service("/usr/bin/chromedriver")  # path to chromedriver
            driver = webdriver.Chrome(service=service, options=options)
        else:
            print("Scraping in local mode")
            # # Local
            driver = webdriver.Chrome(options=options)

        stealth(driver,
                # languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        return driver

    def close_driver(self):
        """ Close Selenium WebDriver"""
        self.driver.close()

    def login_instagram(self):
        """Login Instagram"""
        self.driver.get("https://www.instagram.com/accounts/login/")
        timeout(1, 3)

        user_input = self.driver.find_element(By.NAME, "username")
        pass_input = self.driver.find_element(By.NAME, "password")

        user_input.send_keys(self.username)
        timeout(2, 3)
        pass_input.send_keys(self.password)
        timeout(3, 4)
        pass_input.send_keys(Keys.RETURN)

        timeout(20, 22)

    def human_scroll(self):
        """Imitate human behavior - Scroll page"""
        body = self.driver.find_element(By.TAG_NAME, "body")
        for _ in range(random.randint(1, 3)):
            body.send_keys(Keys.PAGE_DOWN)
            timeout(1, 3)

    def click_on_window(self, x=0, y=0):
        """Click in point (x, y) in browser window to close possible opened window"""
        action = ActionChains(self.driver)
        try:
            action.move_by_offset(x, y).click().perform()
        except WebDriverException as e:
            print(f"Click error: {e}")

    def get_post_containers(self, tag_selector):
        """Get container blocks"""
        try:
            return self.driver.find_elements(By.CSS_SELECTOR, tag_selector)
        except NoSuchElementException:
            print("No found container blocks.")
            return []
        except Exception as e:
            print(f"Error when getting container blocks: {e}")
            return []

    def hover_over_post(self, element):
        """Hover cursor under element to display hidden information"""
        action = ActionChains(self.driver)
        try:
            action.move_to_element(element).perform()
        except Exception as e:
            print(f"Hover error: {e}")

    def get_likes_and_comments(self):
        """Get raw likes & commentaries from post in container blocks"""
        try:
            wait = WebDriverWait(self.driver, 10)
            target_spans = wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, TAG_POST_LIKES_COMMENTS)
                )
            )
            # get text from element
            return [span.text for span in target_spans]
        except TimeoutException:
            print("Timeout error: can't wait appearing Likes/Comments elements.")
            return ["", ""]
        except Exception as e:
            print(f"Error when getting Likes/Comments: {e}")
            return ["", ""]

    def get_post_url(self, post_container):
        """Get Post url """
        return post_container.get_attribute("href")

    def get_post_data(self, post_url, post_container):
        """Get Post data """
        self.hover_over_post(post_container)  # move mouse to element
        timeout(0.2, 1.2)

        raw_likes, comments = self.get_likes_and_comments()  # get likes/commentaries info
        return {
            "post_url": post_url,
            "raw_likes": raw_likes,
            "comments": text2int(comments)
        }

    def get_insta_posts(self, target_username, hashtag):
        """Get Insta posts from Instagram account"""

        self.login_instagram()

        try:
            url = f"https://www.instagram.com/{target_username}/"
            self.driver.get(url)
            timeout(10, 12)  # wait loading page

            self.click_on_window()  # click to close window if exists
            # self.human_scroll()  # imitate human behavior

            # Find container blocks
            post_containers = self.get_post_containers(TAG_POST_CONTAINERS)

            # posts = []
            posts_obj = []
            for post_container in post_containers[:10]:
                try:
                    post_url = self.get_post_url(post_container)
                    if not PostRepository.check_post(db, post_url):
                        post_data = self.get_post_data(post_url, post_container)
                        db_post = create_post(db, PostCreateSchema.model_validate(post_data))
                        posts_obj.append(db_post)
                        print(f"Add new Post: {db_post}")
                except Exception as e:
                    print(f"Error parsing post: {e}")

            return posts_obj

        except TimeoutException:
            print("Timeout when loading page.")
        except WebDriverException as e:
            print(f"WebDriver error: {e}")
        except Exception as e:
            print(f"Unexpected Error: {e}")

    def get_detail_posts(self, posts_obj):
        """Detail info of posts"""
        for post in posts_obj:
            self.get_detail_post(post)
        return posts_obj

    def get_detail_post(self, post):
        """Detail info of one post"""
        try:
            self.driver.get(post.post_url)
            timeout()  # wait while loading page

            # get likes
            try:
                likes = self.driver.find_element(By.CSS_SELECTOR, TAG_POST_DETAIL_LIKES)
                likes = text2int(likes.text)
            except NoSuchElementException:
                print("Likes element not found.")
                likes = 0
            post.likes = likes

            # get #hashtags
            try:
                hashtags_elements = self.driver.find_elements(By.CSS_SELECTOR, TAG_POST_DETAIL_HASHTAGS)
                hashtags_values = ",".join([hashtag.text for hashtag in hashtags_elements])
            except NoSuchElementException:
                print("Hashtags elements not found.")
                hashtags_values = ""
            post.hashtags = hashtags_values

            # get description
            try:
                description_element = self.driver.find_element(By.TAG_NAME, TAG_POST_DETAIL_DESCRIPTION)
                description_html = description_element.get_attribute("outerHTML")
                soup = BeautifulSoup(description_html, "html.parser")
                description = soup.get_text()  # text without nested tags
                description = clean_text(description)  # clean unprintable char
            except NoSuchElementException:
                print("Description element not found.")
                description = ""
            except Exception as e:
                print(f"Error processing description: {e}")
                description = ""
            post.description = description

            # post object has been updated
            patch_post(db, post)
            print(f"Updated {post}")

        except Exception as e:
            print(f"Unexpected error: {e}")

        return post

    def filter_posts_by_hashtag(self, posts: list[Post], hashtag: str) -> str:
        """ Select posts by hashtag """
        result = ""
        for post in posts:
            hashtags_list = post.hashtags.lower().split(",")
            if hashtag.lower() in hashtags_list:
                result += f"id={post.id}:{post.post_url} \n"
        return result
