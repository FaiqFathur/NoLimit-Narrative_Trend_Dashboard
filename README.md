# Medallion Data Pipeline - Sprint 1 & 2 (Perfect Recovery)

Ini adalah *codebase* utama untuk proyek Data Warehouse X (Twitter) menggunakan arsitektur Medallion. Pipeline ini dirancang tahan banting dengan sistem moderasi konten dan message broker.

## Arsitektur

- **Scrapers:** Berisi *Interceptor* untuk menangkap respons JSON GraphQL dari X, memvalidasi konten menggunakan **Smart Validator 3-Tingkat**, lalu memasukkannya ke Beanstalkd (*Dynamic Tube Routing*).
- **Backend:** Menyediakan fondasi *FastAPI Modular* (Sprint 2) yang tersambung ke PostgreSQL & Neo4j. Memiliki rute Otentikasi (`/api/auth`) menggunakan JWT dan sandi bcrypt.

---

## Live Acceptance Evidence (Bukti Berjalan Nyata)

### 1. Beanstalkd Queue Stats (Sprint 1)
Ketika Anda menjalankan `twitter_parser.py`, di bagian paling bawah akan tercetak langsung statistik aktual dari dalam *server* Beanstalkd (membuktikan antrean benar-benar terisi):
```
--- Beanstalkd Live Statistics ---
Tube 'raw-data': 0 ready jobs, 1912 total inserted.
Tube 'quarantine-data': 0 ready jobs, 0 total inserted (Tube is empty/not created).
```

### 2. FastAPI Authentication Integration Test (Sprint 2)
Kami telah memvalidasi penuh kesinambungan antara Pydantic Schema API dengan Model Database `User` (berbasis `Integer ID` dan `password_hash`).
Endpoint Register -> Login -> Me -> Logout berjalan sukses dengan pengembalian `200 OK`.

---

## Cara Menjalankan FastAPI Server

1. Buka terminal dan arahkan ke folder `Backend`
2. Pasang *virtual environment* jika belum:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Atur *environment variables* dengan membuat file `.env` (salin dari `.env.example`). Pastikan mengisi `SECRET_KEY` dengan teks acak panjang.
4. Terapkan migrasi database (termasuk kolom email & is_active terbaru):
   ```bash
   alembic upgrade head
   ```
5. Nyalakan server Uvicorn:
   ```bash
   .venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
6. Buka Browser ke: **http://127.0.0.1:8000/docs** untuk melihat Swagger UI yang cantik.
