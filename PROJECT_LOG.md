# Project Log - IPTV Auto-Scraper

Log perkembangan dan catatan teknis proyek IPTV Auto-Scraper.

---

## 📅 2026-06-10 - Initial Release (v1.0.0)

### 🎉 Milestone
Proyek IPTV Auto-Scraper berhasil dibuat dan dijalankan pertama kali.

### ✅ Fitur yang Diselesaikan

#### Core System
- [x] `main.py` - Orchestrator utama dengan async execution
- [x] `fetcher.py` - Parser M3U dari sumber publik
- [x] `categorizer.py` - Sistem klasifikasi berbasis keyword
- [x] `m3u_writer.py` - Generator file M3U dengan deduplikasi

#### Scrapers
- [x] `scrapers/utils.py` - Network client, cache system, logger
- [x] `scrapers/streamcenter.py` - Scraper untuk streamcenter.xyz (API-based)
- [x] `scrapers/fawa.py` - Scraper untuk fawanews.sc (HTML parsing)
- [x] `scrapers/roxie.py` - Scraper untuk roxiestreams.info (HTML parsing)

#### Automation
- [x] `health.sh` - Health check script (bash)
- [x] `.github/workflows/scraper.yml` - GitHub Actions untuk scraper (tiap 2 jam)
- [x] `.github/workflows/health.yml` - GitHub Actions untuk health check (3x sehari)

### 📊 Hasil Run Pertama

```
========== IPTV Scraper Started ==========
Fetching doms9 from https://s.id/d9M3U8
Parsed 144 entries from doms9
Fetching rosdiyanto from https://raw.githubusercontent.com/rosdiyanto/iptv/main/full.m3u
Parsed 828 entries from rosdiyanto
Total entries fetched: 972

========== Scrapers Started ==========
[scrapers.fawa] Processing 31 new URL(s)
[scrapers.fawa] URL 1-31) Captured M3U8 ✓
[scrapers.fawa] Collected and cached 31 new event(s)
[scrapers.streamcenter] No events found (off-season)
[scrapers.roxie] No new events found (site down)

Categorized: sepakbola=87, tarung=12, tv_lokal=127

Output:
- sepakbola.m3u: 72 entries (63 fetch + 9 scrape)
- tarung.m3u: 12 entries
- tv_lokal.m3u: 127 entries
========== Done ==========
```

### 🐛 Bugs Fixed

1. **Network.request() log parameter leak**
   - Issue: Parameter `log` bocor ke httpx client
   - Fix: Pop `log` dari kwargs sebelum pass ke httpx

2. **HTTP_S semaphore missing**
   - Issue: `Network` class tidak punya attribute `HTTP_S`
   - Fix: Inisialisasi `HTTP_S` di `__init__`

3. **Event kategorisasi salah**
   - Issue: Event MLB/WNBA/NHL masuk ke kategori "tarung"
   - Fix: Tambah filter non-football sports di `categorize_event()`

### 🔧 Technical Details

#### Dependencies
```toml
httpx[http2]>=0.28.1
playwright>=1.58.0
pytz>=2026.1
selectolax>=0.4.7
```

#### Architecture
- **Async-first**: Semua I/O operations menggunakan asyncio
- **Modular scrapers**: Setiap scraper independent, mudah ditambah/dihapus
- **Cache system**: JSON-based cache dengan TTL untuk menghindari re-scrape
- **Deduplication**: URL deduplikasi berdasarkan base URL (tanpa query params)

#### Sources
| Source | Type | Entries | Status |
|--------|------|---------|--------|
| doms9/iptv | M3U fetch | 144 | ✅ Working |
| rosdiyanto/iptv | M3U fetch | 828 | ✅ Working |
| streamcenter.xyz | API scraper | 0 | ⚠️ No events |
| fawanews.sc | HTML scraper | 31 | ✅ Working |
| roxiestreams.info | HTML scraper | 0 | ❌ Site down |

### 📈 Health Check Results

```
Overall: Working=134 | Dead=96

| Category  | Working | Dead |
|-----------|---------|------|
| Sepakbola | 29      | 34   |
| Tarung    | 7       | 33   |
| TV Lokal  | 98      | 29   |
```

### 📝 Notes

1. **FAWA scraper** sangat produktif - berhasil scrape 31 events sepakbola live
2. **Streamcenter** tidak ada event saat ini (mungkin off-season untuk beberapa liga)
3. **Roxie** site tidak merespon - perlu cari alternatif scraper combat sports
4. **TV Lokal** paling stabil - 98/127 stream masih hidup (77%)
5. **Sepakbola** banyak stream mati karena geo-blocking atau expired tokens

### 🎯 Next Steps (TODO)

#### High Priority
- [ ] Tambah scraper untuk combat sports (pengganti roxie)
- [ ] Implementasi EPG fetcher (seperti doms9/epg-fetch.py)
- [ ] Tambah filter untuk menghapus stream yang sudah expired

#### Medium Priority
- [ ] Tambah lebih banyak sumber M3U publik
- [ ] Implementasi stream quality checker (bitrate, resolution)
- [ ] Tambah notifikasi (Telegram/Discord) saat scraper selesai

#### Low Priority
- [ ] Web UI untuk browse playlist
- [ ] API endpoint untuk serve playlist
- [ ] Docker support untuk easy deployment

### 💡 Lessons Learned

1. **Async is king**: Semua scraper berjalan concurrent, total waktu hanya ~10 detik
2. **Cache matters**: JSON cache dengan TTL menghindari re-scrape yang tidak perlu
3. **Keyword categorization works**: Sistem keyword cukup akurat untuk 3 kategori utama
4. **Health check essential**: Banyak stream mati, perlu filter otomatis
5. **Modular design**: Mudah tambah scraper baru tanpa ubah core logic

---

## 📚 References

### Inspirasi
- [doms9/iptv](https://github.com/doms9/iptv) - Arsitektur scraper, health check, GitHub Actions
- [rosdiyanto/iptv](https://github.com/rosdiyanto/iptv) - Sumber TV lokal Indonesia

### Tools Used
- [httpx](https://www.python-httpx.org/) - Async HTTP client
- [selectolax](https://github.com/rushter/selectolax) - Fast HTML parser
- [playwright](https://playwright.dev/python/) - Browser automation (untuk scraper kompleks)
- [uv](https://github.com/astral-sh/uv) - Fast Python package manager

### M3U Format
- [IPTV-org/iptv](https://github.com/iptv-org/iptv) - Referensi format M3U
- [Extended M3U Wikipedia](https://en.wikipedia.org/wiki/M3U#Extended_M3U_directives)

---

## 📊 Changelog

### v1.0.0 (2026-06-10)
- Initial release
- 3 output playlists (sepakbola, tarung, tv_lokal)
- 2 M3U fetchers + 3 web scrapers
- Health check system
- GitHub Actions automation

---

**Last Updated**: 2026-06-10 14:21 UTC
