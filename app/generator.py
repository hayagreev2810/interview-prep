"""
generator.py — Generate tailored interview questions using Groq (free tier).
"""

import json
import os
import re
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are an expert technical interviewer. 
You MUST respond with ONLY a valid JSON object. 
No explanation, no markdown, no code fences, no preamble. 
Start your response with { and end with }"""


def build_prompt(resume_text, sections, job_description, difficulty, counts):
    jd_block = f"\nJob Description:\n{job_description.strip()}" if job_description.strip() else ""
    skills_block = f"\nSkills: {sections['skills']}" if "skills" in sections else ""
    experience_block = f"\nExperience: {sections['experience'][:1500]}" if "experience" in sections else ""

    total = counts.get('technical',5) + counts.get('behavioral',3) + counts.get('role_fit',2) + counts.get('culture',1)

    return f"""Generate {total} interview questions based on this resume.
Resume: {resume_text[:3000]}
{skills_block}
{experience_block}
{jd_block}

Difficulty: {difficulty}
Generate: {counts.get('technical',5)} technical, {counts.get('behavioral',3)} behavioral, {counts.get('role_fit',2)} role_fit, {counts.get('culture',1)} culture questions.

Return ONLY this JSON structure, nothing else:
{{
  "questions": [
    {{
      "id": "q1",
      "category": "technical",
      "difficulty": "{difficulty}",
      "question": "question text here",
      "context": "why this question relates to the resume",
      "hint": "what a good answer covers",
      "ideal_answer_outline": ["point 1", "point 2", "point 3"]
    }}
  ]
}}

category must be one of: technical, behavioral, role_fit, culture
Start response with {{ immediately."""


def generate_questions(resume_text, sections, job_description="", difficulty="mid", counts=None):
    if counts is None:
        counts = {"technical": 5, "behavioral": 3, "role_fit": 2, "culture": 1}

    prompt = build_prompt(resume_text, sections, job_description, difficulty, counts)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=4096,
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"^```\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()

    # Find JSON object in response
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    data = json.loads(raw)
    questions = data.get("questions", [])

    for i, q in enumerate(questions):
        q["id"] = f"q{i + 1}"

    return questions
