# 📊 Presentasi Final: Medallion Data Pipeline
**Topik:** Narative Trend Dashboard - DE 2 (Baihaqi)
**Waktu Presentasi:** ~15 Menit

---

## 🛝 Slide 1: Judul
**Teks Layar:**
> **Arsitektur Pemrosesan Data Cerdas & Backend API**
> Studi Kasus: Ekstraksi Tren Media Sosial X (Twitter)
> Oleh: Baihaqi (Data Engineer 2)

**Catatan Pembicara (Speaker Notes):**
"Selamat pagi Bapak/Ibu Dosen Penguji. Hari ini saya akan mempresentasikan bagian saya dalam proyek *Medallion Data Pipeline*, yaitu membangun arsitektur pemrosesan data (Parser) cerdas dan Web API berkinerja tinggi untuk memvisualisasikan tren dari media sosial."

---

## 🛝 Slide 2: Latar Belakang & Masalah
**Teks Layar:**
> **Tantangan Utama:**
> 1. API Resmi X (Twitter) ditutup/berbayar mahal.
> 2. Banyaknya data kotor (Bot, Judi, NSFW) yang merusak kualitas analisis NLP.
> 3. Visualisasi ratusan ribu data menyebabkan server lambat/lag.

**Catatan Pembicara (Speaker Notes):**
"Kita menghadapi 3 tantangan besar. Pertama, kami tidak punya akses ke API resmi Twitter. Kedua, data mentah Twitter itu ibarat sungai kotor, banyak sekali iklan judi, konten NSFW, dan bot yang bisa merusak model *Machine Learning* yang dibangun Data Scientist. Ketiga, bagaimana kita bisa menampilkan ratusan ribu data di *dashboard* tanpa membuat *server* nge- *lag*."

---

## 🛝 Slide 3: Solusi 1 - Network Interception (Scraper)
**Teks Layar:**
> **Headless Network Interception (Scraper)**
> - Menyadap lalu lintas *GraphQL API* X secara *real-time* (Man-in-the-Middle).
> - Menyimpan 100% *Payload Asli* ke file kompresi (GZIP On-The-Fly) sebagai Barang Bukti Otentik.
> - Efisiensi: 124 MB Data Mentah -> **~4 MB (Kompresi 96%)**.

**Catatan Pembicara (Speaker Notes):**
"Untuk mengatasi pemblokiran API, saya membangun sistem penyadap *Network Interception* menggunakan Playwright. Sistem ini menyamar sebagai aktivitas manusia dan menyadap *GraphQL payload* langsung dari browser, lalu menyimpannya dalam format GZIP secara *on-the-fly*. Ini menghasilkan efisiensi penyimpanan hingga 96%."

---

## 🛝 Slide 4: Solusi 2 - Smart 3-Tier Validator (Parser)
**Teks Layar:**
> **Pembersihan Data Otomatis dengan AI Rules (Parser)**
> 1. **Blocked (Score 10):** Konten Judi, Porno, Spam -> Langsung Dihancurkan.
> 2. **Flagged (Score >= 2):** Konten Mencurigakan -> Masuk Ruang Isolasi/Karantina.
> 3. **Allowed (Score 0-1):** Konten Bersih -> Lanjut ke Datalake (MinIO).

**Catatan Pembicara (Speaker Notes):**
"Data mentah kemudian masuk ke mesin *Parser* buatan saya. Saya merancang *Smart 3-Tier Validator* berbasis *RegEx Scoring*. Kalau sistem mendeteksi iklan judi atau konten dewasa, data itu otomatis dihancurkan. Hasilnya, Faiq (DE 1) hanya menerima data yang 100% halal dan bersih untuk dimasukkan ke *database* utama."

---

## 🛝 Slide 5: Solusi 3 - O(1) In-Memory Deduplication
**Teks Layar:**
> **Mencegah Data Ganda dengan Kecepatan Cahaya**
> - Algoritma Hash Map / Set.
> - Kecepatan Pencarian: **O(1) Kompleksitas Waktu**
> - Hasil: Mengirim puluhan ribu *tweet* tanpa ada satu pun duplikat ke MinIO.

**Catatan Pembicara (Speaker Notes):**
"Selain menyaring konten kotor, mesin *Parser* ini menggunakan struktur data *Hash Map* dengan kompleksitas pencarian O(1). Ini berarti, meskipun ada jutaan ID *tweet*, sistem bisa mendeteksi data ganda/duplikat dalam hitungan milidetik sebelum dikirim ke MinIO."

---

## 🛝 Slide 6: Solusi 4 - Backend Aggregation Push-Down
**Teks Layar:**
> **API Cepat Sekilat (Sub-Millisecond Response)**
> - **PostgreSQL Push-Down:** Menyerahkan kalkulasi matematis (Sum, Count) ke Engine Database.
> - **In-Memory Caching:** Menggunakan dekorator `@in_memory_cache` (TTL 60 detik) untuk *Endpoints Dashboard*.
> - Menghindari memori penuh (Out-Of-Memory) pada Python.

**Catatan Pembicara (Speaker Notes):**
"Untuk Backend, saya mendesain *Database Dictionary (ERD)* dan mengembangkan FastAPI. Rahasia kecepatannya ada dua: Pertama, saya menggunakan teknik *Aggregation Push-Down*, di mana kueri SQL yang berat dijalankan langsung oleh *Database Engine*, bukan oleh Python. Kedua, saya membuat sistem memori bayangan (*In-Memory Cache*) untuk *endpoint dashboard*, sehingga grafik memuat sangat cepat di UI Frontend."

---

## 🛝 Slide 7: Demo & Kesimpulan
**Teks Layar:**
> **Keberhasilan Proyek (Milestone)**
> - ✅ Auto-Pipeline berjalan otomatis (Cron-job) 24/7.
> - ✅ Berhasil menyedot dan memfilter **14.192 Data Bersih** dalam 1 hari.
> - ✅ Menyerahkan Dokumen API (Swagger) & ERD lengkap untuk Tim UI/UX.

**Catatan Pembicara (Speaker Notes):**
*(Di sini kamu tinggal membuka VSCode terminal dan mengetik `python cek_total_data.py` untuk pamer secara live, lalu tunjukkan file API_Documentation.md dan Database_Dictionary.md).*

"Sebagai penutup, sistem ini sekarang sudah berjalan 100% otomatis setiap 1,5 jam. Saat ini kami telah berhasil mengumpulkan lebih dari 14 ribu data murni tanpa campur tangan manusia. Terima kasih."
