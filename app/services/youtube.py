"""YouTube video ID -> transcript as plain text."""

import logging

from youtube_transcript_api import CouldNotRetrieveTranscript, YouTubeTranscriptApi

log = logging.getLogger(__name__)


def get_transcript(video_id: str, languages: tuple[str, ...] = ("en",)) -> str | None:
    """The video's transcript as one block of text, or None if it has none (or YouTube blocks us)."""
    try:
        fetched = YouTubeTranscriptApi().fetch(video_id, languages=languages)
    except CouldNotRetrieveTranscript as e:
        log.warning("No transcript for %s: %s", video_id, type(e).__name__)
        return None
    return " ".join(snippet.text for snippet in fetched)


if __name__ == "__main__":
    print(get_transcript("4MAupwjl3pc"))