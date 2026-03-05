# AI Interview Prep App

Upload your resume → get tailored technical, behavioral, and role-fit interview questions → get scored by AI.

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

\

\
