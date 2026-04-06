import re
import requests

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled

MAX_TRANSCRIPT_CHARS = 150_000  # ~37,500 tokens — stays within Claude's context window

_VIDEO_ID_PATTERNS = [
    r'[?&]v=([a-zA-Z0-9_-]{11})',
    r'youtu\.be/([a-zA-Z0-9_-]{11})',
    r'/shorts/([a-zA-Z0-9_-]{11})',
    r'/embed/([a-zA-Z0-9_-]{11})',
]


def extract_video_id(url: str) -> str | None:
    for pattern in _VIDEO_ID_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_video_title(video_id: str) -> str:
    """Fetch video title by parsing the YouTube page HTML. Falls back to video_id."""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()

        # Try <title> tag first
        match = re.search(r"<title>(.+?) - YouTube</title>", resp.text)
        if match:
            return match.group(1)

        # Fallback: JSON data embedded in page
        match = re.search(r'"title":"([^"]{1,200})"', resp.text)
        if match:
            return match.group(1)
    except Exception:
        pass

    return video_id


def get_transcript(video_id: str) -> str:
    """
    Fetch English transcript for the given video_id.
    Priority: en → en-US → any auto-generated.
    Raises ValueError if no transcript is available.
    """
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)

        # Try manual English transcripts first, then auto-generated
        try:
            transcript = transcript_list.find_transcript(["en", "en-US"])
        except NoTranscriptFound:
            transcript = transcript_list.find_generated_transcript(["en", "en-US"])

        snippets = transcript.fetch()
        parts = []
        for snippet in snippets:
            # Handle both dict (old API) and object (new API ≥0.6) formats
            if isinstance(snippet, dict):
                parts.append(snippet.get("text", ""))
            else:
                parts.append(getattr(snippet, "text", ""))

        text = " ".join(p for p in parts if p)

        if len(text) > MAX_TRANSCRIPT_CHARS:
            text = text[:MAX_TRANSCRIPT_CHARS] + "\n\n[Transcript truncated due to length]"

        return text

    except (NoTranscriptFound, TranscriptsDisabled) as e:
        raise ValueError("No subtitles available for this video") from e
