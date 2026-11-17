"""Print a video's transcript.

Run from the project root:
    uv run python -m scripts.check_transcript              # default test video
    uv run python -m scripts.check_transcript <video_id>   # any other video
"""

import logging
import sys

from app.services.youtube import get_transcript

logging.basicConfig(level=logging.WARNING, format="WARN  %(message)s")
video_id = sys.argv[1] if len(sys.argv) > 1 else "E8zpgNPx8jE"
transcript = get_transcript(video_id)
if transcript:
    print(f"{video_id}: {len(transcript):,} chars\n\n{transcript[:500]}...")
else:
    print(f"{video_id}: no transcript")
