import json

f = open(r'd:\College\KP\Scrapers\raw_batches\twitter-batch-IN_PROGRESS.json', encoding='utf-8')
data = json.load(f)
tweets = []

def find(obj):
    if isinstance(obj, dict):
        if 'legacy' in obj and 'full_text' in obj['legacy']: 
            tweets.append(obj)
        for v in obj.values(): 
            find(v)
    elif isinstance(obj, list):
        for item in obj: 
            find(item)

find(data)
if tweets:
    t = tweets[0]
    leg = t.get('legacy', {})
    print("BUKTI DATA DAPET BRO:")
    print(f"Text: {leg.get('full_text')[:100]}...")
    print(f"Likes: {leg.get('favorite_count')}")
    print(f"Comments: {leg.get('reply_count')}")
    print(f"Retweets: {leg.get('retweet_count')}")
else:
    print("Belum ada tweet")
