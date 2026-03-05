"""
session.py — In-memory session store for interview sessions.
Each session tracks: resume data, generated questions, answers, evaluations.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class InterviewSession:
    session_id: str
    resume_filename: str
    resume_text: str
    resume_sections: dict
    job_description: str
    difficulty: str
    questions: list[dict] = field(default_factory=list)
    current_index: int = 0
    answers: list[dict] = field(default_factory=list)       # raw answers
    evaluations: list[dict] = field(default_factory=list)   # evaluated answers
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed: bool = False


# Global in-memory store { session_id: InterviewSession }
_sessions: dict[str, InterviewSession] = {}


def create_session(
    resume_filename: str,
    resume_text: str,
    resume_sections: dict,
    job_description: str = "",
    difficulty: str = "mid",
) -> InterviewSession:
    session_id = str(uuid.uuid4())
    session = InterviewSession(
        session_id=session_id,
        resume_filename=resume_filename,
        resume_text=resume_text,
        resume_sections=resume_sections,
        job_description=job_description,
        difficulty=difficulty,
    )
    _sessions[session_id] = session
    return session


def get_session(session_id: str) -> InterviewSession | None:
    return _sessions.get(session_id)


def set_questions(session_id: str, questions: list[dict]) -> None:
    s = _sessions.get(session_id)
    if s:
        s.questions = questions
        s.current_index = 0


def current_question(session_id: str) -> dict | None:
    s = _sessions.get(session_id)
    if not s or s.current_index >= len(s.questions):
        return None
    return s.questions[s.current_index]


def advance_question(session_id: str) -> dict | None:
    """Move to the next question and return it, or None if session is done."""
    s = _sessions.get(session_id)
    if not s:
        return None
    s.current_index += 1
    if s.current_index >= len(s.questions):
        s.completed = True
        return None
    return s.questions[s.current_index]


def record_evaluation(session_id: str, evaluation: dict) -> None:
    s = _sessions.get(session_id)
    if s:
        # Attach category from the matching question
        q = next((q for q in s.questions if q["id"] == evaluation.get("question_id")), {})
        evaluation["category"] = q.get("category", "unknown")
        s.evaluations.append(evaluation)


def session_progress(session_id: str) -> dict:
    s = _sessions.get(session_id)
    if not s:
        return {}
    return {
        "total": len(s.questions),
        "current": s.current_index + 1,
        "answered": len(s.evaluations),
        "completed": s.completed,
    }


def delete_session(session_id: str) -> None:
    _sessions.pop(session_id, None)
