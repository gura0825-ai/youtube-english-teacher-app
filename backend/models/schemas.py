from pydantic import BaseModel
from typing import Dict, List


class ProcessRequest(BaseModel):
    url: str


class QuizItem(BaseModel):
    id: int
    question: str
    options: Dict[str, str]  # {"A": "...", "B": "...", "C": "...", "D": "..."}
    answer: str              # "A" | "B" | "C" | "D"


class TranscriptSegment(BaseModel):
    time: str  # "MM:SS" or "HH:MM:SS"
    text: str


class ProcessResponse(BaseModel):
    video_id: str
    title: str
    transcript: List[TranscriptSegment]
    summary: str
    insights: List[str]
    quiz: List[QuizItem]
