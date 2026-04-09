import re
import json
import requests
import yt_dlp

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
    """Fetch video title via yt-dlp. Falls back to video_id."""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}",
                download=False,
            )
            return info.get('title') or video_id
    except Exception:
        pass
    return video_id


def get_transcript(video_id: str) -> str:
    """
    Fetch English transcript for the given video_id using yt-dlp.
    Priority: manual en/en-US → auto-generated en/en-US.
    Raises ValueError if no transcript is available.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
        'writesubtitles': False,
        'writeautomaticsub': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    subtitles = info.get('subtitles') or {}
    automatic_captions = info.get('automatic_captions') or {}

    # Try manual subtitles first, then auto-generated
    lang_candidates = ['en', 'en-US', 'en-GB']
    subtitle_data = None
    for lang in lang_candidates:
        if lang in subtitles:
            subtitle_data = subtitles[lang]
            break
    if subtitle_data is None:
        for lang in lang_candidates:
            if lang in automatic_captions:
                subtitle_data = automatic_captions[lang]
                break

    if not subtitle_data:
        raise ValueError("No subtitles available for this video")

    # Prefer json3 format, fall back to ttml/vtt
    fmt_priority = ['json3', 'ttml', 'vtt', 'srv3', 'srv2', 'srv1']
    chosen = None
    for fmt in fmt_priority:
        for entry in subtitle_data:
            if entry.get('ext') == fmt:
                chosen = entry
                break
        if chosen:
            break
    if not chosen:
        chosen = subtitle_data[0]

    sub_url = chosen.get('url')
    if not sub_url:
        raise ValueError("No subtitle URL found")

    resp = requests.get(sub_url, timeout=15)
    resp.raise_for_status()

    ext = chosen.get('ext', '')
    if ext == 'json3':
        text = _parse_json3(resp.text)
    elif ext in ('ttml', 'xml'):
        text = _parse_ttml(resp.text)
    else:
        text = _parse_vtt(resp.text)

    if not text.strip():
        raise ValueError("Transcript is empty")

    if len(text) > MAX_TRANSCRIPT_CHARS:
        text = text[:MAX_TRANSCRIPT_CHARS] + "\n\n[Transcript truncated due to length]"

    return text


def _parse_json3(raw: str) -> str:
    data = json.loads(raw)
    parts = []
    for event in data.get('events', []):
        segs = event.get('segs')
        if not segs:
            continue
        line = ''.join(s.get('utf8', '') for s in segs).replace('\n', ' ').strip()
        if line and line != ' ':
            parts.append(line)
    return ' '.join(parts)


def _parse_ttml(raw: str) -> str:
    # Strip XML tags, collapse whitespace
    text = re.sub(r'<[^>]+>', ' ', raw)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _parse_vtt(raw: str) -> str:
    lines = raw.splitlines()
    parts = []
    for line in lines:
        # Skip WEBVTT header, cue timestamps, NOTE lines, and empty lines
        if (line.startswith('WEBVTT') or
                line.startswith('NOTE') or
                re.match(r'^\d{2}:\d{2}', line) or
                '-->' in line or
                line.strip() == ''):
            continue
        # Strip inline tags like <00:00:01.000><c>text</c>
        clean = re.sub(r'<[^>]+>', '', line).strip()
        if clean:
            parts.append(clean)
    return ' '.join(parts)
