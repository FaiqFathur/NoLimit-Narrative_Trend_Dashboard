# 📝 Pembagian Beban Kerja Tim Data Engineer (Faiq & Baihaqi)
**Durasi Proyek:** 11 Agustus – 9 November 2026 (6 Sprint)

Berikut adalah pembagian tugas spesifik untuk tim Data Engineer agar beban kerja seimbang antara Anda (Faiq) dan rekan Anda (Baihaqi), berdasarkan timeline PRD resmi.

---

### Sprint 0: Setup & Planning (11–23 Agustus)
Fokus: Persiapan lingkungan kerja dan infrastruktur dasar.

**DE 1 (Faiq) - Core Storage & Queue**
- `[x]` **Repository Setup:** Inisialisasi GitHub/GitLab repository dengan struktur folder standar.
- `[x]` **Docker Compose (Laptop 1):** Membuat file `docker-compose.yml` untuk infrastruktur *core* (PostgreSQL, MinIO, Beanstalkd).

**DE 2 (Baihaqi) - Search, Graph, & Database Schema**
- `[x]` **Docker Compose (Laptop 2):** Setup infrastruktur berbasis JVM (Neo4J, Elasticsearch).
- `[x]` **Alembic Setup:** Inisialisasi SQLAlchemy dan Alembic untuk manajemen skema PostgreSQL.
- `[x]` **Schema Design:** Membuat tabel dasar (`posts`, `topics`, `entities`, `users`) di PostgreSQL & setup *constraints* Neo4J.

---

### Sprint 1: Data Foundation (25 Agustus – 6 September)
Fokus: Pengumpulan data mentah dan *ingestion* ke Data Lake.

**DE 1 (Faiq) - TikTok & IG Pipeline**
- `[x]` **TikTok & IG Scraper:** Mengembangkan mekanisme *intercept* (Chrome Extension / Mitmproxy) untuk menangkap data TikTok dan Instagram.
- `[x]` **MinIO Ingestion Worker:** Membuat `parser_worker.py` untuk mengonsumsi JSON dari Beanstalkd, menormalisasikannya, dan mengunggahnya ke MinIO.

**DE 2 (Baihaqi) - X (Twitter) Pipeline**
- `[x]` **X (Twitter) Scraper:** Membuat script Python/Playwright untuk mengambil data dari X.
- `[x]` **Queue Publisher X:** Memastikan hasil *scraping* X masuk ke Beanstalkd dengan format yang seragam.

---

### Sprint 2: Pipeline Processing & API Backend (8–20 September)
Fokus: Mengalirkan data ke database dan membangun fondasi REST API.

**DE 1 (Faiq) - Data Warehouse Ingestion**
- `[ ]` **PostgreSQL Inserter:** Menambahkan modul di *Worker* untuk memasukkan data yang sudah dinormalisasi ke tabel PostgreSQL.
- `[ ]` **Elasticsearch Indexer:** Mengirim data teks (caption) ke Elasticsearch untuk keperluan *full-text search*.
- `[ ]` **Deduplication Engine:** Mencegah data ganda (*duplicate post*) masuk ke database.

**DE 2 (Baihaqi) - FastAPI Foundation**
- `[x]` **FastAPI Setup:** Membuat kerangka *backend* API (konfigurasi CORS, Router, Middleware, Dependency Injection untuk DB).
- `[x]` **Auth Endpoints:** Membuat endpoint login/logout menggunakan JWT/Session sederhana.

---

### Sprint 3: NLP Integration & API Lanjutan (22 September – 4 Oktober)
Fokus: Integrasi model AI dan endpoint data analitik.

**DE 1 (Faiq) - NLP Pipeline Integration**
- `[ ]` **Model Connector:** Menghubungkan *Parser Worker* dengan API Model IndoBERT (buatan tim DS) agar setiap *post* mendapatkan label sentimen otomatis sebelum masuk database.
- `[ ]` **Error Handling AI:** Menangani skenario jika model AI lambat merespons atau *timeout* (misal: fitur *retry* di Beanstalkd).

**DE 2 (Baihaqi) - Analytical Endpoints**
- `[x]` **Dashboard API:** Membuat endpoint `/api/dashboard/overview` dan `/api/dashboard/timeline`.
- `[x]` **Sentiment & Topic API:** Membuat endpoint agregasi untuk menampilkan distribusi sentimen dan *trending topics*.

---

### Sprint 4: Knowledge Graph & Full Integration (6–18 Oktober)
Fokus: Visualisasi relasi data tingkat lanjut dan optimasi.

**DE 1 (Faiq) - Graph & Performance**
- `[ ]` **Graph Endpoints:** Membuat endpoint `/api/graph/nodes` dan `/api/graph/edges` yang langsung mengambil relasi (Cypher query) dari Neo4J.
- `[ ]` **Neo4J Query Tuning:** Mengoptimalkan kueri traversi graf agar bisa merender ratusan *node* di bawah 3 detik.

**DE 2 (Baihaqi) - Search & Filter API**
- `[x]` **Global Search API:** Membangun endpoint `/api/search` menggunakan Elasticsearch (pencarian kata kunci cepat).
- `[x]` **PostgreSQL Indexing:** Membuat indeks database pada kolom yang sering difilter (seperti `platform`, `created_at`, `sentiment`).

---

### Sprint 5: Testing & Edge Cases (20 Oktober – 1 November)
Fokus: Uji coba beban, stabilitas, dan perbaikan *bug*.

**DE 1 (Faiq) - Scraper & Pipeline Resilience**
- `[ ]` **Rate Limiting Handling:** Menambahkan logika *backoff/sleep* otomatis jika scraper IG/TikTok terkena pemblokiran sementara.
- `[ ]` **Worker Optimization:** Memastikan *throughput* parser mencapai target ≥ 100 post/menit tanpa membuat server macet.

**DE 2 (Baihaqi) - API & Backend Stability**
- `[x]` **API Caching (Opsional):** Mengimplementasikan *Redis* atau *in-memory cache* pada endpoint yang berat (seperti agregasi grafik bulanan).
- `[ ]` **Bug Fixing Backend:** Memperbaiki celah/kutu dari laporan hasil *testing* bersama tim Front-End dan UI/UX.

---

### Sprint 6: Finalisasi & Handover (3–9 November)
Fokus: Dokumentasi akhir dan penyerahan sistem.

**DE 1 (Faiq) - Infrastructure Handover**
- `[ ]` **Dokumentasi Pipeline:** Membuat diagram *Data Lineage* (aliran data dari scraper -> MinIO -> PostgreSQL -> Frontend).
- `[ ]` **Panduan Deployment:** Menulis instruksi cara memutar ulang sistem ini di server baru menggunakan *Docker Compose*.

**DE 2 (Baihaqi) - Code Handover**
- `[x]` **API Documentation:** Merapikan dokumentasi Swagger UI / OpenAPI (memberikan deskripsi jelas untuk tiap parameter *request*).
- `[x]` **Database Dictionary:** Mendokumentasikan *Entity Relationship Diagram* (ERD) dan skema Graph Neo4J.
- `[ ]` **Presentasi Akhir:** Menyiapkan materi teknis *backend* untuk demo akhir.
