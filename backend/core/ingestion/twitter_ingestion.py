# import snscrape.modules.twitter as sntwitter
from core.models import RawPost
import requests
from pathlib import Path
from PIL import Image
import pytesseract
import tempfile
from core.utils.text import similarity
from playwright.sync_api import sync_playwright
from datetime import datetime


from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

import os

load_dotenv()


X_GMAIL = os.getenv("X_GMAIL")
X_USERNAME = os.getenv("X_USERNAME")
X_PASSWORD = os.getenv("X_PASSWORD")


def login_to_x(page):

    page.goto("https://twitter.com/i/flow/login")

    page.wait_for_timeout(5000)

    username_input = page.locator(
        'input[autocomplete="username"]'
    )

    username_input.click()

    username_input.type(
        X_USERNAME,
        delay=100
    )

    page.wait_for_timeout(1000)

    page.keyboard.press("Enter")

    page.wait_for_timeout(5000)

    # Password
    password_input = page.locator(
        'input[name="password"]'
    )

    password_input.click()
    print("****X_PASSWORD",X_PASSWORD)
    password_input.type(
        X_PASSWORD,
        delay=100
    )

    page.wait_for_timeout(1000)

    page.keyboard.press("Enter")

    page.wait_for_timeout(5000)

def fetch_posts(
    account,
    since_date,
    max_posts=50000
):

    results = []

    seen_post_ids = set()

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            user_data_dir="playwright_data",
            headless=False,
        )

        page = context.new_page()

        page.goto("https://twitter.com/login")

        # input(
        #     "Login manually in browser, then press ENTER..."
        # )
        # page = context.new_page()

        # login_to_x(page)

        # page = browser.new_page()

        page.goto(
            f"https://twitter.com/{account}"
        )

        page.wait_for_timeout(5000)

        reached_target_date = False

        while (
            not reached_target_date
            and len(results) < max_posts
        ):

            tweets = page.locator("article")

            count = tweets.count()

            for i in range(count):

                tweet = tweets.nth(i)

                try:

                    # -----------------------------
                    # Tweet text
                    # -----------------------------
                    text = ""

                    text_locator = tweet.locator(
                        '[data-testid="tweetText"]'
                    )

                    if text_locator.count() > 0:

                        text = text_locator.first.inner_text()


                    # -----------------------------
                    # Tweet URL + Post ID
                    # -----------------------------
                    post_url = ""

                    tweet_links = tweet.locator("a")

                    for j in range(tweet_links.count()):

                        href = tweet_links.nth(j).get_attribute(
                            "href"
                        )

                        if (
                            href
                            and "/status/" in href
                        ):

                            post_url = (
                                f"https://twitter.com{href}"
                            )

                            break

                    # Skip invalid posts
                    if not post_url:
                        continue

                    # Real stable tweet ID
                    post_id = post_url.split("/")[-1]

                    # Skip duplicates
                    if post_id in seen_post_ids:
                        continue

                    seen_post_ids.add(post_id)


                    # -----------------------------
                    # Posted at
                    # -----------------------------
                    time_element = tweet.locator(
                        "time"
                    ).first

                    datetime_value = (
                        time_element.get_attribute(
                            "datetime"
                        )
                    )

                    posted_at = datetime.fromisoformat(
                        datetime_value.replace(
                            "Z",
                            "+00:00"
                        )
                    )


                    # -----------------------------
                    # Stop when older than target
                    # -----------------------------
                    if posted_at < datetime.strptime(since_date):

                        reached_target_date = True
                        break


                    # -----------------------------
                    # Image URLs
                    # -----------------------------
                    images = tweet.locator("img")

                    image_urls = []

                    for j in range(images.count()):

                        src = images.nth(j).get_attribute(
                            "src"
                        )

                        if (
                            src
                            and "media" in src
                        ):

                            image_urls.append(src)


                    # -----------------------------
                    # Save result
                    # -----------------------------
                    results.append({
                        "post_id": post_id,
                        "text": text,
                        "posted_at": posted_at,
                        "url": post_url,
                        "image_urls": image_urls,
                    })

                    print(
                        f"Collected post: {post_id}"
                    )

                except Exception as e:

                    print(
                        f"Tweet parsing failed: {e}"
                    )

            # -----------------------------
            # Scroll for older tweets
            # -----------------------------
            page.mouse.wheel(0, 15000)

            page.wait_for_timeout(3000)

        browser.close()

    return results

def save_posts(posts, country, handle):

    for post in posts:
        print("***post",post)
        RawPost.objects.get_or_create(
            post_id=post["post_id"],
            defaults={
                "country": country,
                "account_handle": handle,
                "post_text": post["text"],
                "image_urls": post["image_urls"],
                "post_url": post["url"],
                "posted_at": post["posted_at"],
            }
        )


def process_ocr(raw_post):

    if raw_post.ocr_processed:
        return

    extracted_texts = []

    for image_url in raw_post.image_urls:

        try:

            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            with tempfile.NamedTemporaryFile(
                suffix=".jpg"
            ) as temp_file:

                temp_file.write(response.content)
                temp_file.flush()

                image = Image.open(temp_file.name)
                image.load()

                text = pytesseract.image_to_string(image)

                if text.strip():
                    extracted_texts.append(text.strip())

        except Exception as e:
            print(f"OCR failed: {e}")

    image_text = "\n".join(extracted_texts)

    raw_post.image_text = image_text
    score = similarity(
    raw_post.post_text,
    image_text
    )

    if score > 0.85:
        raw_post.combined_text = raw_post.post_text

    else:
        raw_post.combined_text = "\n\n".join([
            raw_post.post_text,
            image_text
        ])
#     raw_post.combined_text = f"""
# {raw_post.post_text}

# {image_text}
#     """.strip()
    raw_post.ocr_processed = True
    raw_post.save()


# def fetch_posts(account,
#                 since_date,
#                 until_date=None,
#                 max_posts=None):

#     query = f"from:{account} since:{since_date}"

#     if until_date:
#         query += f" until:{until_date}"

#     results = []

#     for tweet in sntwitter.TwitterSearchScraper(query).get_items():

#         image_urls = []

#         if tweet.media:
#             for media in tweet.media:

#                 # Image
#                 if hasattr(media, "fullUrl"):
#                     image_urls.append(media.fullUrl)

#         results.append({
#             "post_id": str(tweet.id),
#             "text": tweet.rawContent,
#             "posted_at": tweet.date,
#             "url": tweet.url,
#             "image_urls": image_urls,
#         })

#         if max_posts and len(results) >= max_posts:
#             break

#     return results

