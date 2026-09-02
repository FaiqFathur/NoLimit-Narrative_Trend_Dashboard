import os
import json
import time
import random
import urllib.parse
import gzip
from datetime import datetime
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

TWITTER_AUTH_TOKEN = os.getenv("TWITTER_AUTH_TOKEN")
TWITTER_CT0 = os.getenv("TWITTER_CT0")

# Inisialisasi list untuk menampung JSON mentah dari GraphQL
intercepted_data = []

# Variabel global untuk mencatat tren apa yang sedang di-scroll
current_trend = "Unknown"


def handle_response(response):
    """
    Fungsi penyadap (interceptor).
    Akan dipanggil setiap kali browser menerima data (response) dari internet.
    """
    try:
        url = response.url
        if "api" in url or "graphql" in url:
            print(f"  [DEBUG URL] {response.status}: {url[:100]}")
            
        # Kita incar jalur belakang (GraphQL API / Timeline JSON) milik Twitter
        if response.status == 200 and ("graphql" in url or "timeline.json" in url):
            print(f"[+] [INTERCEPT] Berhasil menyadap payload JSON dari: {url.split('?')[0].split('/')[-1]}")
            data = response.json()
            intercepted_data.append({
                "trend": current_trend,
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "raw_json": data
            })
    except Exception as e:
        print(f"  [DEBUG ERROR] Gagal ekstrak JSON dari {response.url[:80]}: {e}")

def extract_clean_trend_names(page):
    """Mengekstrak daftar tren dari halaman Explore Twitter"""
    trends = []
    trend_elements = page.locator("div[data-testid='trend']").all()
    
    for el in trend_elements:
        text = el.inner_text()
        lines = text.split('\n')
        
        valid_lines = []
        for line in lines:
            line_clean = line.strip()
            # Buang baris kosong, karakter titik tengah '·', dan angka urutan murni (misal: '1', '2')
            if line_clean in ['', '·'] or line_clean.isdigit():
                continue
                
            # Buang label kategori bawaan Twitter (Trending, Only on X, posts, dll)
            lower_line = line_clean.lower()
            if "trending" in lower_line: continue
            if "only on x" in lower_line: continue
            if "post" in lower_line: continue
            
            valid_lines.append(line_clean)
            
        if valid_lines:
            # Baris valid pertama yang tersisa hampir dipastikan 100% adalah topik utamanya
            trend_name = valid_lines[0]
            if trend_name not in trends and len(trend_name) > 1:
                trends.append(trend_name)
                
    return trends

def scrape_twitter_batch(max_trends_to_scrape=10, scrolls_per_trend=3):
    global current_trend
    
    profile_dir = os.path.join(os.getcwd(), "twitter_profile")
    raw_dir = os.path.join(os.getcwd(), "raw_batches")
    
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)

    with sync_playwright() as p:
        print(f"Membuka browser dengan profil di '{profile_dir}'...")
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=True,
            channel="msedge", 
            viewport={"width": 1280, "height": 720},
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # MENGINJEKSI COOKIES OTOMATIS
        if TWITTER_AUTH_TOKEN:
            print("Menginjeksi cookies ke dalam browser untuk Login Otomatis...")
            browser.add_cookies([
                {"name": "auth_token", "value": TWITTER_AUTH_TOKEN, "domain": ".twitter.com", "path": "/"},
                {"name": "ct0", "value": TWITTER_CT0, "domain": ".twitter.com", "path": "/"},
                {"name": "auth_token", "value": TWITTER_AUTH_TOKEN, "domain": ".x.com", "path": "/"},
                {"name": "ct0", "value": TWITTER_CT0, "domain": ".x.com", "path": "/"}
            ])
            print("Cookies berhasil diinjeksi!")
        
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # MENGAKTIFKAN PENYADAP JARINGAN (NETWORK INTERCEPTOR)
        page.on("response", handle_response)
        
        # LANGKAH 1: Kumpulkan Daftar Tren
        print("Membuka halaman Trending Indonesia...")
        page.goto("https://x.com/explore/tabs/trending", timeout=60000)
        time.sleep(7)
        page.evaluate("window.scrollBy(0, 1000)")
        time.sleep(2)
        
        trends = extract_clean_trend_names(page)
        
        print(f"\nBerhasil menemukan {len(trends)} Top Trending Topics:")
        for i, t in enumerate(trends, 1):
            print(f"  {i}. {t}")
            
        if not trends:
            print("Gagal menemukan elemen tren. Menggunakan tren cadangan sementara.")
            trends = ["#Indonesia", "Viral"]

        # LANGKAH 2: Looping Setiap Trend dan Intercept Data
        for trend in trends[:max_trends_to_scrape]:
            current_trend = trend
            print(f"\n=======================================================")
            print(f"Mulai menyedot data untuk tren: {trend}")
            print(f"=======================================================")
            
            search_url = f"https://x.com/search?q={urllib.parse.quote(trend)}&src=trend_click"
            page.goto(search_url)
            time.sleep(5) # Tunggu loading awal
            
            for i in range(scrolls_per_trend): # Lakukan scroll untuk memancing lebih banyak data
                print(f"Scroll {i+1}/{scrolls_per_trend} untuk tren '{trend}'...")
                page.evaluate("window.scrollBy(0, 2000)")
                # Jeda acak 3 hingga 6 detik antar scroll agar terlihat seperti manusia asli membaca
                time.sleep(random.uniform(3.0, 6.0)) 
            
            # Jeda acak yang lumayan lama saat berpindah tren agar tidak terkena Rate Limit Twitter
            print(f"Selesai dengan '{trend}'. Istirahat sejenak seperti manusia...")
            time.sleep(random.uniform(7.0, 15.0))
            
            # --- TAMBAHAN: SIMPAN DATA SEMENTARA (INCREMENTAL SAVE & GZIP ON THE FLY) ---
            if intercepted_data:
                temp_filename = os.path.join(raw_dir, f"twitter-batch-IN_PROGRESS.json.gz")
                with gzip.open(temp_filename, "wt", encoding="utf-8") as f:
                    json.dump(intercepted_data, f, indent=4, ensure_ascii=False)
                print(f"[+] Data sementara disimpan terkompresi. Total: {len(intercepted_data)} payload.")
            
        print(f"\n=======================================================")
        print(f"SELESAI KESELURUHAN! Berhasil menyadap {len(intercepted_data)} payload GraphQL.")
        print(f"=======================================================")
        
        browser.close()
        
        # Simpan hasil sadapan ke file lokal (GZIP On The Fly)
        if intercepted_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(raw_dir, f"twitter-batch-{timestamp}.json.gz")
            
            with gzip.open(filename, "wt", encoding="utf-8") as f:
                json.dump(intercepted_data, f, indent=4, ensure_ascii=False)
                
            print(f"Data Batch berhasil disimpan terkompresi di: {filename}")
        else:
            print("Gagal menyadap API. Twitter mungkin mengubah URL endpoint-nya atau API tidak dipanggil.")

if __name__ == "__main__":
    # LIMITS MODERAT UNTUK KEAMANAN AKUN (TETAP MASS-SCRAPING)
    # 25 Trends x 25 Scrolls. Cukup aman tapi tetap ribuan data per siklus.
    scrape_twitter_batch(max_trends_to_scrape=25, scrolls_per_trend=25)
