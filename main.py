"""
main.py — FastAPI entry point for the AI Interview Prep app.

Endpoints:
  POST /upload          → parse resume, create session
  POST /generate        → generate questions for a session
  GET  /question/{sid}  → get current question
  POST /answer/{sid}    → submit answer, get evaluation
  POST /next/{sid}      → advance to next question
  GET  /report/{sid}    → get full session report
  DELETE /session/{sid} → clean up session
"""

import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.parser import parse_resume
from app.generator import generate_questions
from app.evaluator import evaluate_answer, generate_session_report
from app import session as sess

app = FastAPI(
    title="AI Interview Prep",
    description="Upload your resume, get tailored interview questions, get scored.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ────────────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    session_id: str
    job_description: str = ""
    difficulty: str = "mid"          # junior | mid | senior
    technical_count: int = 5
    behavioral_count: int = 3
    role_fit_count: int = 2
    culture_count: int = 1


class AnswerRequest(BaseModel):
    answer: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.post("/upload", summary="Upload resume (PDF or DOCX)")
async def upload_resume(
    file: UploadFile = File(...),
    job_description: str = Form(default=""),
    difficulty: str = Form(default="mid"),
):
    """
    Parse resume, create a session.
    Returns session_id + parsed section summary.
    """
    if not file.filename:
        raise HTTPException(400, "No file provided.")

    allowed = (".pdf", ".docx")
    if not any(file.filename.lower().endswith(ext) for ext in allowed):
        raise HTTPException(400, f"Only PDF and DOCX files are supported.")

    file_bytes = await file.read()

    try:
        parsed = parse_resume(file_bytes, file.filename)
    except Exception as e:
        raise HTTPException(422, f"Failed to parse resume: {e}")

    # Create session
    s = sess.create_session(
        resume_filename=parsed["filename"],
        resume_text=parsed["full_text"],
        resume_sections=parsed["sections"],
        job_description=job_description,
        difficulty=difficulty,
    )

    return {
        "session_id": s.session_id,
        "filename": parsed["filename"],
        "char_count": parsed["char_count"],
        "sections_detected": list(parsed["sections"].keys()),
        "message": "Resume parsed successfully. Call /generate to create questions.",
    }


@app.post("/generate", summary="Generate interview questions")
def generate(req: GenerateRequest):
    """
    Generate tailored interview questions using Claude.
    """
    s = sess.get_session(req.session_id)
    if not s:
        raise HTTPException(404, "Session not found.")

    counts = {
        "technical": req.technical_count,
        "behavioral": req.behavioral_count,
        "role_fit": req.role_fit_count,
        "culture": req.culture_count,
    }

    try:
        questions = generate_questions(
            resume_text=s.resume_text,
            sections=s.resume_sections,
            job_description=req.job_description or s.job_description,
            difficulty=req.difficulty or s.difficulty,
            counts=counts,
        )
    except Exception as e:
        raise HTTPException(500, f"Question generation failed: {e}")

    sess.set_questions(req.session_id, questions)

    return {
        "session_id": req.session_id,
        "total_questions": len(questions),
        "categories": {
            cat: len([q for q in questions if q["category"] == cat])
            for cat in ["technical", "behavioral", "role_fit", "culture"]
        },
        "message": "Questions ready. Call /question/{session_id} to start.",
    }


@app.get("/question/{session_id}", summary="Get current question")
def get_question(session_id: str):
    """Return the current question in the session."""
    s = sess.get_session(session_id)
    if not s:
        raise HTTPException(404, "Session not found.")

    q = sess.current_question(session_id)
    if q is None:
        return {
            "done": True,
            "message": "All questions answered. Call /report/{session_id} for your results.",
        }

    progress = sess.session_progress(session_id)

    return {
        "done": False,
        "progress": progress,
        "question": {
            "id": q["id"],
            "category": q["category"],
            "difficulty": q["difficulty"],
            "question": q["question"],
            "context": q.get("context", ""),
            "hint": q.get("hint", ""),
            # Don't reveal ideal answer outline until after they answer
        },
    }


@app.post("/answer/{session_id}", summary="Submit answer and get evaluation")
def submit_answer(session_id: str, req: AnswerRequest):
    """
    Submit the candidate's answer to the current question.
    Returns an evaluation with score, strengths, gaps, and follow-up.
    """
    s = sess.get_session(session_id)
    if not s:
        raise HTTPException(404, "Session not found.")

    q = sess.current_question(session_id)
    if q is None:
        raise HTTPException(400, "No active question. Session may be complete.")

    try:
        evaluation = evaluate_answer(
            question=q,
            candidate_answer=req.answer,
            resume_text=s.resume_text,
        )
    except Exception as e:
        raise HTTPException(500, f"Evaluation failed: {e}")

    sess.record_evaluation(session_id, evaluation)

    return {
        "evaluation": evaluation,
        "ideal_answer_outline": q.get("ideal_answer_outline", []),
        "next": "Call POST /next/{session_id} to move to the next question.",
    }


@app.post("/next/{session_id}", summary="Advance to next question")
def next_question(session_id: str):
    """Move the session forward to the next question."""
    s = sess.get_session(session_id)
    if not s:
        raise HTTPException(404, "Session not found.")

    next_q = sess.advance_question(session_id)

    if next_q is None:
        return {
            "done": True,
            "message": "Interview complete! Call /report/{session_id} for your full report.",
        }

    progress = sess.session_progress(session_id)
    return {
        "done": False,
        "progress": progress,
        "next_question_id": next_q["id"],
        "next_category": next_q["category"],
    }


@app.get("/report/{session_id}", summary="Get full session report")
def get_report(session_id: str):
    """Generate and return the final interview performance report."""
    s = sess.get_session(session_id)
    if not s:
        raise HTTPException(404, "Session not found.")

    if not s.evaluations:
        raise HTTPException(400, "No answers evaluated yet. Complete the interview first.")

    report = generate_session_report(s.evaluations, s.resume_filename)
    return report


@app.delete("/session/{session_id}", summary="Delete a session")
def delete_session(session_id: str):
    """Clean up a session from memory."""
    sess.delete_session(session_id)
    return {"message": f"Session {session_id} deleted."}


@app.get("/", summary="Health check")
def root():
    return {"status": "ok", "app": "AI Interview Prep", "version": "1.0.0"}
