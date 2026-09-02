import os
import json
import urllib.parse
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()
TWITTER_AUTH_TOKEN = os.getenv('TWITTER_AUTH_TOKEN')
TWITTER_CT0 = os.getenv('TWITTER_CT0')

def debug_response(response):
    if 'api' in response.url or 'graphql' in response.url:
        print(f"DEBUG URL [{response.status}]: {response.url[:100]}")

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
        
        print("Visiting search...")
        page.goto('https://x.com/search?q=Train')
        
        # Take a screenshot to see if it's logged in or blocked
        page.wait_for_timeout(5000)
        page.screenshot(path='debug_login.png')
        print("Done.")
        browser.close()

if __name__ == '__main__':
    test()
