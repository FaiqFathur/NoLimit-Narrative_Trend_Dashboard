import boto3
import json
from botocore.client import Config
from datetime import datetime

def upload_twitter_to_datalake(parsed_data_dict, tweet_id):
    """
    Fungsi untuk Mas Baihaqi mengunggah data Twitter yang sudah di-parse
    langsung ke Data Lake (MinIO) milik Faiq via Ngrok.
    """
    # 1. Pastikan URL Ngrok MinIO Faiq dimasukkan di sini
    S3_ENDPOINT = 'https://ventral-unfondly-rosalyn.ngrok-free.dev' 
    ACCESS_KEY = 'admin'
    SECRET_KEY = 'password123'
    BUCKET_NAME = 'narative-datalake'
    
    # 2. Inisialisasi Boto3 S3 Client
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )
    except Exception as e:
        print(f"❌ Gagal konek ke S3/MinIO: {e}")
        return False
        
    # 3. Format folder dan nama file
    month_folder = datetime.now().strftime("%Y-%m")
    folder_path = f"twitter/parsed/{month_folder}/"
    filename = f"twitter_{tweet_id}.json"
    object_key = f"{folder_path}{filename}"
    
    # 4. Unggah ke Data Lake
    try:
        json_bytes = json.dumps(parsed_data_dict, indent=4).encode('utf-8')
        
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=object_key,
            Body=json_bytes,
            ContentType='application/json'
        )
        print(f"✅ Sukses upload {filename} ke {S3_ENDPOINT}/{BUCKET_NAME}/{object_key}")
        return True
    except Exception as e:
        print(f"❌ Gagal upload data Twitter: {e}")
        return False

# ==========================================
# CONTOH PENGGUNAAN OLEH MAS BAIHAQI:
# ==========================================
if __name__ == "__main__":
    # Contoh data yang sudah selesai di-parse oleh Mas Baihaqi
    contoh_data_twitter = {
        "platform": "twitter",
        "post_id": "1234567890",
        "author_username": "jokowi",
        "caption": "Membangun masa depan Indonesia yang lebih cerah.",
        "metrics": {
            "likes": 50000,
            "comments": 2000,
            "views": 1500000,
            "shares": 10000
        },
        "timestamp": 1690000000,
        "url": "https://twitter.com/jokowi/status/1234567890"
    }
    
    # Panggil fungsinya
    upload_twitter_to_datalake(contoh_data_twitter, contoh_data_twitter["post_id"])
