import os
import urllib.parse
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()
TWITTER_AUTH_TOKEN = os.getenv('TWITTER_AUTH_TOKEN')
TWITTER_CT0 = os.getenv('TWITTER_CT0')

def debug_response(response):
    if 'SearchTimeline' in response.url:
        print(f"SEARCH TIMELINE HTTP STATUS: {response.status}")

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=os.path.join(os.getcwd(), 'twitter_profile'),
            headless=False,
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
        page.goto('https://x.com/search?q=FRAGRANT')
        page.wait_for_timeout(5000)
        browser.close()

if __name__ == '__main__':
    test()
