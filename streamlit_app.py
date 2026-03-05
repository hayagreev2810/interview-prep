"""
streamlit_app.py — Frontend UI for the AI Interview Prep App.
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import requests
import json

API = "http://127.0.0.1:8000"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Interview Prep",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;800&family=JetBrains+Mono:wght@400;600&display=swap');

* { font-family: 'Syne', sans-serif; }
code, pre, .mono { font-family: 'JetBrains Mono', monospace; }

/* Background */
.stApp {
    background: #0d0d14;
    color: #e0e0f0;
}

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Hero */
.hero {
    text-align: center;
    padding: 48px 0 32px;
}
.hero h1 {
    font-size: 3.2rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.1;
    margin-bottom: 8px;
}
.hero h1 span { color: #00e87a; }
.hero p {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    color: #5a5a7a;
    letter-spacing: 0.1em;
}

/* Cards */
.card {
    background: #13131f;
    border: 1px solid #1e1e30;
    border-radius: 4px;
    padding: 24px;
    margin: 16px 0;
}
.card-accent-green { border-left: 3px solid #00e87a; }
.card-accent-blue  { border-left: 3px solid #4da6ff; }
.card-accent-orange{ border-left: 3px solid #ff6b35; }
.card-accent-purple{ border-left: 3px solid #a78bfa; }

/* Question display */
.question-box {
    background: #0a0a12;
    border: 1px solid #2a2a40;
    border-left: 4px solid #00e87a;
    border-radius: 4px;
    padding: 28px;
    margin: 20px 0;
}
.question-text {
    font-size: 1.25rem;
    font-weight: 600;
    color: #ffffff;
    line-height: 1.5;
    margin-bottom: 12px;
}
.question-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #5a5a7a;
    letter-spacing: 0.08em;
}

/* Category badges */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 2px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-right: 6px;
}
.badge-technical  { background: rgba(0,232,122,0.12); color: #00e87a; border: 1px solid #00e87a; }
.badge-behavioral { background: rgba(77,166,255,0.12); color: #4da6ff; border: 1px solid #4da6ff; }
.badge-role_fit   { background: rgba(255,107,53,0.12); color: #ff6b35; border: 1px solid #ff6b35; }
.badge-culture    { background: rgba(167,139,250,0.12); color: #a78bfa; border: 1px solid #a78bfa; }
.badge-junior     { background: rgba(255,220,0,0.1);  color: #ffd700; border: 1px solid #ffd700; }
.badge-mid        { background: rgba(255,107,53,0.1); color: #ff6b35; border: 1px solid #ff6b35; }
.badge-senior     { background: rgba(255,50,50,0.1);  color: #ff5555; border: 1px solid #ff5555; }

/* Score display */
.score-big {
    font-size: 4rem;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    text-align: center;
    padding: 16px;
}
.score-excellent { color: #00e87a; }
.score-good      { color: #4da6ff; }
.score-needs     { color: #ff6b35; }
.score-poor      { color: #ff5555; }

/* Progress bar */
.prog-wrap {
    background: #1e1e30;
    border-radius: 2px;
    height: 4px;
    margin: 12px 0 24px;
    overflow: hidden;
}
.prog-fill {
    height: 4px;
    background: linear-gradient(90deg, #00e87a, #4da6ff);
    border-radius: 2px;
    transition: width 0.4s ease;
}

/* Hint box */
.hint-box {
    background: rgba(255,215,0,0.05);
    border: 1px dashed rgba(255,215,0,0.3);
    border-radius: 4px;
    padding: 14px 18px;
    font-size: 0.88rem;
    color: #c0a840;
    margin: 12px 0;
}

/* Report */
.report-grade {
    text-align: center;
    font-size: 1.4rem;
    font-weight: 800;
    padding: 20px;
    border-radius: 4px;
    margin: 16px 0;
}

/* Streamlit widget overrides */
div[data-testid="stTextArea"] textarea {
    background: #0a0a12 !important;
    border: 1px solid #2a2a40 !important;
    color: #e0e0f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: 4px !important;
}
div[data-testid="stTextArea"] textarea:focus {
    border-color: #00e87a !important;
    box-shadow: 0 0 0 1px #00e87a !important;
}
.stButton button {
    background: #00e87a !important;
    color: #000000 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 10px 28px !important;
    letter-spacing: 0.05em !important;
}
.stButton button:hover {
    background: #00c066 !important;
    transform: translateY(-1px);
}
div[data-testid="stFileUploader"] {
    background: #13131f !important;
    border: 1px dashed #2a2a40 !important;
    border-radius: 4px !important;
}
.stSelectbox select, div[data-testid="stSelectbox"] {
    background: #13131f !important;
    color: #e0e0f0 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key, default in {
    "stage": "upload",           # upload | interview | report
    "session_id": None,
    "current_question": None,
    "progress": {},
    "last_evaluation": None,
    "show_hint": False,
    "show_eval": False,
    "report": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Helpers ───────────────────────────────────────────────────────────────────
def badge(label, kind):
    return f'<span class="badge badge-{kind}">{label}</span>'

def score_class(score):
    if score >= 8: return "score-excellent"
    if score >= 6: return "score-good"
    if score >= 4: return "score-needs"
    return "score-poor"

def progress_bar(current, total):
    pct = int((current / total) * 100) if total else 0
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#5a5a7a;">
            QUESTION {current} OF {total}
        </span>
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#00e87a;">{pct}%</span>
    </div>
    <div class="prog-wrap"><div class="prog-fill" style="width:{pct}%"></div></div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 1 — UPLOAD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.stage == "upload":

    st.markdown("""
    <div class="hero">
        <h1>AI Interview<br><span>Prep</span></h1>
        <p>// upload resume · get grilled · get better</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card card-accent-green">', unsafe_allow_html=True)
    st.markdown("#### 📄 Upload Your Resume")
    resume_file = st.file_uploader("PDF or DOCX", type=["pdf", "docx"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card card-accent-blue">', unsafe_allow_html=True)
    st.markdown("#### ⚙️ Interview Settings")
    col1, col2 = st.columns(2)
    with col1:
        difficulty = st.selectbox("Difficulty", ["junior", "mid", "senior"], index=1)
    with col2:
        tech_count = st.selectbox("Technical Qs", [3, 4, 5, 6, 7], index=2)

    col3, col4 = st.columns(2)
    with col3:
        beh_count = st.selectbox("Behavioral Qs", [2, 3, 4], index=1)
    with col4:
        role_count = st.selectbox("Role-fit Qs", [1, 2, 3], index=1)

    jd = st.text_area("Job Description (optional — paste for targeted questions)", height=100, placeholder="Paste the job description here for more targeted questions...")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀  Start Interview", use_container_width=True):
        if not resume_file:
            st.error("Please upload your resume first.")
        else:
            with st.spinner("Parsing resume..."):
                res = requests.post(
                    f"{API}/upload",
                    files={"file": (resume_file.name, resume_file.getvalue(), resume_file.type)},
                    data={"job_description": jd, "difficulty": difficulty},
                )
            if res.status_code != 200:
                st.error(f"Upload failed: {res.text}")
            else:
                sid = res.json()["session_id"]
                st.session_state.session_id = sid

                with st.spinner("Generating your personalised questions with AI..."):
                    gen = requests.post(f"{API}/generate", json={
                        "session_id": sid,
                        "job_description": jd,
                        "difficulty": difficulty,
                        "technical_count": tech_count,
                        "behavioral_count": beh_count,
                        "role_fit_count": role_count,
                        "culture_count": 1,
                    })
                if gen.status_code != 200:
                    st.error(f"Generation failed: {gen.text}")
                else:
                    # Load first question
                    q_res = requests.get(f"{API}/question/{sid}")
                    q_data = q_res.json()
                    st.session_state.current_question = q_data.get("question")
                    st.session_state.progress = q_data.get("progress", {})
                    st.session_state.stage = "interview"
                    st.session_state.show_eval = False
                    st.session_state.last_evaluation = None
                    st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 2 — INTERVIEW
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "interview":

    sid = st.session_state.session_id
    q = st.session_state.current_question
    prog = st.session_state.progress

    st.markdown("""
    <div style="padding: 24px 0 8px;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:#00e87a;letter-spacing:0.15em;">
            ▸ INTERVIEW IN PROGRESS
        </span>
    </div>
    """, unsafe_allow_html=True)

    if prog:
        progress_bar(prog.get("current", 1), prog.get("total", 1))

    if q:
        cat = q.get("category", "technical")
        diff = q.get("difficulty", "mid")

        st.markdown(f"""
        <div class="question-box">
            <div class="question-meta">
                {badge(cat, cat)}
                {badge(diff, diff)}
            </div>
            <div class="question-text" style="margin-top:14px;">{q['question']}</div>
            <div class="question-meta" style="margin-top:8px;font-size:0.72rem;">{q.get('context','')}</div>
        </div>
        """, unsafe_allow_html=True)

        # Hint toggle
        if st.button("💡 Show Hint"):
            st.session_state.show_hint = not st.session_state.show_hint

        if st.session_state.show_hint and q.get("hint"):
            st.markdown(f'<div class="hint-box">💡 {q["hint"]}</div>', unsafe_allow_html=True)

        # ── Answer input (only if not yet evaluated) ──
        if not st.session_state.show_eval:
            answer = st.text_area(
                "Your Answer",
                height=160,
                placeholder="Type your answer here... be as detailed as you can.",
                key=f"answer_{q['id']}"
            )

            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("✅  Submit Answer", use_container_width=True):
                    if not answer.strip():
                        st.warning("Write something — even a partial answer gets scored!")
                    else:
                        with st.spinner("Evaluating your answer..."):
                            ev = requests.post(
                                f"{API}/answer/{sid}",
                                json={"answer": answer}
                            )
                        if ev.status_code == 200:
                            st.session_state.last_evaluation = ev.json()["evaluation"]
                            st.session_state.show_eval = True
                            st.session_state.show_hint = False
                            st.rerun()
                        else:
                            st.error(f"Error: {ev.text}")
            with col2:
                if st.button("⏭ Skip", use_container_width=True):
                    with st.spinner("Skipping..."):
                        requests.post(f"{API}/answer/{sid}", json={"answer": ""})
                    nxt = requests.post(f"{API}/next/{sid}").json()
                    if nxt.get("done"):
                        st.session_state.stage = "report"
                    else:
                        q_res = requests.get(f"{API}/question/{sid}").json()
                        st.session_state.current_question = q_res.get("question")
                        st.session_state.progress = q_res.get("progress", {})
                        st.session_state.show_eval = False
                        st.session_state.last_evaluation = None
                        st.session_state.show_hint = False
                    st.rerun()

        # ── Evaluation results ──
        if st.session_state.show_eval and st.session_state.last_evaluation:
            ev = st.session_state.last_evaluation
            score = ev.get("score", 0)
            sc = score_class(score)

            st.markdown(f'<div class="score-big {sc}">{score}<span style="font-size:1.5rem">/10</span></div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="text-align:center;font-family:'JetBrains Mono',monospace;font-size:0.85rem;
                        color:#5a5a7a;margin-bottom:20px;">{ev.get('grade','')}</div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<div class="card card-accent-green">', unsafe_allow_html=True)
                st.markdown("**✅ Strengths**")
                for s in ev.get("strengths", []):
                    st.markdown(f"- {s}")
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="card card-accent-orange">', unsafe_allow_html=True)
                st.markdown("**⚠️ Gaps**")
                for g in ev.get("gaps", []):
                    st.markdown(f"- {g}")
                st.markdown('</div>', unsafe_allow_html=True)

            if ev.get("model_answer_summary"):
                st.markdown('<div class="card card-accent-blue">', unsafe_allow_html=True)
                st.markdown("**📖 Model Answer**")
                st.markdown(ev["model_answer_summary"])
                st.markdown('</div>', unsafe_allow_html=True)

            if ev.get("follow_up_question"):
                st.markdown('<div class="card card-accent-purple">', unsafe_allow_html=True)
                st.markdown(f"**🔁 Follow-up:** {ev['follow_up_question']}")
                st.markdown('</div>', unsafe_allow_html=True)

            if st.button("➡️  Next Question", use_container_width=True):
                nxt = requests.post(f"{API}/next/{sid}").json()
                if nxt.get("done"):
                    st.session_state.stage = "report"
                else:
                    q_res = requests.get(f"{API}/question/{sid}").json()
                    st.session_state.current_question = q_res.get("question")
                    st.session_state.progress = q_res.get("progress", {})
                    st.session_state.show_eval = False
                    st.session_state.last_evaluation = None
                    st.session_state.show_hint = False
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STAGE 3 — REPORT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.stage == "report":

    sid = st.session_state.session_id

    if not st.session_state.report:
        with st.spinner("Generating your report..."):
            r = requests.get(f"{API}/report/{sid}")
        if r.status_code == 200:
            st.session_state.report = r.json()
        else:
            st.error(f"Could not load report: {r.text}")
            st.stop()

    report = st.session_state.report

    st.markdown("""
    <div style="text-align:center;padding:32px 0 16px;">
        <span style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;
                     color:#00e87a;letter-spacing:0.15em;">▸ INTERVIEW COMPLETE</span>
        <h2 style="font-size:2.4rem;font-weight:800;color:#fff;margin-top:8px;">Your Results</h2>
    </div>
    """, unsafe_allow_html=True)

    # Overall score
    avg = report.get("average_score", 0)
    sc = score_class(avg)
    st.markdown(f'<div class="score-big {sc}">{avg}<span style="font-size:1.5rem">/10</span></div>', unsafe_allow_html=True)

    grade_colors = {
        "Outstanding": "#00e87a",
        "Good": "#4da6ff",
        "Average": "#ff6b35",
        "Below": "#ff5555",
    }
    grade = report.get("overall_grade", "")
    gcolor = next((v for k, v in grade_colors.items() if k in grade), "#e0e0f0")
    st.markdown(f"""
    <div style="text-align:center;font-size:1.1rem;font-weight:700;color:{gcolor};
                margin-bottom:28px;font-family:'JetBrains Mono',monospace;">{grade}</div>
    """, unsafe_allow_html=True)

    # Category breakdown
    cat_avgs = report.get("category_averages", {})
    if cat_avgs:
        st.markdown("#### 📊 Score by Category")
        cols = st.columns(len(cat_avgs))
        cat_colors = {"technical": "#00e87a", "behavioral": "#4da6ff", "role_fit": "#ff6b35", "culture": "#a78bfa"}
        for i, (cat, score) in enumerate(cat_avgs.items()):
            with cols[i]:
                color = cat_colors.get(cat, "#e0e0f0")
                st.markdown(f"""
                <div style="background:#13131f;border:1px solid #1e1e30;border-top:3px solid {color};
                            padding:16px;text-align:center;border-radius:4px;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;
                                color:#5a5a7a;letter-spacing:0.1em;text-transform:uppercase;">{cat}</div>
                    <div style="font-size:2rem;font-weight:800;color:{color};
                                font-family:'JetBrains Mono',monospace;">{score}</div>
                </div>
                """, unsafe_allow_html=True)

    # Weak areas
    weak = report.get("weak_areas", [])
    if weak:
        st.markdown("#### ⚠️ Areas to Improve")
        st.markdown('<div class="card card-accent-orange">', unsafe_allow_html=True)
        for w in weak:
            st.markdown(f"- {w}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Full breakdown
    with st.expander("📋 Full Question Breakdown"):
        for ev in report.get("evaluations", []):
            score = ev.get("score", 0)
            sc = score_class(score)
            st.markdown(f"""
            <div style="border:1px solid #1e1e30;border-radius:4px;padding:16px;margin:8px 0;background:#0a0a12;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="font-size:0.9rem;color:#e0e0f0;font-weight:600;">{ev.get('question','')}</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:1.2rem;
                                font-weight:800;" class="{sc}">{score}/10</div>
                </div>
                <div style="font-size:0.8rem;color:#5a5a7a;margin-top:8px;">{ev.get('grade','')}</div>
            </div>
            """, unsafe_allow_html=True)

    # JSON export
    st.markdown("#### 💾 Export Report")
    st.download_button(
        label="⬇️  Download Full Report (JSON)",
        data=json.dumps(report, indent=2),
        file_name="interview_report.json",
        mime="application/json",
        use_container_width=True,
    )

    if st.button("🔄  Start New Interview", use_container_width=True):
        for key in ["stage", "session_id", "current_question", "progress",
                    "last_evaluation", "show_hint", "show_eval", "report"]:
            del st.session_state[key]
        st.rerun()
