"""Quick check that the YouTube scraper works.

Run from the project root:
    uv run python -m scripts.check_youtube          # last 24 hours
    uv run python -m scripts.check_youtube 168      # last 7 days (more likely to find videos)
"""

import logging
import sys
from datetime import datetime, timedelta, timezone

from app.config import YOUTUBE_CHANNELS
from app.scrapers.youtube import parse_feed, scrape_channels

# 1. Offline check of the 24h filter on a tiny fake feed: no network needed.
now = datetime.now(timezone.utc)
fmt = "%Y-%m-%dT%H:%M:%S+00:00"
FAKE_FEED = f"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015">
  <entry><yt:videoId>new1</yt:videoId><title>New</title>
    <link rel="alternate" href="https://www.youtube.com/watch?v=new1"/>
    <published>{(now - timedelta(hours=2)).strftime(fmt)}</published></entry>
  <entry><yt:videoId>old1</yt:videoId><title>Old</title>
    <link rel="alternate" href="https://www.youtube.com/watch?v=old1"/>
    <published>{(now - timedelta(hours=30)).strftime(fmt)}</published></entry>
</feed>"""
videos = parse_feed(FAKE_FEED, since=now - timedelta(hours=24))
assert [v["video_id"] for v in videos] == ["new1"], videos
assert videos[0]["url"] == "https://www.youtube.com/watch?v=new1"
print("OK  offline filter check: kept the 2h-old video, dropped the 30h-old one\n")

# 2. Live check against the real channels in app/config.py.
logging.basicConfig(level=logging.WARNING, format="WARN  %(message)s")
hours = int(sys.argv[1]) if len(sys.argv) > 1 else 24
print(f"Fetching videos from the last {hours}h for {len(YOUTUBE_CHANNELS)} channels...\n")
results = scrape_channels(YOUTUBE_CHANNELS, hours=hours)
for v in results:
    transcript = v["transcript"]
    status = f"{len(transcript):,} chars: {transcript[:80]!r}..." if transcript else "NO TRANSCRIPT"
    print(f"[{v['channel']}] {v['title']}\n  {v['url']}  ({v['published_at']:%Y-%m-%d %H:%M} UTC)\n  transcript: {status}\n")
print(f"Done: {len(results)} videos, {sum(1 for v in results if v['transcript'])} with transcripts.")
