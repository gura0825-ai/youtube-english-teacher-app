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


def _format_timestamp(offset_ms: float) -> str:
    total_seconds = int(offset_ms // 1000)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def _merge_into_lines(chunks: list, gap_threshold_ms: int = 2000, max_line_chars: int = 200) -> list:
    """
    Auto-generated captions arrive as many small, sometimes overlapping
    fragments. Sort them by their real start time and glue nearby fragments
    into one readable line per timestamp, instead of a timestamp per fragment.
    """
    ordered = sorted(chunks, key=lambda c: c.get("offset", 0))

    lines = []
    current_text = []
    current_start = None
    last_end = None

    for chunk in ordered:
        text = (chunk.get("text") or "").strip()
        if not text:
            continue
        start = chunk.get("offset", 0)
        end = start + chunk.get("duration", 0)

        starts_new_line = (
            current_start is None
            or start - last_end > gap_threshold_ms
            or sum(len(t) for t in current_text) > max_line_chars
        )

        if starts_new_line:
            if current_text:
                lines.append({"start_ms": current_start, "text": " ".join(current_text)})
            current_text = [text]
            current_start = start
        else:
            current_text.append(text)

        last_end = max(last_end or 0, end)

    if current_text:
        lines.append({"start_ms": current_start, "text": " ".join(current_text)})

    return lines


def get_transcript(video_id: str) -> dict:
    """
    Fetch the English transcript via Supadata API and organize it into
    time-ordered, merged lines instead of raw overlapping caption fragments.

    Returns {"plain_text": str, "segments": [{"time": "MM:SS", "text": str}, ...]}.
    Raises ValueError if no transcript is available.
    """
    api_key = os.environ.get("SUPADATA_API_KEY")
    if not api_key:
        raise ValueError("SUPADATA_API_KEY environment variable is not set")

    resp = requests.get(
        SUPADATA_API_URL,
        headers={"x-api-key": api_key},
        params={"videoId": video_id, "lang": "en", "text": "false"},
        timeout=30,
    )

    if resp.status_code == 404:
        raise ValueError("No subtitles available for this video")
    if not resp.ok:
        raise ValueError(f"Supadata API error: {resp.status_code} {resp.text[:200]}")

    data = resp.json()
    chunks = data.get("content", [])

    if not isinstance(chunks, list) or not chunks:
        raise ValueError("Transcript is empty")

    lines = _merge_into_lines(chunks)
    if not lines:
        raise ValueError("Transcript is empty")

    segments = [
        {"time": _format_timestamp(line["start_ms"]), "text": line["text"]}
        for line in lines
    ]

    plain_text = "\n".join(f"[{seg['time']}] {seg['text']}" for seg in segments)
    if len(plain_text) > MAX_TRANSCRIPT_CHARS:
        plain_text = plain_text[:MAX_TRANSCRIPT_CHARS] + "\n\n[Transcript truncated due to length]"

    return {"plain_text": plain_text, "segments": segments}
