import re
from functools import partial

from selectolax.parser import HTMLParser

from .utils import Cache, Time, get_logger, leagues, network

log = get_logger(__name__)

urls: dict[str, dict[str, str | float]] = {}

TAG = "ROXIE"

CACHE_FILE = Cache(TAG, exp=10_800)

BASE_URL = "https://roxiestreams.info"


async def process_event(url: str, url_num: int) -> str | None:
    if not (html_data := await network.request(url, log=log)):
        log.warning(f"URL {url_num}) Failed to load url.")
        return

    valid_m3u8 = re.compile(
        r'(?:source|src|file|hls)\s*[=:]\s*["\']?(https?:\/\/[^"\'\s>]+\.m3u8[^"\'\s>]*)',
        re.I,
    )

    if not (match := valid_m3u8.search(html_data.text)):
        log.warning(f"URL {url_num}) No M3U8 found")
        return

    log.info(f"URL {url_num}) Captured M3U8")

    return match[1]


async def get_events(cached_links: set[str]) -> list[dict[str, str]]:
    events = []

    if not (html_data := await network.request(BASE_URL, log=log)):
        return events

    soup = HTMLParser(html_data.content)

    for link in soup.css("a[href]"):
        href = link.attributes.get("href", "")

        if not href or "/event/" not in href:
            continue

        full_url = href if href.startswith("http") else f"{BASE_URL}{href}"

        if full_url in cached_links:
            continue

        text = link.text(strip=True)

        if not text:
            continue

        sport = ""
        text_lower = text.lower()
        if "wwe" in text_lower:
            sport = "WWE"
        elif "ufc" in text_lower:
            sport = "Fight MMA"
        elif "boxing" in text_lower or "box" in text_lower:
            sport = "Boxing"
        elif "fight" in text_lower:
            sport = "Fight MMA"
        else:
            sport = "Fight MMA"

        events.append(
            {
                "sport": sport,
                "event": text,
                "link": full_url,
            }
        )

    return events


async def scrape() -> None:
    cached_urls = CACHE_FILE.load()

    cached_links = {entry["link"] for entry in cached_urls.values() if "link" in entry}

    valid_urls = {k: v for k, v in cached_urls.items() if v.get("url")}

    valid_count = cached_count = len(valid_urls)

    urls.update(valid_urls)

    log.info(f"Loaded {cached_count} event(s) from cache")

    log.info(f'Scraping from "{BASE_URL}"')

    if events := await get_events(cached_links):
        log.info(f"Processing {len(events)} new URL(s)")

        now = Time.clean(Time.now())

        for i, ev in enumerate(events, start=1):
            handler = partial(
                process_event,
                url=(link := ev["link"]),
                url_num=i,
            )

            url = await network.safe_process(
                handler,
                url_num=i,
                semaphore=network.HTTP_S,
                log=log,
            )

            sport, event = ev["sport"], ev["event"]

            key = f"[{sport}] {event} ({TAG})"

            tvg_id, logo = leagues.get_tvg_info(sport, event)

            entry = {
                "url": url,
                "logo": logo,
                "base": BASE_URL,
                "timestamp": now.timestamp(),
                "id": tvg_id or "Live.Event.us",
                "link": link,
            }

            cached_urls[key] = entry

            if url:
                valid_count += 1

                urls[key] = entry

        log.info(f"Collected and cached {valid_count - cached_count} new event(s)")

    else:
        log.info("No new events found")

    CACHE_FILE.write(cached_urls)
