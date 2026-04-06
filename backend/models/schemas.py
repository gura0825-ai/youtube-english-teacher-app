from pydantic import BaseModel
from typing import Dict, List


class ProcessRequest(BaseModel):
    url: str


class QuizItem(BaseModel):
    id: int
    question: str
    options: Dict[str, str]  # {"A": "...", "B": "...", "C": "...", "D": "..."}
    answer: str              # "A" | "B" | "C" | "D"


class ProcessResponse(BaseModel):
    video_id: str
    title: str
    transcript: str
    summary: str
    insights: List[str]
    quiz: List[QuizItem]
