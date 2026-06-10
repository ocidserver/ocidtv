from pathlib import Path

from fetcher import StreamEntry
from scrapers.utils import get_logger

log = get_logger(__name__)

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def format_entry(entry: StreamEntry) -> str:
    lines = []

    extinf_parts = ["#EXTINF:-1"]

    if entry.tvg_id:
        extinf_parts.append(f'tvg-id="{entry.tvg_id}"')
    if entry.tvg_name:
        extinf_parts.append(f'tvg-name="{entry.tvg_name}"')
    if entry.tvg_logo:
        extinf_parts.append(f'tvg-logo="{entry.tvg_logo}"')
    if entry.group_title:
        extinf_parts.append(f'group-title="{entry.group_title}"')

    extinf_parts.append(f",{entry.name}")

    lines.append(" ".join(extinf_parts))

    for extra in entry.extra_lines:
        if extra.startswith("#EXTINF"):
            continue
        lines.append(extra)

    lines.append(entry.url)

    return "\n".join(lines)


def deduplicate(entries: list[StreamEntry]) -> list[StreamEntry]:
    seen_urls = set()
    unique = []

    for entry in entries:
        url_key = entry.url.split("?")[0] if "?" in entry.url else entry.url
        if url_key not in seen_urls:
            seen_urls.add(url_key)
            unique.append(entry)

    return unique


def write_m3u(entries: list[StreamEntry], filename: str) -> Path:
    entries = deduplicate(entries)

    output_path = OUTPUT_DIR / filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")

        for entry in entries:
            f.write("\n")
            f.write(format_entry(entry))
            f.write("\n")

    log.info(f"Written {len(entries)} entries to {output_path}")
    return output_path


def write_all(
    sepakbola: list[StreamEntry],
    tarung: list[StreamEntry],
    tv_lokal: list[StreamEntry],
) -> dict[str, Path]:
    return {
        "sepakbola": write_m3u(sepakbola, "sepakbola.m3u"),
        "tarung": write_m3u(tarung, "tarung.m3u"),
        "tv_lokal": write_m3u(tv_lokal, "tv_lokal.m3u"),
    }
