from playwright.sync_api import sync_playwright

def handle_response(response):
    url = response.url
    if response.status == 200 and ("graphql" in url or "timeline.json" in url):
        print(f"INTERCEPT: {url[:80]}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.on('response', handle_response)
    print("Going to X explore...")
    page.goto('https://x.com/explore/tabs/trending', timeout=60000)
    page.wait_for_timeout(5000)
    browser.close()
