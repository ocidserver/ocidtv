import re
from dataclasses import dataclass, field

from scrapers.utils import get_logger, network

log = get_logger(__name__)

SOURCES = {
    "doms9": "https://s.id/d9M3U8",
    "rosdiyanto": "https://raw.githubusercontent.com/rosdiyanto/iptv/main/full.m3u",
}


@dataclass
class StreamEntry:
    name: str
    url: str
    group_title: str
    tvg_id: str = ""
    tvg_logo: str = ""
    tvg_name: str = ""
    source: str = ""
    raw_block: str = ""
    extra_lines: list[str] = field(default_factory=list)

    @property
    def unique_key(self) -> str:
        return f"{self.group_title}|{self.name}|{self.url}"


def parse_m3u(content: str, source: str) -> list[StreamEntry]:
    entries = []
    lines = content.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line.startswith("#EXTINF"):
            i += 1
            continue

        extinf_line = line
        block_lines = [line]
        extra_lines = []
        i += 1

        while i < len(lines):
            next_line = lines[i].strip()
            if next_line.startswith("#"):
                block_lines.append(next_line)
                extra_lines.append(next_line)
                i += 1
            elif next_line.startswith("http"):
                block_lines.append(next_line)
                break
            else:
                break
            i += 1

        if i >= len(lines) or not lines[i].strip().startswith("http"):
            continue

        url = lines[i].strip()
        i += 1

        name_match = re.search(r',(.+)$', extinf_line)
        name = name_match.group(1).strip() if name_match else "Unknown"

        group_match = re.search(r'group-title="([^"]*)"', extinf_line)
        group_title = group_match.group(1) if group_match else ""

        tvg_id_match = re.search(r'tvg-id="([^"]*)"', extinf_line)
        tvg_id = tvg_id_match.group(1) if tvg_id_match else ""

        tvg_logo_match = re.search(r'tvg-logo="([^"]*)"', extinf_line)
        tvg_logo = tvg_logo_match.group(1) if tvg_logo_match else ""

        tvg_name_match = re.search(r'tvg-name="([^"]*)"', extinf_line)
        tvg_name = tvg_name_match.group(1) if tvg_name_match else ""

        entry = StreamEntry(
            name=name,
            url=url,
            group_title=group_title,
            tvg_id=tvg_id,
            tvg_logo=tvg_logo,
            tvg_name=tvg_name,
            source=source,
            raw_block="\n".join(block_lines),
            extra_lines=extra_lines,
        )
        entries.append(entry)

    return entries


async def fetch_source(name: str, url: str) -> list[StreamEntry]:
    log.info(f"Fetching {name} from {url}")

    r = await network.request(url)
    if not r:
        log.error(f"Failed to fetch {name}")
        return []

    entries = parse_m3u(r.text, source=name)
    log.info(f"Parsed {len(entries)} entries from {name}")
    return entries


async def fetch_all() -> list[StreamEntry]:
    all_entries = []

    for name, url in SOURCES.items():
        entries = await fetch_source(name, url)
        all_entries.extend(entries)

    log.info(f"Total entries fetched: {len(all_entries)}")
    return all_entries
