# AI Interview Prep App

Upload your resume → get tailored technical, behavioral, and role-fit interview questions → get scored by AI.

---

## Stack

- **Python 3.11+** + **FastAPI** — REST API
- **Google Gemini 1.5 Flash** — question generation + answer evaluation (free tier)
- **PyMuPDF** — PDF parsing  
- **python-docx** — DOCX parsing

---

## Setup

### 1. Clone & install

```bash
git clone <your-repo>
cd interview-prep
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set your API key

```bash
cp .env.example .env
# Edit .env and add your Gemini API key:
# GEMINI_API_KEY=AIza...
# Get a free key at: https://aistudio.google.com/app/apikey
```

### 3. Run

```bash
uvicorn main:app --reload
```

Open: http://localhost:8000/docs — full interactive API explorer.

---

## API Flow

```
1. POST /upload          → upload resume PDF/DOCX → get session_id
2. POST /generate        → generate questions for session
3. GET  /question/{sid}  → get current question
4. POST /answer/{sid}    → submit your answer → get score + feedback
5. POST /next/{sid}      → advance to next question
6. GET  /report/{sid}    → full session report
```

### Example curl flow

```bash
# 1. Upload resume
curl -X POST http://localhost:8000/upload \
  -F "file=@my_resume.pdf" \
  -F "difficulty=mid"

# → { "session_id": "abc-123", ... }

# 2. Generate questions
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"session_id": "abc-123", "difficulty": "mid", "technical_count": 5}'

# 3. Get first question
curl http://localhost:8000/question/abc-123

# 4. Submit answer
curl -X POST http://localhost:8000/answer/abc-123 \
  -H "Content-Type: application/json" \
  -d '{"answer": "I used Redis as a cache layer to reduce database load by 60%..."}'

# 5. Advance
curl -X POST http://localhost:8000/next/abc-123

# 6. Repeat 3-5 until done, then:
curl http://localhost:8000/report/abc-123
```

---

## Question Categories

| Category    | Count (default) | Description                                    |
|-------------|-----------------|------------------------------------------------|
| `technical` | 5               | Deep dives on tech the candidate actually used |
| `behavioral`| 3               | STAR-format, grounded in real experience       |
| `role_fit`  | 2               | Motivation, career goals, why this role        |
| `culture`   | 1               | Team dynamics, values, collaboration style     |

---

## Difficulty Levels

- `junior` — fundamentals, explain-the-concept questions
- `mid` — design decisions, trade-offs, real experience
- `senior` — system design, leadership, architecture choices

---

## Project Structure

```
interview-prep/
├── main.py                  # FastAPI app + all routes
├── requirements.txt
├── .env                     # ANTHROPIC_API_KEY (not committed)
└── app/
    ├── parser.py            # PDF/DOCX text extraction
    ├── generator.py         # Claude question generation
    ├── evaluator.py         # Claude answer evaluation + report
    └── session.py           # In-memory session state
```

---

## Next Steps (Phase 5–6)

- [ ] Add Streamlit frontend (`streamlit_app.py`)
- [ ] Add voice input with Whisper
- [ ] Export report as PDF (ReportLab)
- [ ] Persist sessions to SQLite
- [ ] Deploy to Railway / Render
