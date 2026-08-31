# Narrative Trend Dashboard

Proyek analitik untuk memantau, menganalisis, dan memvisualisasikan tren narasi di media sosial (X, TikTok, Instagram) yang dibangun oleh tim Data Engineer dan Data Scientist untuk internal PT NoLimit Indonesia.

## Struktur Direktori

- `backend/`: REST API menggunakan FastAPI (Python).
- `scrapers/`: Script web scraper untuk TikTok, Instagram, dan X.
- `pipeline/`: Message queue consumers (Beanstalkd) dan ingestion scripts (ke MinIO & DB).
- `infrastructure/`: Konfigurasi Docker Compose untuk dependensi (PostgreSQL, Neo4J, Elasticsearch, MinIO, Beanstalkd).
- `frontend/`: Aplikasi antarmuka menggunakan React + TypeScript.

## Dependensi Infrastruktur
- PostgreSQL
- Neo4J
- Elasticsearch
- MinIO
- Beanstalkd
