import os
import json
import gzip
import glob
from validator import moderate_content

raw_dir = r"d:\College\KP\Scrapers\raw_batches"
files = glob.glob(os.path.join(raw_dir, "twitter-batch-*"))

unique_ids = set()
total_blocked = 0
total_flagged = 0
total_clean = 0

def find_tweets(obj, results):
    if isinstance(obj, dict):
        if 'legacy' in obj and 'full_text' in obj['legacy']:
            results.append(obj)
        for v in obj.values():
            find_tweets(v, results)
    elif isinstance(obj, list):
        for item in obj:
            find_tweets(item, results)

print("Mulai menyimulasikan penyaringan Data (Anti-Duplikat & Validator)...")

for f in files:
    try:
        if f.endswith('.gz'):
            with gzip.open(f, 'rt', encoding='utf-8') as file:
                data = json.load(file)
        else:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
        
        raw_tweets = []
        find_tweets(data, raw_tweets)
        
        for t in raw_tweets:
            tweet_id = t.get('rest_id')
            if not tweet_id:
                continue
                
            if tweet_id not in unique_ids:
                unique_ids.add(tweet_id)
                text = t.get('legacy', {}).get('full_text', '')
                if text:
                    mod = moderate_content(text)
                    if mod.status == "blocked":
                        total_blocked += 1
                    elif mod.status == "flagged":
                        total_flagged += 1
                    else:
                        total_clean += 1
                        
    except Exception as e:
        print(f"Gagal membaca file {os.path.basename(f)}: {e}")

print(f"\nTotal Tweet Mentah yang Ditemukan (Unique ID): {len(unique_ids)}")
print(f"[-] Diblokir oleh Validator (Kotor/Sensitif): {total_blocked}")
print(f"[!] Masuk Karantina (Quarantine/Flagged): {total_flagged}")
print(f"[+] Lolos Bersih (Masuk Raw MinIO): {total_clean}")
