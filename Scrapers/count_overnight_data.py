import os
import json
import gzip
import glob

raw_dir = r"d:\College\KP\Scrapers\raw_batches"
files = glob.glob(os.path.join(raw_dir, "twitter-batch-*"))

total_payloads = 0
total_tweets = 0

def count_tweets_in_obj(obj):
    global total_tweets
    if isinstance(obj, dict):
        if 'legacy' in obj and 'full_text' in obj['legacy']:
            total_tweets += 1
        for v in obj.values():
            count_tweets_in_obj(v)
    elif isinstance(obj, list):
        for item in obj:
            count_tweets_in_obj(item)

print("Mulai menghitung jumlah tweet dari semalaman...")

for f in files:
    try:
        if f.endswith('.gz'):
            with gzip.open(f, 'rt', encoding='utf-8') as file:
                data = json.load(file)
        else:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
        
        total_payloads += len(data)
        count_tweets_in_obj(data)
    except Exception as e:
        print(f"Gagal membaca file {os.path.basename(f)}: {e}")

print(f"\nTotal File Batch: {len(files)}")
print(f"Total API Payloads disadap: {total_payloads}")
print(f"Total Tweet Asli Terkumpul: {total_tweets} tweets")
