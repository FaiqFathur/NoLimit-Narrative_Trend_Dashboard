import json
import os
import glob

def cek_total():
    print("==================================================")
    print("DASHBOARD STATUS DATA SCRAPING DE 2")
    print("==================================================")
    
    # Cek total data yang berhasil masuk ke MinIO
    db_path = "processed_tweet_ids.json"
    if os.path.exists(db_path):
        with open(db_path, "r") as f:
            data = json.load(f)
            print(f"[SUCCESS] Total Data Berhasil Dikirim ke MinIO : {len(data)} Tweet")
    else:
        print("[SUCCESS] Total Data Berhasil Dikirim ke MinIO : 0 Tweet")
        
    print("\n[INFO] Cek Folder Barang Bukti (raw_batches):")
    raw_files = glob.glob("raw_batches/twitter-batch-*")
    if raw_files:
        print(f"Ditemukan {len(raw_files)} file batch (GZIP/JSON).")
        total_size = sum(os.path.getsize(f) for f in raw_files)
        print(f"Total ukuran penyimpanan barang bukti  : {total_size / (1024*1024):.2f} MB")
    else:
        print("Belum ada file barang bukti.")
        
    print("\n[INFO] Cek Audit Log:")
    log_files = glob.glob("audit_log_*.txt")
    print(f"Terdapat {len(log_files)} file Laporan Audit.")
    print("==================================================")

if __name__ == "__main__":
    cek_total()
