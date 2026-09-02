# NoLimit Narrative Trend Dashboard (Data Engineering)

Ini adalah *codebase* utama untuk subsistem Data Engineering & Backend dari proyek **NoLimit Narrative Trend Dashboard**. Repositori ini berisi arsitektur Pipa Data (Data Pipeline) lengkap dan API Backend berbasis FastAPI yang dikerjakan hingga **Sprint 6**.

## 🏗️ Arsitektur Sistem (Sprint 1 - 6)

Sistem ini terbagi menjadi dua komponen utama:

### 1. Data Pipeline (Scraper & Parser)
- **Playwright Batch Interceptor**: Menangkap respons GraphQL (JSON) secara langsung dari peramban (Headless X/Twitter) tanpa perlu kredensial API resmi.
- **Smart 3-Tier Validator**: Sistem penyaringan otomatis menggunakan RegEx untuk membuang konten NSFW, Perjudian (Slot), dan Spam.
- **O(1) Deduplication System**: Mencegah data ganda (*duplicate*) masuk ke dalam Datalake dengan memori super hemat (Hash Map).
- **Auto-Pipeline Scheduler**: Berjalan secara mandiri (*background job*) di jam-jam tertentu (00:30, 02:00, ..., 23:00) untuk memanen data secara otomatis dan memindahkannya ke MinIO Datalake.

### 2. Backend API (FastAPI)
- **FastAPI Modular**: Struktur folder skala korporasi (`routes`, `models`, `schemas`, `core`).
- **PostgreSQL & Alembic**: Skema *database* berelasi yang dikelola sepenuhnya oleh Alembic Migration. Siap dieksekusi dengan `alembic upgrade head`. Termasuk indeks performa tinggi pada `tweet_id` dan `created_at`.
- **Search & Dashboard Endpoints**: API performa tinggi yang merangkum miliaran baris data menjadi analitik tren (Volume, Sentimen, Top Keyword).
- **In-Memory Caching (TTL)**: Mencegah *Database Crash* ketika *Dashboard* memuat ulang grafik. Data *cache* bertahan selama 60 detik sebelum memuat ulang kueri SQL.
- **Authentication**: Sistem Login JWT dengan enkripsi *Bcrypt* untuk keamanan Dasbor UI.

---

## 🚀 Cara Instalasi & Menjalankan (Untuk Tim Internal)

### 1. Inisialisasi Database (PostgreSQL & Neo4J)
Pastikan Docker Desktop menyala, lalu jalankan:
```bash
cd Backend
docker-compose up -d
```
Setelah *database* menyala, bangun seluruh struktur tabel PostgreSQL dengan Alembic:
```bash
python -m alembic upgrade head
```

### 2. Menjalankan Backend API
Buka terminal di folder `Backend` dan pasang *Virtual Environment*:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
Salin `.env.example` menjadi `.env` lalu nyalakan server:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Buka Browser ke: **http://127.0.0.1:8000/docs** untuk melihat Dokumentasi API interaktif (Swagger UI).
