# Checklist Integrasi & Penyesuaian Proyek
Dokumen ini berisi daftar hal-hal yang **harus disesuaikan, dikoordinasikan, dan diselesaikan** agar pekerjaan antara DE 1 (Faiq), DE 2 (Baihaqi), dan tim Frontend bisa terintegrasi dengan sempurna.

## 🔴 Tindakan Mendesak untuk DE 2 (Baihaqi)
Hal-hal yang harus segera kamu sesuaikan di *local env*-mu:
- [ ] **Jalankan Database Migration:** Server PostgreSQL kita saat ini **mati**. Begitu Faiq menyalakan Docker PostgreSQL, kamu **wajib** menjalankan perintah `python -m alembic revision --autogenerate -m "Add index"` dan `python -m alembic upgrade head` agar fitur *Search API* (Sprint 4) bisa bekerja tanpa *error*.
- [ ] **Ubah Konfigurasi `.env`:** Pastikan kredensial DB di file `.env` Backend mengarah ke port PostgreSQL yang benar (misal `5432`).
- [ ] **Validasi Token (Sprint 2):** Uji coba *endpoint* `/api/auth/login` menggunakan kredensial buatanmu, lalu pastikan token JWT yang keluar bisa dipakai untuk mengakses `/api/dashboard/overview`.

## 🟡 Penyesuaian dari Sisi DE 1 (Faiq)
Hal-hal yang harus Faiq lakukan agar nyambung dengan kodinganmu:
- [ ] **Dockerisasi Database:** Faiq harus memastikan *container* PostgreSQL menyala dengan user/password yang sesuai dengan `.env` Backend milikmu.
- [ ] **PostgreSQL Inserter (Sprint 2):** Faiq belum membuat skrip yang membaca 11.189 data JSON di MinIO (hasil *Scraping*-mu) lalu memasukannya (*insert*) ke dalam PostgreSQL milikmu. Jika ini belum dilakukan, Dashboard API-mu akan mengembalikan nilai 0.
- [ ] **Graph (Neo4J):** Faiq harus mengonfigurasi *pipeline* yang mengekstrak relasi entitas ke Neo4J, karena fitur *Graph Endpoint* belum bisa kita bangun tanpa ada data di Neo4J.

## 🔵 Penyesuaian dari Sisi Front-End
Tim UI/UX dan Front-End harus menyesuaikan hal berikut dari sisi *client*:
- [ ] **Header Authorization:** Front-End wajib menyisipkan `Authorization: Bearer <token>` di setiap pemanggilan API Dashboard dan Search.
- [ ] **Format Global Search:** Fitur *Search Bar* di UI sekarang bisa menggunakan endpoint `/api/search?q=keyword&platform=x`. Front-End tidak perlu melakukan pencarian manual di *client-side*.
- [ ] **Caching Awareness:** Beritahu Front-End bahwa *Dashboard API* sekarang memiliki *cache* (TTL 60 detik). Artinya, jika ada data baru masuk, grafik mungkin baru akan *update* 1 menit kemudian. Tidak perlu panik karena ini disengaja untuk menjaga server tidak *crash*.

## 🟢 Yang Sudah 100% Selesai & Tinggal Pakai
- ✔️ **X (Twitter) Scraper & Pipeline:** Pipeline *headless* + GZIP kompresi + 3-Tier Validator sudah anti-bocor dan menghasilkan ribuan data super padat per sesi.
- ✔️ **Backend Core & Auth:** FastAPI, JWT Token, dan koneksi SQLAlchemy sudah kokoh.
- ✔️ **Analytical API:** Seluruh *endpoint* Dashboard (Overview, Timeline, Sentiment, Topics) sudah memiliki *query* efisien (`func.sum`, `group_by`) dengan dukungan *In-Memory Caching*.
- ✔️ **Search & Filter:** Endpoint Search siap dengan PostgreSQL FTS (ILIKE/tsvector).
