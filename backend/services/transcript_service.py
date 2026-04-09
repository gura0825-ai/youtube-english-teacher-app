import os
import re
import requests

MAX_TRANSCRIPT_CHARS = 150_000  # ~37,500 tokens — stays within Claude's context window

_VIDEO_ID_PATTERNS = [
    r'[?&]v=([a-zA-Z0-9_-]{11})',
    r'youtu\.be/([a-zA-Z0-9_-]{11})',
    r'/shorts/([a-zA-Z0-9_-]{11})',
    r'/embed/([a-zA-Z0-9_-]{11})',
]

SUPADATA_API_URL = "https://api.supadata.ai/v1/youtube/transcript"


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

        match = re.search(r"<title>(.+?) - YouTube</title>", resp.text)
        if match:
            return match.group(1)

        match = re.search(r'"title":"([^"]{1,200})"', resp.text)
        if match:
            return match.group(1)
    except Exception:
        pass

    return video_id


def get_transcript(video_id: str) -> str:
    """
    Fetch English transcript via Supadata API.
    Raises ValueError if no transcript is available.
    """
    api_key = os.environ.get("SUPADATA_API_KEY")
    if not api_key:
        raise ValueError("SUPADATA_API_KEY environment variable is not set")

    resp = requests.get(
        SUPADATA_API_URL,
        headers={"x-api-key": api_key},
        params={"videoId": video_id, "lang": "en", "text": "true"},
        timeout=30,
    )

    if resp.status_code == 404:
        raise ValueError("No subtitles available for this video")
    if not resp.ok:
        raise ValueError(f"Supadata API error: {resp.status_code} {resp.text[:200]}")

    data = resp.json()
    text = data.get("content", "")

    if not isinstance(text, str):
        raise ValueError("Unexpected response format from Supadata API")

    if not text.strip():
        raise ValueError("Transcript is empty")

    if len(text) > MAX_TRANSCRIPT_CHARS:
        text = text[:MAX_TRANSCRIPT_CHARS] + "\n\n[Transcript truncated due to length]"

    return text
