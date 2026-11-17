# Nayyen Daily Brief

## Tujuan
Aplikasi agregator berita AI yang mengumpulkan berita dari beberapa sumber,
merangkumnya dengan LLM, lalu mengirim daily digest ke email pribadiku setiap
hari. Digest berisi cuplikan pendek beserta link ke sumber aslinya.

## Sumber data
- **Channel YouTube**: aku punya daftar channel, lalu video terbarunya
  diambil lewat RSS feed YouTube.
- **Blog (OpenAI, Anthropic)**: aku punya daftar URL yang di-scrape.

## Struktur data (PostgreSQL + SQLAlchemy)
- Tabel `sources`: daftar sumber (channel YouTube dan URL blog).
- Tabel `articles`: artikel/video yang diambil dari sumber.
- Model didefinisikan dengan SQLAlchemy, dan tabel juga dibuat lewat SQLAlchemy.

## Alur proses
1. Ambil konten terbaru dari semua sumber, lalu simpan ke tabel `articles`.
2. Jalankan daily digest: ambil semua artikel dalam rentang waktu tertentu.
3. LLM merangkum artikel-artikel tersebut.
4. Agent dengan system prompt berisi minat/insight user menyusun digest
   sesuai minatku.
5. Hasilnya cuplikan pendek + link ke sumber asli.
6. Digest dikirim ke email pribadiku.

## Tech stack
- Backend: Python
- Database: PostgreSQL + SQLAlchemy
- LLM: OpenAI
- Lokal: Docker
- Deploy: Render

## Struktur folder
- `app/`: semua logika aplikasi
- `docker/`: setup Postgres minimal sebagai titik awal

## Deploy dan jadwal
Dirancang supaya mudah dideploy ke Render dan dijadwalkan berjalan
setiap 24 jam (ambil konten, buat digest, kirim email).

## Cara membangun
Mulai dari yang minimal (setup Postgres di Docker), lalu bertahap menambah
scraper, pipeline, agent digest, email, dan deployment.