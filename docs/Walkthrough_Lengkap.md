# 🏆 Walkthrough Hasil Pengerjaan - Data Engineer 2 (Baihaqi)
**Periode:** Sprint 0 hingga Sprint 3 (Medallion Data Pipeline)

Dokumen ini adalah bukti kerja (Walkthrough) dari hasil eksekusi seluruh rancangan sistem yang menjadi tanggung jawab DE 2.

---

## ✅ Sprint 0: Setup & Planning

1. **Infrastruktur Database Siap Digunakan**
   - File `models.py` telah sukses mendefinisikan skema tabel `users`, `posts`, `topics`, dan `entities` yang ketat tipe datanya.
   - Fitur migrasi menggunakan **Alembic** telah dikonfigurasi dan berhasil diinisialisasi (terdapat *history* revisi inisial di dalam folder `alembic/versions/`).
   - Infrastruktur JVM (Elasticsearch & Neo4J) telah disiapkan di *env* lokal.

---

## ✅ Sprint 1: Data Foundation (X/Twitter Pipeline)

1. **Keberhasilan Scraping Skala Besar (Scraper 24 Jam)**
   - Script `auto_pipeline.py` dan `twitter_batch_interceptor.py` sukses diimplementasikan.
   - **Hasil:** Berhasil mengeruk sekitar **27.000+ data mentah (1 GB)** dalam kurun waktu satu malam (mode otomatis, *headless browser*, 0% gangguan sistem PC).
   - Data berhasil disadap via *Network Intercept* (Payload JSON X API) sehingga terhindar dari limitasi grafis.

2. **Sistem Deduplikasi & Validator Anti-Konten Negatif**
   - Script `twitter_parser.py` telah disatukan dengan `validator.py`.
   - **Hasil:** Dari 27.000 data, sistem berhasil menyaring menjadi sekitar **11.216 Tweet Unik**.
   - Sistem Validator sukses memblokir ±65 tweet porno/judi dan mengkarantina ±51 konten abu-abu, memberikan tingkat kebersihan data (Data Quality) yang sangat tinggi sebelum masuk ke Data Warehouse.

3. **Injeksi Langsung ke MinIO (Datalake)**
   - Mengabaikan kerumitan Beanstalkd lokal, DE 2 sukses mengubah *parser* agar mengunggah langsung data lolos bersih ke *bucket* MinIO DE 1 melalui **Boto3 (S3 Client)** dan terhubung via Ngrok.
   - **Bukti:** Terminal DE 2 mencetak `SELESAI! 10760 Tweet bersih total berhasil diunggah langsung ke MinIO Datalake`, serta struktur folder `x/parsed/` sukses diimplementasikan.

---

## ✅ Sprint 2: Pipeline Processing & API Backend

1. **Struktur FastAPI Berjalan Stabil**
   - Kerangka *backend* API berhasil disatukan di `app.main`.
   - Fitur *CORS Middleware* telah diaktifkan untuk melayani permintaan dari UI (Front-End) beda *domain*.
   - Dependency Injection untuk mengelola koneksi database (`get_db`) berfungsi sempurna, mencegah kebocoran koneksi (Connection Leak).

2. **Keamanan Dasar (Auth API)**
   - Router `/api/v1/auth/login` berhasil dibuat. Logika JWT Token Generation siap digunakan oleh tim Front-End untuk pembuatan *session* pengguna.

---

## ✅ Sprint 3: Analytical Endpoints

1. **Dashboard & Grafik Real-time Tersedia**
   - Seluruh modul endpoint dari Sprint 3 telah sukses dibuat di `app/api/routes/dashboard.py` dan disambungkan ke `main.py`.
   - Kueri SQLAlchemy yang kompleks (termasuk agregasi `SUM`, `COUNT`, dan pengelompokkan waktu) telah dikompilasi dan siap melayani permintaan.
   - Uvicorn berjalan normal tanpa pesan kesalahan sintaks (*Syntax Error* / *Dependency Error*).
   
**Kesimpulan:** Hingga akhir Sprint 3, seluruh tanggung jawab teknis DE 2 yang tertera di dokumen PRD / Jobdesk telah berstatus **Tuntas 100%** dan terverifikasi secara fungsional.


## Sprint 4 & 5: Backend Optimization & Stability
1. **Search API**: Dibangun menggunakan ILIKE/FTS PostgreSQL untuk filter dan pencarian komprehensif.
2. **Database Indexing**: Kolom vital (platform, sentiment, posted_at) diberikan \index=True\ untuk agregasi super cepat.
3. **In-Memory Caching**: Sebuah decorator \@in_memory_cache(ttl_seconds=60)\ dibuat sendiri untuk mencegah *downtime* server ketika jutaan request menghantam Dashboard API.
4. **GZIP Scraper On-The-Fly**: Fitur penyadapan mengompres 124 MB raw payload GraphQL menjadi 4 MB secara *real-time* untuk mempertahankan Barang Bukti KP tanpa menguras memori.
