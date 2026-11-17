"""YouTube scraper: latest videos from channel RSS feeds, plus their transcripts."""

import logging
import re
from datetime import datetime, timedelta, timezone

import feedparser
import httpx

from app.services.youtube import get_transcript

log = logging.getLogger(__name__)

FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
# Without this, YouTube may serve a consent page instead of the channel page.
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en"}


def get_channel_id(channel: str) -> str:
    """Turn any channel reference into its channel ID ('UC...'), which the RSS feed needs.

    Accepts a full URL (https://www.youtube.com/@daveebbelaar or .../channel/UC...),
    a handle (@daveebbelaar) or a bare ID.
    """
    if match := re.search(r"(?:^|/channel/)(UC[\w-]{22})(?:[/?]|$)", channel):
        return match.group(1)  # the ID is already in it: no request needed
    url = channel if channel.startswith("http") else f"https://www.youtube.com/@{channel.lstrip('@')}"
    html = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=15).text
    match = re.search(r'<link rel="canonical" href="https://www\.youtube\.com/channel/(UC[\w-]{22})"', html)
    if not match:
        raise ValueError(f"Could not find a channel ID on {url}")
    return match.group(1)


def parse_feed(xml: str, since: datetime) -> list[dict]:
    """Turn the RSS XML into video dicts, keeping only videos published after `since`."""
    videos = []
    for entry in feedparser.parse(xml).entries:
        published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        if published >= since:
            videos.append({
                "video_id": entry.yt_videoid,
                "title": entry.title,
                "url": entry.link,
                "published_at": published,
                "description": entry.get("summary", ""),
            })
    return videos


def get_latest_videos(channel: str, hours: int = 24) -> list[dict]:
    """Videos from one channel that were published in the last `hours` hours.

    `channel` can be a URL, @handle/username or channel ID (see get_channel_id).
    The feed only holds a channel's newest ~15 videos, which is plenty for a 24h window.
    """
    resp = httpx.get(FEED_URL.format(channel_id=get_channel_id(channel)), headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return parse_feed(resp.text, since=datetime.now(timezone.utc) - timedelta(hours=hours))


def scrape_channels(channels: dict[str, str], hours: int = 24) -> list[dict]:
    """Latest videos with transcripts for every channel. One failing channel doesn't stop the others.

    `channels`: name -> channel URL, @handle or ID (see get_channel_id).
    """
    results = []
    for name, channel in channels.items():
        try:
            videos = get_latest_videos(channel, hours)
        except (httpx.HTTPError, ValueError) as e:
            log.warning("Feed failed for %s (%s): %s", name, channel, e)
            continue
        for video in videos:
            video["channel"] = name
            video["transcript"] = get_transcript(video["video_id"])
            results.append(video)
    return results


if __name__ == "__main__":
    videos = get_latest_videos(channel="daveebbelaar", hours=200)
    print(videos)  