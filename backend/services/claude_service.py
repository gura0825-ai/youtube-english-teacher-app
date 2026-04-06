import json
import os
import re

from google import genai

MODEL = "gemini-2.5-flash"
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def _extract_json(text: str) -> str:
    """Strip markdown code fences (```json ... ```) if present, then return raw JSON string."""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    return text.strip()


def get_summary_and_insights(transcript: str) -> dict:
    """
    Call Gemini to summarize the transcript and extract key insights.
    Returns {"summary": str, "insights": [str, ...]}.
    """
    prompt = f"""You are an English education assistant. Analyze the following video transcript.

STRICT RULE: Use ONLY the information in the transcript below. Do NOT use any external knowledge.

---TRANSCRIPT START---
{transcript}
---TRANSCRIPT END---

Respond with valid JSON only — no markdown, no explanation outside the JSON:
{{
  "summary": "A comprehensive summary in 3–5 paragraphs covering the main points.",
  "insights": [
    "Most important takeaway from the video",
    "Second key insight",
    "Third key insight"
  ]
}}

Requirements:
- Summary: 3–5 paragraphs in English
- Insights: 3–5 bullet items, each a single concise sentence in English"""

    response = _get_client().models.generate_content(model=MODEL, contents=prompt)
    raw = response.text
    return json.loads(_extract_json(raw))


def get_quiz(transcript: str) -> list:
    """
    Call Gemini to generate exactly 20 multiple-choice questions from the transcript.
    Returns a list of dicts matching the QuizItem schema.
    """
    prompt = f"""You are an English education assistant. Create a multiple-choice quiz based on this transcript.

STRICT RULE: Use ONLY the information in the transcript below. Do NOT use any external knowledge.

---TRANSCRIPT START---
{transcript}
---TRANSCRIPT END---

Respond with a valid JSON array only — no markdown, no explanation:
[
  {{
    "id": 1,
    "question": "What does the speaker say about [topic]?",
    "options": {{
      "A": "First option",
      "B": "Second option",
      "C": "Third option",
      "D": "Fourth option"
    }},
    "answer": "B"
  }}
]

Requirements:
- Exactly 20 questions
- All questions and options in English
- One correct answer per question (value must be "A", "B", "C", or "D")
- Three plausible but incorrect distractors grounded in the transcript context
- Vary difficulty: comprehension, inference, vocabulary, main idea"""

    response = _get_client().models.generate_content(model=MODEL, contents=prompt)
    raw = response.text
    return json.loads(_extract_json(raw))
