import os
import json
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()
TWITTER_AUTH_TOKEN = os.getenv('TWITTER_AUTH_TOKEN')
TWITTER_CT0 = os.getenv('TWITTER_CT0')

def debug_response(response):
    url = response.url
    if 'graphql' in url and response.status == 200:
        try:
            data = response.json()
            print(f"SUCCESS JSON: {url[:100]}")
        except Exception as e:
            print(f"FAILED JSON: {url[:100]} - ERROR: {e}")

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=os.path.join(os.getcwd(), 'twitter_profile'),
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        if TWITTER_AUTH_TOKEN:
            browser.add_cookies([
                {'name': 'auth_token', 'value': TWITTER_AUTH_TOKEN, 'domain': '.twitter.com', 'path': '/'},
                {'name': 'ct0', 'value': TWITTER_CT0, 'domain': '.twitter.com', 'path': '/'},
                {'name': 'auth_token', 'value': TWITTER_AUTH_TOKEN, 'domain': '.x.com', 'path': '/'},
                {'name': 'ct0', 'value': TWITTER_CT0, 'domain': '.x.com', 'path': '/'}
            ])
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.on('response', debug_response)
        page.goto('https://x.com/search?q=Train')
        page.wait_for_timeout(5000)
        browser.close()

if __name__ == '__main__':
    test()
