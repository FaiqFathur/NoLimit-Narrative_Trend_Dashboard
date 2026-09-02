import time
import subprocess
import sys
from datetime import datetime

def run_script(script_name, delay=0):
    if delay > 0:
        print(f"Menunggu {delay} detik sebelum menjalankan {script_name}...")
        time.sleep(delay)
        
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [RUN] MENJALANKAN {script_name}...")
    try:
        # Menggunakan sys.executable agar kompatibel di OS apapun
        subprocess.run([sys.executable, script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[-] Gagal menjalankan {script_name}. Error code: {e.returncode}")
    except Exception as e:
        print(f"[-] Error tidak terduga saat menjalankan {script_name}: {e}")

def run_pipeline():
    print(f"\n========================================================================")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] MEMULAI SIKLUS SCRAPING OTOMATIS")
    print("  1. Interceptor menangkap batch data GraphQL")
    print("  2. Parser mengambil BATCH tersebut dan mendorongnya ke Beanstalkd Queue (raw-data / quarantine-data)")
    print(f"========================================================================")
    
    # 1. Menjalankan Pemanen Data (Scraper)
    run_script("twitter_batch_interceptor.py")
    
    # 2. Menjalankan Pembersih Data (Parser)
    run_script("twitter_parser.py", delay=2)
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Siklus saat ini rampung. Menunggu siklus berikutnya...")
    print(f"\nPastikan Docker container Beanstalkd sudah menyala!")
    print("========================================================================\n")

if __name__ == "__main__":
    # Jadwal waktu spesifik: Dibuat setiap 1.5 jam (24 Jam)
    JADWAL_SCRAPING = [
        "00:30", "02:00", "03:30", "05:00", "06:30", "08:00", 
        "09:30", "11:00", "12:30", "15:00", "16:30", 
        "18:30", "20:00", "21:30", "23:00"
    ]
    
    print("[INFO] Auto-Pipeline Aktif! Sistem siap mengeruk data pada jam-jam berikut:")
    for jadwal in JADWAL_SCRAPING:
        print(f"   - {jadwal}")
    
    print("\nTekan Ctrl+C kapan saja untuk menghentikan program.")
    print("Menunggu waktu yang ditentukan...")
    
    # Looping abadi mengecek waktu setiap menit
    while True:
        waktu_sekarang = datetime.now().strftime("%H:%M")
        if waktu_sekarang in JADWAL_SCRAPING:
            run_pipeline()
            # Tidur 65 detik untuk memastikan skrip tidak tereksekusi dua kali di menit yang sama
            time.sleep(65) 
        else:
            # Cek jam lagi setiap 20 detik
            time.sleep(20)
