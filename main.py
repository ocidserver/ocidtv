import asyncio
import re
from pathlib import Path

from categorizer import categorize, categorize_event
from fetcher import StreamEntry, fetch_all
from m3u_writer import write_all
from scrapers import fawa, roxie, streamcenter
from scrapers.utils import get_logger, network

log = get_logger(__name__)


def scraper_to_entries() -> dict[str, list[StreamEntry]]:
    result: dict[str, list[StreamEntry]] = {"sepakbola": [], "tarung": []}

    all_scraper_urls = (
        streamcenter.urls
        | fawa.urls
        | roxie.urls
    )

    for event_name, info in all_scraper_urls.items():
        url = info.get("url")
        if not url:
            continue

        sport_match = re.search(r'\[([^\]]+)\]', event_name)
        sport = sport_match.group(1) if sport_match else ""

        cat = categorize_event(event_name, sport)
        if not cat or cat not in result:
            continue

        entry = StreamEntry(
            name=event_name,
            url=url,
            group_title="LIVE EVENT SCRAPE",
            tvg_id=info.get("id", "Live.Event.us"),
            tvg_logo=info.get("logo", ""),
            tvg_name=event_name,
            source="scraper",
            extra_lines=[
                f'#EXTVLCOPT:http-referrer={info.get("base", "")}',
                f'#EXTVLCOPT:http-origin={info.get("base", "")}',
                f'#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0',
            ],
        )
        result[cat].append(entry)

    return result


async def run_scrapers() -> None:
    log.info(f"{'=' * 10} Scrapers Started {'=' * 10}")

    httpx_tasks = [
        asyncio.create_task(fawa.scrape()),
        asyncio.create_task(streamcenter.scrape()),
        asyncio.create_task(roxie.scrape()),
    ]

    await asyncio.gather(*httpx_tasks)

    log.info("All scrapers completed")


async def main() -> None:
    log.info(f"{'=' * 10} IPTV Scraper Started {'=' * 10}")

    fetched_entries = await fetch_all()

    await run_scrapers()

    await network.client.aclose()

    sepakbola: list[StreamEntry] = []
    tarung: list[StreamEntry] = []
    tv_lokal: list[StreamEntry] = []

    for entry in fetched_entries:
        cat = categorize(entry.group_title)

        if cat == "sepakbola":
            sepakbola.append(entry)
        elif cat == "tarung":
            tarung.append(entry)
        elif cat == "tv_lokal":
            tv_lokal.append(entry)

    scraper_entries = scraper_to_entries()
    for cat_name, entries in scraper_entries.items():
        if cat_name == "sepakbola":
            sepakbola.extend(entries)
        elif cat_name == "tarung":
            tarung.extend(entries)

    log.info(f"Categorized: sepakbola={len(sepakbola)}, tarung={len(tarung)}, tv_lokal={len(tv_lokal)}")

    output_paths = write_all(sepakbola, tarung, tv_lokal)

    for name, path in output_paths.items():
        log.info(f"Output: {name} -> {path}")

    log.info(f"{'=' * 10} Done {'=' * 10}")


if __name__ == "__main__":
    asyncio.run(main())
