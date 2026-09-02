import boto3
import json
import pandas as pd
from botocore.client import Config

def get_data_from_datalake(platform='instagram', year_month='2026-08'):
    """
    Fungsi untuk menarik data bersih dari Data Lake (MinIO/S3)
    dan mengonversinya menjadi Pandas DataFrame.
    
    platform: 'instagram' atau 'tiktok'
    year_month: format 'YYYY-MM' (contoh: '2026-08')
    """
    
    # 1. Konfigurasi Endpoint (URL Ngrok)
    S3_ENDPOINT = 'https://ventral-unfondly-rosalyn.ngrok-free.dev'
    ACCESS_KEY = 'admin'
    SECRET_KEY = 'password123'
    BUCKET_NAME = 'narative-datalake'
    
    print(f"Menghubungkan ke Data Lake: {S3_ENDPOINT} ...")

    # 2. Inisialisasi Koneksi ke Data Lake
    s3 = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        config=Config(signature_version='s3v4'),
        region_name='us-east-1'
    )

    # 3. Mengambil daftar file dari folder bulan ini
    folder_path = f'{platform}/parsed/{year_month}/'
    print(f"Mencari data di path: {folder_path}")
    
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=folder_path)
    except Exception as e:
        print(f"Gagal menghubungi Data Lake. Pastikan Ngrok & MinIO menyala. Error: {e}")
        return pd.DataFrame()

    data_bersih = []

    # 4. Looping untuk membaca setiap file JSON yang ditemukan
    if 'Contents' in response:
        print(f"Menemukan {len(response['Contents'])} file postingan. Mengunduh data...")
        
        for obj in response['Contents']:
            file_key = obj['Key']
            
            # Download isi file (tanpa perlu simpan ke hardisk)
            file_obj = s3.get_object(Bucket=BUCKET_NAME, Key=file_key)
            file_content = file_obj['Body'].read().decode('utf-8')
            
            # Parse JSON dan masukkan ke list
            post_data = json.loads(file_content)
            data_bersih.append(post_data)
    else:
        print(f"Tidak ada data ditemukan di folder {folder_path}.")
        return pd.DataFrame()

    # 5. Ubah ke Pandas DataFrame
    df = pd.json_normalize(data_bersih)
    return df

if __name__ == "__main__":
    print("=== SCRIPT PENARIKAN DATA (UNTUK TIM DATA SCIENCE) ===\n")
    
    # Contoh penggunaan untuk mengambil data Instagram
    df_ig = get_data_from_datalake(platform='instagram', year_month='2026-08')
    
    if not df_ig.empty:
        print("\n=== Data Instagram Siap Olah ===")
        print(f"Total Baris: {len(df_ig)}")
        # Menampilkan 5 data teratas dengan kolom-kolom penting
        kolom_penting = ['platform', 'author_username', 'caption', 'metrics.likes', 'metrics.comments']
        # Gunakan intersection agar tidak error jika ada kolom yang belum ada datanya
        kolom_tampil = [k for k in kolom_penting if k in df_ig.columns]
        
        print(df_ig[kolom_tampil].head())
        
        # Contoh menyimpan (opsional)
        # df_ig.to_csv('data_instagram.csv', index=False)
        # print("Data berhasil disimpan ke data_instagram.csv")
