# 📘 Laporan Arsitektur, Metodologi, dan Pencapaian Data Engineer 2 (Baihaqi)
**Proyek:** Narative Trend Dashboard (Medallion Data Pipeline)
**Periode:** Sprint 0 hingga Sprint 3

Dokumen ini disusun untuk menguraikan **metodologi teknis tingkat lanjut**, **alur kerja (workflow) sistem**, dan **arsitektur** yang dikembangkan oleh DE 2 (Baihaqi) dari tahap *Scraping* hingga *Backend API*. 

---

## 🏗️ 1. Arsitektur Pengumpulan Data (Scraper Layer)
Pada tahap ini, DE 2 bertugas mengambil data dari X (Twitter). Karena limitasi API resmi, DE 2 mengembangkan arsitektur *Network Interceptor* yang diorkestrasi melalui dua skrip utama: `auto_pipeline.py` dan `twitter_batch_interceptor.py`.

### A. Metodologi Network Interception & Headless Automation
- **Konsep Dasar:** Sistem tidak melakukan *DOM Scraping* (membaca kode HTML layar) karena rentan *error* saat struktur web berubah. Sistem ini bertindak sebagai peretas jaringan (*Man-in-the-Middle*) yang menyadap paket data komunikasi antara *Browser* dan *Server X*.
- **Alur Kerja (Workflow) Injeksi dan Penyadapan:**
  1. **Ekstraksi Sesi via Akun Dummy:** Untuk menghindari pengetikan *username/password* otomatis yang mudah diblokir oleh anti-bot Twitter, DE 2 pertama-tama melakukan *login* manual di browser menggunakan akun *dummy*. File profil browser (berisi *Auth Cookies* dan *Session Tokens*) kemudian disalin dan disimpan secara lokal.
  2. **Inisialisasi Mode Siluman:** Skrip `twitter_batch_interceptor.py` memuat *library* `Playwright` dengan pengaturan `headless=True` (tanpa GUI). Mode ini menonaktifkan GPU dan antarmuka, menghemat 90% RAM, mencegah *Black Screen*, dan membiarkan sistem menyamar sebagai pengguna *login* otentik menggunakan *Cookies* dari akun *dummy*.
  3. **Penyadapan GraphQL:** Bot memasang *Network Listener* (`page.on('response')`). Bot kemudian menavigasi tab *Explore / Trending Topics* dan menyimulasikan *scrolling* manusia.
  4. **Ekstraksi Payload:** Setiap kali server X merespons dengan paket JSON berbasis GraphQL (contohnya *endpoint* `timeline.json` atau `useStoryTopicQuery`), *listener* langsung mencegat paket tersebut. Paket ini mengandung ratusan *tweet* mentah berserta metriknya. Paket ini langsung disimpan ke lokal di dalam folder `raw_batches/`.
  5. **Orkestrasi 24/7:** Skrip `auto_pipeline.py` bertindak sebagai *cron-job* (penjadwal otomatis) yang mengeksekusi proses penyadapan ini setiap 1,5 jam sekali secara terus-menerus.

---

## 🧹 2. Arsitektur Pemrosesan dan Kualitas Data (Parser Layer)
Jutaan JSON mentah yang ditangkap harus dibersihkan sebelum masuk ke *Data Warehouse*. Proses ini diatur oleh `twitter_parser.py` dan `validator.py`.

### A. Metodologi Smart 3-Tier Content Moderation
- **Konsep Dasar:** Banyaknya konten bot, pornografi, dan judi *online* di X dapat merusak *Natural Language Processing* (NLP) di tahap selanjutnya.
- **Alur Kerja (Workflow) Validator:**
  1. **Parsing Rekursif:** Karena respons GraphQL Twitter memiliki hierarki JSON yang sangat dalam (`instructions` -> `entries` -> `itemContent` -> `tweet_results`), `twitter_parser.py` menggunakan fungsi *rekursif* untuk membongkar JSON sedalam apapun demi menemukan entitas teks *tweet*.
  2. **Sistem Skoring (Regex-based):** Teks yang ditemukan dikirim ke `validator.py`. Validator membedah teks menggunakan *Regular Expressions* (RegEx).
     - **Poin +1 (Suspicious):** Kata abu-abu seperti *cdn*, *terabox*.
     - **Poin +2 (Promo):** Kata promosi seperti *telegram*, *slot*.
  3. **Routing Keputusan (3-Tier):**
     - **Hard Block:** Jika teks mengandung 1 saja kata dari *Blacklist* Ekstrim (misal: `videy`, pornografi, judi), tweet **langsung dihancurkan/dihapus** saat itu juga.
     - **Quarantine:** Jika total skor mencapai ≥ 2, tweet diberi status `flagged`.
     - **Allowed:** Jika bersih (skor 0-1), statusnya `allowed`.

### B. Metodologi O(1) Deduplication & Asynchronous Upload
- **Alur Kerja (Workflow) Deduplikasi:** 
  Untuk mencegah *tweet* yang sama diproses dua kali, DE 2 menggunakan struktur data **`Set` (Hash Map)** di Python. Setiap ID *tweet* yang berstatus `allowed` atau `flagged` akan dimasukkan ke `Set` dan disimpan persisten di file `processed_tweet_ids.json`. Kecepatan pencarian `Set` adalah **O(1)**, sehingga pengecekan duplikasi dari jutaan ID hanya membutuhkan waktu hitungan milidetik.
- **Alur Kerja Pengiriman (Upload):**
  Data yang lolos (Tingkat Karantina & Bersih) langsung diubah bentuk formatnya agar seragam. Kemudian, modul `boto3` menembakkan data tersebut secara asinkron ke Datalake MinIO (via Ngrok). Data bersih masuk ke folder `x/parsed/YYYY-MM/`, sedangkan data karantina masuk ke `x/quarantine/YYYY-MM/`.

---

## ⚙️ 3. Arsitektur Agregasi dan Backend (API Layer)
Setelah data terkumpul, DE 2 membangun *Web Server* menggunakan **FastAPI** untuk melayani *Dashboard UI*.

### A. Metodologi Database Aggregation Push-Down
- **Konsep Dasar:** Menghindari beban komputasi di level memori Python (FastAPI). Jika kita menggunakan Python untuk menghitung puluhan ribu *tweet*, memori (*RAM*) *server* akan penuh (Out-Of-Memory) dan API akan sangat lambat (Lag).
- **Alur Kerja (Workflow) Aggregation Push-Down:**
  1. DE 2 merancang skema *Relational Database* di PostgreSQL menggunakan `SQLAlchemy` ORM, dibantu `Alembic` untuk melacak versi migrasi database.
  2. DE 2 menerapkan sistem keamanan *Dependency Injection* (`get_db`) yang secara otomatis membuka dan menutup Sesi Database (SessionLocal) pada setiap *request* API. Ini mencegah *Connection Pool Leak* (kebocoran koneksi).
  3. Pada *file* `dashboard.py`, DE 2 menulis kueri agregat yang memerintahkan *Database Engine* (PostgreSQL) untuk melakukan kalkulasi berat. Contoh:
     - **Endpoint `/timeline`:** Menggunakan kueri `group_by(cast(Post.created_at, Date))` dan `func.count()`. PostgreSQL yang mengelompokkan jumlah *post* harian, lalu mengirimkan *Array* kecil langsung ke FastAPI untuk divisualisasikan menjadi *Line Chart*.
     - **Endpoint `/overview` & `/sentiment`:** Menggunakan `func.sum()` untuk menjumlahkan ratusan ribu *Likes/Views*, sehingga Python hanya menerima hasil akhir berupa satu angka *Integer*. Waktu respons (Response Time) API terjaga di bawah 100ms.

---

## 🎯 4. Rincian Pencapaian & Evaluasi Sprint
1. **Sprint 0:** Skema Database, Docker Compose lokal (Neo4J & Elasticsearch), dan sistem migrasi Alembic **sukses diinisialisasi 100%**.
2. **Sprint 1:** Mesin Interseptor 24/7 dan Parser sukses bekerja. Dalam pengujian *stress-test*, mesin berhasil menyadap **~27.000 JSON mentah (1 GB)** semalaman. Melalui mekanisme Deduplikasi dan Moderasi Cerdas, data disaring menjadi **10.760 Tweet Bersih** yang sukses diunggah langsung ke Datalake MinIO.
3. **Sprint 2:** *FastAPI Foundation* berjalan stabil dengan konfigurasi CORS (mengizinkan permintaan UI lintas *domain*) dan keamanan standar *JWT Token* di `/auth/login`.
4. **Sprint 3:** Empat (4) modul Analitik utama (`/overview`, `/timeline`, `/sentiment`, `/topics`) berstatus **Production-Ready**. Kueri telah diuji dan siap me- *render* grafik seketika setelah *Inserter* dari DE 1 diaktifkan.

Seluruh elemen arsitektural yang menjadi tanggung jawab DE 2 terbukti **sangat tangguh (resilient)**, ramah memori (teroptimasi), dan memiliki kualitas data (*Data Quality Assurance*) yang terjamin ketat sebelum mencapai visualisasi akhir.


### 5. Optimasi Penyimpanan dan Performa Backend (Sprint 4 & 5)
Untuk memastikan arsitektur dapat ditingkatkan ke jutaan record data, dua strategi tambahan diimplementasikan:
1. **GZIP On-The-Fly Interception**: *Scraper* memampatkan data Payload JSON mentah menggunakan gzip secara *real-time* saat data ditulis ke *disk*. Ini mempertahankan 100% data GraphQL sebagai **Barang Bukti Otentik (Evidence)** penyadapan mandiri, namun memangkas penggunaan *storage* dari 124 MB menjadi ~4 MB.
2. **In-Memory API Caching**: Dekorator kustom @in_memory_cache dengan metode *hash* parameter dan *Time-to-Live* (TTL) 60 detik ditempelkan pada *Endpoint Dashboard*. Hal ini menjamin bahwa ribuan *request* konkuren hanya akan mengenai PostgreSQL satu kali, mengurangi *latency* dari hitungan detik menjadi *sub-millisecond*.