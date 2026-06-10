# IPTV Auto-Scraper

Sistem otomatis untuk mengumpulkan dan mengkategorikan stream IPTV dari berbagai sumber publik, dengan fokus pada event sepakbola, event tarung (UFC/MMA/boxing), dan TV lokal Indonesia.

## 🎯 Fitur

- **Auto-fetch** dari playlist M3U publik (doms9/iptv, rosdiyanto/iptv)
- **Web scraping** dari situs streaming live (streamcenter, fawa, roxie)
- **Kategorisasi otomatis** ke 3 playlist terpisah:
  - `sepakbola.m3u` - Event sepakbola (liga Eropa, internasional, dll)
  - `tarung.m3u` - Event tarung (UFC, MMA, boxing, WWE)
  - `tv_lokal.m3u` - TV lokal Indonesia (RCTI, SCTV, Indosiar, TVRI, dll)
- **Health check** otomatis untuk mendeteksi stream mati
- **GitHub Actions** untuk otomatisasi (scraper tiap 2 jam, health check 3x sehari)
- **Deduplikasi** URL untuk menghindari duplikasi stream

## 📊 Hasil Run Saat Ini

| Playlist | Entries | Status |
|----------|---------|--------|
| sepakbola.m3u | 72 | ✅ Aktif |
| tarung.m3u | 12 | ✅ Aktif |
| tv_lokal.m3u | 127 | ✅ Aktif |

## 🏗️ Struktur Proyek

```
iptv/
├── main.py                          # Orchestrator utama
├── fetcher.py                       # Fetch M3U dari sumber publik
├── categorizer.py                   # Klasifikasi stream ke 3 kategori
├── m3u_writer.py                    # Generate file M3U output
├── health.sh                        # Health check stream (bash)
├── pyproject.toml                   # Dependencies Python
├── scrapers/
│   ├── __init__.py
│   ├── utils.py                     # Network, cache, logger utilities
│   ├── streamcenter.py              # Scrape streamcenter.xyz
│   ├── fawa.py                      # Scrape fawanews.sc
│   └── roxie.py                     # Scrape roxiestreams.info
├── output/
│   ├── sepakbola.m3u                # Output: event sepakbola
│   ├── tarung.m3u                   # Output: event tarung
│   └── tv_lokal.m3u                 # Output: TV lokal Indonesia
├── cache/                           # Cache hasil scrape (JSON)
└── .github/workflows/
    ├── scraper.yml                  # Auto-run scraper tiap 2 jam
    └── health.yml                   # Health check 3x sehari
```

## 🚀 Cara Install

### Prasyarat
- Python 3.11+
- uv (Python package manager)

### Install Dependencies

```bash
# Install uv jika belum ada
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync
```

## 📝 Cara Menggunakan

### Jalankan Scraper Manual

```bash
uv run python main.py
```

Output akan tersimpan di folder `output/`:
- `sepakbola.m3u`
- `tarung.m3u`
- `tv_lokal.m3u`

### Jalankan Health Check

```bash
chmod +x health.sh
bash health.sh
```

Script ini akan:
- Cek semua URL di 3 file M3U
- Update `readme.md` dengan status stream (working/dead)
- Generate laporan stream mana yang mati

### Deploy ke GitHub

```bash
# Initialize git repo
git init
git add .
git commit -m "Initial commit: IPTV auto-scraper"

# Buat repo baru di GitHub, lalu:
git remote add origin https://github.com/USERNAME/REPO.git
git branch -M main
git push -u origin main
```

Setelah push, GitHub Actions akan otomatis:
- Menjalankan scraper tiap 2 jam
- Menjalankan health check 3x sehari (08:30, 14:30, 20:30 UTC)

## 🔧 Konfigurasi

### Tambah Sumber M3U Baru

Edit `fetcher.py`:

```python
SOURCES = {
    "doms9": "https://s.id/d9M3U8",
    "rosdiyanto": "https://raw.githubusercontent.com/rosdiyanto/iptv/main/full.m3u",
    # Tambah sumber baru di sini:
    "sumber_baru": "https://example.com/playlist.m3u",
}
```

### Tambah Scraper Baru

1. Buat file baru di `scrapers/` (contoh: `scrapers/newsite.py`)
2. Implementasi fungsi `scrape()` yang mengisi `urls` dict
3. Import dan tambahkan ke `main.py`:

```python
from scrapers import newsite

async def run_scrapers() -> None:
    httpx_tasks = [
        asyncio.create_task(fawa.scrape()),
        asyncio.create_task(streamcenter.scrape()),
        asyncio.create_task(roxie.scrape()),
        asyncio.create_task(newsite.scrape()),  # Tambah di sini
    ]
    await asyncio.gather(*httpx_tasks)
```

### Ubah Jadwal GitHub Actions

Edit `.github/workflows/scraper.yml`:

```yaml
on:
  schedule:
    - cron: "0 */2 * * *"  # Tiap 2 jam (ubah sesuai kebutuhan)
```

Format cron: `menit jam hari bulan hari-minggu`

## 📥 Sumber Data

### Fetch dari Playlist Publik
- **doms9/iptv**: https://s.id/d9M3U8 (144 entries)
- **rosdiyanto/iptv**: https://raw.githubusercontent.com/rosdiyanto/iptv/main/full.m3u (828 entries)

### Web Scraping
- **streamcenter.xyz**: API-based scraper untuk event live
- **fawanews.sc**: HTML scraper untuk event sepakbola
- **roxiestreams.info**: HTML scraper untuk event combat sports

## 🔍 Kategorisasi

### Sepakbola
Keywords: LIGA INGGRIS, LIGA ITALIA, LIGA JERMAN, LIGA SPANYOL, LIGA CHAMPION, BRI SUPER LEAGUE, FIFA+, PREMIER LEAGUE, SERIE A, BUNDESLIGA, LA LIGA, UEFA, EPL, dll.

### Tarung
Keywords: MMA, UFC, BOXING, FIGHT, WWE, PFL, ONE CHAMPIONSHIP, COMBAT, KICKBOXING, BELLATOR, dll.

### TV Lokal Indonesia
Keywords: INDONESIA TV, TVRI, RCTI, MNCTV, GTV, SCTV, INDOSIAR, TRANS TV, TRANS 7, ANTV, TV ONE, METRO TV, KOMPAS TV, dll.

## 🛡️ Health Check

Health check akan:
1. Cek semua URL dengan HTTP HEAD request (timeout 10s)
2. Catat stream yang masih hidup (HTTP 2xx/3xx)
3. Catat stream yang mati (HTTP 4xx/5xx/timeout)
4. Update `readme.md` dengan statistik
5. Parallel max 10 jobs untuk kecepatan

## 📄 Legal Disclaimer

Proyek ini hanya mengumpulkan link stream yang tersedia secara publik di internet. Tidak ada konten video/audio yang di-host di repository ini. Link-link ini mungkin mengarah ke materi berhak cipta milik pihak ketiga dan disediakan **hanya untuk tujuan edukasi dan riset**.

Penulis tidak mendukung, mempromosikan, atau mendorong streaming ilegal atau pelanggaran hak cipta. Pengguna akhir bertanggung jawab penuh untuk memastikan kepatuhan terhadap hukum yang berlaku di yurisdiksi mereka sebelum menggunakan link manapun.

Jika Anda pemegang hak cipta dan ingin link dihapus, silakan buka issue.

## 📊 Statistics

- **Total sources**: 2 playlist publik + 3 web scrapers
- **Total entries processed**: 972+ entries
- **Output playlists**: 3 files (sepakbola, tarung, tv_lokal)
- **Health check**: 230 URLs checked (134 working, 96 dead)

## 🤝 Kontribusi

Kontribusi sangat diterima! Silakan:
1. Fork repository
2. Buat branch fitur (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buka Pull Request

## 📝 Lisensi

Proyek ini dibuat untuk tujuan edukasi dan riset. Gunakan dengan bijak dan patuhi hukum yang berlaku di yurisdiksi Anda.

## 🙏 Acknowledgments

- [doms9/iptv](https://github.com/doms9/iptv) - Inspirasi arsitektur scraper
- [rosdiyanto/iptv](https://github.com/rosdiyanto/iptv) - Sumber TV lokal Indonesia
- Semua kontributor playlist IPTV open-source

---

**Catatan**: Proyek ini terus dikembangkan. Stream yang tersedia dapat berubah sewaktu-waktu tergantung pada ketersediaan sumber.
# ocidtv
