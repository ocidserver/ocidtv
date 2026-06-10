import asyncio
import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path

import httpx
import pytz

CACHE_DIR = Path(__file__).parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s"))
        logger.addHandler(h)
    return logger


class Network:
    def __init__(self):
        self.HTTP_S = asyncio.Semaphore(10)
        self.client = httpx.AsyncClient(
            headers={"User-Agent": UA},
            follow_redirects=True,
            timeout=30,
            http2=True,
        )

    async def request(self, url: str, **kwargs) -> httpx.Response | None:
        log = kwargs.pop("log", None)
        try:
            r = await self.client.get(url, **kwargs)
            r.raise_for_status()
            return r
        except Exception as e:
            if log:
                log.warning(f"Request failed: {url} -> {e}")
            return None

    async def safe_process(self, handler, *, url_num, semaphore, log):
        async with semaphore:
            try:
                return await handler()
            except Exception as e:
                log.warning(f"URL {url_num}) Processing failed: {e}")
                return None


network = Network()


class Cache:
    def __init__(self, tag: str, exp: int = 86400):
        self.tag = tag
        self.exp = exp
        self.path = CACHE_DIR / f"{tag}.json"

    def load(self) -> dict:
        if not self.path.exists():
            return {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            now = time.time()
            return {k: v for k, v in data.items() if now - v.get("timestamp", 0) < self.exp}
        except Exception:
            return {}

    def write(self, data: dict) -> None:
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


class Time:
    @staticmethod
    def now(tz: str = "UTC") -> datetime:
        return datetime.now(pytz.timezone(tz))

    @staticmethod
    def clean(dt: datetime) -> datetime:
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    @staticmethod
    def from_str(s: str, fmt: str = "%Y-%m-%d %H:%M:%S", timezone: str = "UTC") -> datetime:
        dt = datetime.strptime(s, fmt)
        return pytz.timezone(timezone).localize(dt)


LEAGUES_LOGOS = {
    "Football": "https://i.gyazo.com/4a5e9fa2525808ee4b65002b56d3450e.png",
    "Soccer": "https://i.gyazo.com/4a5e9fa2525808ee4b65002b56d3450e.png",
    "Basketball": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/leagues/500/nba.png",
    "Baseball": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/leagues/500/mlb.png",
    "Hockey": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/leagues/500/nhl.png",
    "Fight MMA": "https://i.gyazo.com/4a5e9fa2525808ee4b65002b56d3450e.png",
    "Boxing": "https://i.gyazo.com/4a5e9fa2525808ee4b65002b56d3450e.png",
    "WWE": "https://i.gyazo.com/4a5e9fa2525808ee4b65002b56d3450e.png",
    "Tennis": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/leagues/500/ten.png",
    "Motor Sport": "https://a.espncdn.com/combiner/i?img=/i/teamlogos/leagues/500/f1.png",
}


class leagues:
    live_img = "https://i.gyazo.com/4a5e9fa2525808ee4b65002b56d3450e.png"

    @staticmethod
    def get_tvg_info(sport: str, event: str) -> tuple[str | None, str]:
        logo = LEAGUES_LOGOS.get(sport, leagues.live_img)
        tvg_id = "Live.Event.us"
        return tvg_id, logo
