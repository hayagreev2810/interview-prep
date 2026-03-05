"""
evaluator.py — Evaluate candidate answers using Groq (free tier).
"""

import json
import os
import re
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

EVAL_SYSTEM = """You are a strict but fair senior interviewer evaluating a candidate's answer.
Be honest and constructive. Point out gaps clearly but encourage improvement.
Always respond with valid JSON only. No markdown, no preamble."""

EVAL_SCHEMA = """
Return JSON with this exact structure:
{
  "score": <integer 1-10>,
  "grade": "Excellent",
  "strengths": ["what the candidate did well"],
  "gaps": ["what was missing or could be stronger"],
  "follow_up_question": "One natural follow-up the interviewer would ask",
  "model_answer_summary": "A concise 3-5 sentence ideal answer"
}
grade must be one of: Excellent, Good, Needs Work, Insufficient
"""


def evaluate_answer(question, candidate_answer, resume_text):
    prompt = f"""
## Interview Question
Category: {question.get('category', 'unknown').upper()}
Difficulty: {question.get('difficulty', 'mid').upper()}
Question: {question['question']}

## Ideal Answer Outline
{chr(10).join(f"- {b}" for b in question.get('ideal_answer_outline', []))}

## Candidate Resume Context
{resume_text[:2000]}

## Candidate's Answer
{candidate_answer.strip() if candidate_answer.strip() else "(No answer — candidate skipped)"}

Evaluate strictly. For behavioral questions check STAR structure.
For technical questions check accuracy and depth.

{EVAL_SCHEMA}
""".strip()

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": EVAL_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=1024,
    )

    raw = response.choices[0].message.content.strip()
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    result = json.loads(raw)
    result["question_id"] = question.get("id", "unknown")
    result["question"] = question["question"]
    result["candidate_answer"] = candidate_answer
    return result


def generate_session_report(evaluations, resume_filename):
    if not evaluations:
        return {"error": "No evaluations to summarize"}

    scores = [e["score"] for e in evaluations if "score" in e]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    by_category = {}
    for e in evaluations:
        cat = e.get("category", "unknown")
        by_category.setdefault(cat, []).append(e["score"])

    category_averages = {
        cat: round(sum(s) / len(s), 1) for cat, s in by_category.items()
    }

    weak = [e["question"] for e in evaluations if e.get("score", 10) < 6]

    if avg_score >= 8.5:
        overall_grade = "Outstanding — Strong Hire"
    elif avg_score >= 7:
        overall_grade = "Good — Likely Hire"
    elif avg_score >= 5.5:
        overall_grade = "Average — Needs Improvement"
    else:
        overall_grade = "Below Bar — More Prep Needed"

    return {
        "resume_filename": resume_filename,
        "total_questions": len(evaluations),
        "average_score": avg_score,
        "overall_grade": overall_grade,
        "category_averages": category_averages,
        "weak_areas": weak,
        "evaluations": evaluations,
    }
