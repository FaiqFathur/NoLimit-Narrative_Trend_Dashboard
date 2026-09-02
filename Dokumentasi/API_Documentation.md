# Dokumentasi Medallion API

Dokumentasi ini berisi penjelasan lengkap mengenai endpoint API yang tersedia pada backend Medallion Data Pipeline. API ini menggunakan arsitektur RESTful dan dikembangkan menggunakan FastAPI.

## Base URL
Secara default, saat dijalankan secara lokal: `http://localhost:8000/api/v1`

---

## 1. Authentication Endpoints

### 1.1. Login User
Digunakan untuk mendapatkan Access Token (JWT) yang diperlukan untuk mengakses endpoint privat.
- **URL**: `/auth/login`
- **Method**: `POST`
- **Headers**: `Content-Type: application/x-www-form-urlencoded`
- **Request Body (Form Data)**:
  - `username` (string, required): Username pengguna
  - `password` (string, required): Kata sandi pengguna
- **Response (200 OK)**:
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5...",
    "token_type": "bearer"
  }
  ```
- **Error Response (400 Bad Request)**:
  ```json
  {
    "detail": "Incorrect username or password"
  }
  ```

### 1.2. Register User
Mendaftarkan pengguna baru ke sistem.
- **URL**: `/auth/register`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Request Body (JSON)**:
  - `username` (string, required)
  - `email` (string, required)
  - `full_name` (string, required)
  - `password` (string, required)
- **Response (200 OK)**: Data pengguna yang baru dibuat (tanpa password)
- **Error Response (400 Bad Request)**: `{"detail": "The user with this username already exists..."}`

### 1.3. Get Current User
Mengambil profil pengguna yang sedang login. Membutuhkan Bearer Token.
- **URL**: `/auth/me`
- **Method**: `GET`
- **Headers**: `Authorization: Bearer <token>`
- **Response (200 OK)**:
  ```json
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Administrator",
    "is_active": true
  }
  ```

### 1.4. Logout
- **URL**: `/auth/logout`
- **Method**: `POST`
- **Response (200 OK)**: `{"message": "Successfully logged out..."}`

---

## 2. Dashboard Analytics Endpoints

*(Semua endpoint dashboard dilengkapi fitur in-memory cache dengan TTL 60 detik untuk mempercepat performa).*

### 2.1. Dashboard Overview (KPI)
Menampilkan ringkasan total (posts, topics, engagement) dari seluruh data yang ada.
- **URL**: `/dashboard/overview`
- **Method**: `GET`
- **Response (200 OK)**:
  ```json
  {
    "kpi": {
      "total_posts": 14192,
      "total_topics": 520,
      "total_engagement": 532014
    },
    "breakdown": {
      "likes": 250000,
      "comments": 150000,
      "shares": 80000,
      "views": 52014
    }
  }
  ```

### 2.2. Trend Timeline
Menampilkan deret waktu jumlah publikasi harian. Cocok untuk visualisasi Line Chart.
- **URL**: `/dashboard/timeline`
- **Method**: `GET`
- **Query Parameters**:
  - `days` (integer, optional, default: 7): Jumlah hari ke belakang.
- **Response (200 OK)**:
  ```json
  {
    "days_requested": 7,
    "timeline": [
      { "date": "2026-09-01", "count": 1205 },
      { "date": "2026-09-02", "count": 3003 }
    ]
  }
  ```

### 2.3. Sentiment Distribution
Menampilkan distribusi sentimen dari seluruh data teks (untuk visualisasi Pie/Donut chart).
- **URL**: `/dashboard/sentiment`
- **Method**: `GET`
- **Response (200 OK)**:
  ```json
  {
    "positive": 4520,
    "neutral": 6300,
    "negative": 3100,
    "unlabeled": 272
  }
  ```

### 2.4. Top Trending Topics
Menampilkan daftar topik (keyword) teratas yang paling banyak dibicarakan.
- **URL**: `/dashboard/topics`
- **Method**: `GET`
- **Query Parameters**:
  - `limit` (integer, optional, default: 10): Jumlah topik yang ingin ditampilkan.
- **Response (200 OK)**:
  ```json
  {
    "limit": 10,
    "trending_topics": [
      {
        "id": 1,
        "name": "#Pilpres2029",
        "post_count": 8450,
        "keywords": "pilpres, presiden, pemilu"
      }
    ]
  }
  ```

---

## 3. Global Search API

### 3.1. Filtered Search
Melakukan pencarian penuh (Full-Text Search) menggunakan parameter khusus (ILIKE db native).
- **URL**: `/api/search` *(Perhatikan: Endpoint ini diluar prefix `/v1`)*
- **Method**: `GET`
- **Query Parameters**:
  - `q` (string, optional): Kata kunci pencarian (mencari di *content* dan *author_username*)
  - `platform` (string, optional): Filter platform (misal: `x`, `tiktok`)
  - `sentiment` (string, optional): Filter sentimen (`positive`, `negative`, `neutral`)
  - `start_date` (datetime, optional): Batas waktu awal (format: `YYYY-MM-DDTHH:MM:SS`)
  - `end_date` (datetime, optional): Batas waktu akhir
  - `limit` (integer, optional, default: 50, max: 500)
  - `skip` (integer, optional, default: 0)
- **Response (200 OK)**: Array list berupa objek JSON dari `PostResponse`.

---

> [!TIP]
> Semua endpoint API ini (dan skema data lengkapnya) juga bisa diakses interaktif langsung melalui dokumentasi Swagger UI otomatis FastAPI.
> Cukup buka browser dan arahkan ke: **`http://localhost:8000/docs`** saat server sedang berjalan.
