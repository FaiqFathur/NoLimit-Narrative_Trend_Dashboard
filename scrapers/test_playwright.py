import os
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()
TWITTER_AUTH_TOKEN = os.getenv('TWITTER_AUTH_TOKEN')
TWITTER_CT0 = os.getenv('TWITTER_CT0')

def test_twitter():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=os.path.join(os.getcwd(), 'twitter_profile'),
            headless=True,
            viewport={'width': 1280, 'height': 720}
        )
        if TWITTER_AUTH_TOKEN:
            browser.add_cookies([
                {'name': 'auth_token', 'value': TWITTER_AUTH_TOKEN, 'domain': '.twitter.com', 'path': '/'},
                {'name': 'ct0', 'value': TWITTER_CT0, 'domain': '.twitter.com', 'path': '/'},
                {'name': 'auth_token', 'value': TWITTER_AUTH_TOKEN, 'domain': '.x.com', 'path': '/'},
                {'name': 'ct0', 'value': TWITTER_CT0, 'domain': '.x.com', 'path': '/'}
            ])
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto('https://x.com/search?q=Train')
        time.sleep(5)
        page.screenshot(path='debug.png')
        browser.close()

if __name__ == '__main__':
    test_twitter()
