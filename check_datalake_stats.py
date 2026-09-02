import os
import boto3
from botocore.client import Config
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Setup Boto3 Client
endpoint_url = os.getenv('S3_ENDPOINT') or os.getenv('MINIO_ENDPOINT', 'http://localhost:9000')
if not endpoint_url.startswith('http'):
    endpoint_url = f"http://{endpoint_url}"

access_key = os.getenv('AWS_ACCESS_KEY_ID') or os.getenv('MINIO_ROOT_USER', 'admin')
secret_key = os.getenv('AWS_SECRET_ACCESS_KEY') or os.getenv('MINIO_ROOT_PASSWORD', 'password123')
bucket_name = os.getenv('S3_BUCKET_NAME', 'narative-datalake')

s3 = boto3.client(
    's3',
    endpoint_url=endpoint_url,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

def count_files_in_prefix(prefix):
    total_files = 0
    paginator = s3.get_paginator('list_objects_v2')
    try:
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        for page in pages:
            if 'Contents' in page:
                total_files += len(page['Contents'])
        return total_files
    except Exception as e:
        print(f"Error reading prefix {prefix}: {e}")
        return 0

if __name__ == '__main__':
    print(f"=== STATISTIK DATA LAKE (Bucket: {bucket_name}) ===\n")
    
    platforms = ['instagram', 'tiktok', 'twitter']
    
    total_all = 0
    for plat in platforms:
        # Kita hitung file yang ada di dalam folder 'parsed' (data bersih)
        prefix = f"{plat}/parsed/"
        count = count_files_in_prefix(prefix)
        total_all += count
        
        print(f"[{plat.upper()}]")
        print(f"Total File Parsed : {count} file\n")
        
    print(f"=====================================")
    print(f"TOTAL KESELURUHAN   : {total_all} file")
    print(f"=====================================")
