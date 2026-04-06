import logging
import traceback
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

from models.schemas import ProcessRequest, ProcessResponse, QuizItem
from services import claude_service, transcript_service, validator

router = APIRouter()

MAX_QUIZ_RETRIES = 2


@router.post("/process", response_model=ProcessResponse)
async def process_video(request: ProcessRequest):
    # STEP 1: Extract and validate video_id
    video_id = transcript_service.extract_video_id(request.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    # STEP 2: Fetch transcript and title
    try:
        transcript = transcript_service.get_transcript(video_id)
        title = transcript_service.get_video_title(video_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Failed to fetch transcript: {exc}"
        ) from exc

    # STEP 3: Summary + Insights via Claude
    try:
        summary_data = claude_service.get_summary_and_insights(transcript)
        summary = summary_data.get("summary", "")
        insights = summary_data.get("insights", [])
    except Exception as exc:
        logger.error("Summary failed: %s\n%s", exc, traceback.format_exc())
        raise HTTPException(
            status_code=502, detail=f"AI processing failed: {exc}"
        ) from exc

    # STEP 4: Q&A generation with retry loop (max 2 retries)
    quiz_data = None
    last_error = "Unknown error"
    for attempt in range(MAX_QUIZ_RETRIES + 1):
        try:
            raw_quiz = claude_service.get_quiz(transcript)
            is_valid, error_msg = validator.validate_quiz(raw_quiz)
            if is_valid:
                quiz_data = raw_quiz
                break
            last_error = error_msg
        except Exception as exc:
            last_error = str(exc)

    if quiz_data is None:
        raise HTTPException(
            status_code=502,
            detail=f"AI processing failed, please retry (validation: {last_error})",
        )

    # STEP 5: Serialize and return
    quiz_items = [QuizItem(**item) for item in quiz_data]

    return ProcessResponse(
        video_id=video_id,
        title=title,
        transcript=transcript,
        summary=summary,
        insights=insights,
        quiz=quiz_items,
    )
