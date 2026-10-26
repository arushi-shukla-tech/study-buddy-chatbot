import os
import io
import json
import requests
import streamlit as st
from datetime import datetime
from html import escape as html_escape
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from xml.sax.saxutils import escape

# =========================================================
# 1. CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

GREEN = "#245C43"
DARK = "#173D2D"
CREAM = "#F7F5EC"
SURFACE = "#FFFFFF"
SOFT_GREEN = "#E8EFE5"
BORDER = "#DCE4D8"
MUTED = "#68776C"

PAGES = [
    "Dashboard",
    "Study Chat",
    "AI Quiz",
    "PDF Notes",
    "Performance",
    "Settings",
]

# =========================================================
# 2. SESSION STATE
# =========================================================

defaults = {
    "chat_history": [],
    "quiz_questions": [],
    "quiz_answers": {},
    "quiz_submitted": False,
    "quiz_score_history": [],
    "pdf_text": "",
    "pdf_name": "",
    "notes_text": "",
    "study_activity": 0,
    "user_name": "Student",
    "quiz_topic": "",
    "difficulty": "Medium",
    "selected_page": "Dashboard",
    "last_summary": "",
    "quiz_result_saved": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Handle dashboard quick navigation.
if "_navigate" in st.session_state:
    destination = st.session_state.pop("_navigate")
    if destination in PAGES:
        st.session_state["selected_page"] = destination

# =========================================================
# 3. PROFESSIONAL UI
# =========================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --green: #245C43;
    --dark: #173D2D;
    --cream: #F7F5EC;
    --surface: #FFFFFF;
    --soft: #E8EFE5;
    --border: #DCE4D8;
    --muted: #68776C;
}

/* Overall application */
.stApp {
    background: var(--cream) !important;
    color: var(--dark) !important;
    font-family: 'DM Sans', sans-serif !important;
}

.block-container {
    max-width: 1220px;
    padding-top: 1.8rem;
    padding-bottom: 2.5rem;
}

h1, h2, h3, h4 {
    color: var(--dark) !important;
    font-family: 'Manrope', sans-serif !important;
    letter-spacing: -0.4px;
}

h1 {
    font-weight: 800 !important;
    font-size: clamp(1.8rem, 4vw, 2.5rem) !important;
}

h2 { font-weight: 750 !important; }
h3 { font-weight: 700 !important; }

p, li, label {
    line-height: 1.65;
}

/* Header and built-in menu */
.stAppHeader,
[data-testid="stHeader"] {
    background: var(--cream) !important;
    border-bottom: 1px solid var(--border) !important;
}

[data-testid="stToolbar"] {
    background: transparent !important;
}

.stAppHeader button,
.stAppHeader button *,
[data-testid="stHeader"] button,
[data-testid="stHeader"] button * {
    color: var(--dark) !important;
    fill: var(--dark) !important;
    stroke: var(--dark) !important;
    opacity: 1 !important;
}

.stAppHeader button,
[data-testid="stHeader"] button {
    background-color: var(--soft) !important;
    border: 1px solid #C8D7C6 !important;
    border-radius: 9px !important;
}

.stAppHeader button:hover,
[data-testid="stHeader"] button:hover {
    background: #D6E5D4 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #F0F1E8 !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] > div:first-child {
    background: #F0F1E8 !important;
}

.brand {
    color: var(--dark);
    font-family: 'Manrope', sans-serif;
    font-size: 21px;
    font-weight: 800;
    padding: 8px 0 2px;
}

.brand-sub {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 20px;
}

.sidebar-label {
    color: var(--muted);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.5px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    border-radius: 10px;
    padding: 9px 10px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #E0E9DC;
}

/* Buttons */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    background: var(--green) !important;
    color: #FFFFFF !important;
    border: 1px solid var(--green) !important;
    border-radius: 10px !important;
    min-height: 43px;
    font-weight: 650 !important;
    transition: all 0.18s ease;
}

.stButton > button *,
.stDownloadButton > button *,
.stFormSubmitButton > button * {
    color: #FFFFFF !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
    background: var(--dark) !important;
    border-color: var(--dark) !important;
    transform: translateY(-1px);
}

/* Form controls */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stChatInput"] textarea {
    background: #FFFFFF !important;
    color: var(--dark) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

[data-baseweb="select"] > div {
    border-radius: 10px !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 17px;
    box-shadow: 0 4px 16px rgba(23,61,45,0.035);
}

[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: var(--dark) !important;
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
}

/* Hero */
.hero {
    background: linear-gradient(125deg, #173D2D, #245C43);
    border-radius: 22px;
    padding: clamp(24px, 4vw, 42px);
    margin: 5px 0 26px;
    box-shadow: 0 10px 28px rgba(23,61,45,0.09);
}

.hero h1, .hero h2, .hero p, .hero span,
.hero strong, .hero div {
    color: #FFFFFF !important;
}

.hero h1 {
    line-height: 1.2;
    margin-bottom: 13px;
}

.hero p {
    color: #E4EEE4 !important;
    max-width: 650px;
}

.eyebrow {
    color: #D5E6D7 !important;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 13px;
}

.hero-note {
    background: rgba(255,255,255,0.09);
    border: 1px solid rgba(255,255,255,0.17);
    border-radius: 12px;
    padding: 14px 16px;
    margin-top: 18px;
}

/* Feature cards */
.feature-card {
    height: 100%;
    min-height: 155px;
    padding: 21px;
    border: 1px solid var(--border);
    border-radius: 15px;
    background: #FFFFFF;
    box-shadow: 0 4px 15px rgba(23,61,45,0.025);
}

.feature-number {
    color: var(--green);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.5px;
}

.feature-title {
    color: var(--dark);
    font-size: 17px;
    font-weight: 800;
    margin: 12px 0 7px;
}

.feature-copy {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.7;
}

.section-caption {
    color: var(--muted);
    font-size: 14px;
}

[data-testid="stFileUploader"] {
    background: #FFFFFF;
    border: 1px dashed #A7BDA5;
    border-radius: 13px;
    padding: 12px;
}

[data-testid="stAlert"] {
    border-radius: 12px;
}

[data-testid="stChatMessage"] {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 13px;
    padding: 12px;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
}

hr {
    border-color: var(--border) !important;
}

.app-footer {
    text-align: center;
    color: var(--muted);
    font-size: 11px;
    letter-spacing: 1.2px;
    padding: 14px 0;
}

@media (max-width: 700px) {
    .block-container {
        padding: 1rem 1rem 2rem;
    }
    .hero {
        border-radius: 16px;
        padding: 23px 19px;
    }
    [data-testid="stMetric"] {
        padding: 12px;
    }
}

footer {
    visibility: hidden;
}
</style>
""",
    unsafe_allow_html=True,
)

# =========================================================
# 4. API KEY AND AI
# =========================================================

def get_api_key():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    return os.getenv("GROQ_API_KEY", "")


def ask_ai(prompt, system_prompt=None, temperature=0.4):
    api_key = get_api_key()

    if not api_key:
        return (
            "Groq API key configure nahi hai. "
            "Streamlit Cloud ke Settings > Secrets mein "
            "GROQ_API_KEY add karein."
        )

    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt,
        })

    messages.append({
        "role": "user",
        "content": prompt,
    })

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-oss-20b",
                "messages": messages,
                "temperature": temperature,
            },
            timeout=90,
        )

        if response.status_code != 200:
            return (
                f"AI request failed ({response.status_code}). "
                "API key, model availability aur usage limits check karein."
            )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return "Request mein time lag raha hai. Please dobara try karein."
    except requests.exceptions.RequestException:
        return "Network connection check karke dobara try karein."
    except (KeyError, IndexError, ValueError):
        return "AI response read nahi ho saka. Please dobara try karein."


# =========================================================
# 5. PDF EXPORT
# =========================================================

def export_pdf(title, body):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=48,
        leftMargin=48,
        topMargin=48,
        bottomMargin=48,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "StudyBuddyTitle",
        parent=styles["Title"],
        textColor=colors.HexColor(GREEN),
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=26,
        spaceAfter=18,
    )

    body_style = ParagraphStyle(
        "StudyBuddyBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        spaceAfter=8,
    )

    story = [Paragraph(escape(title), title_style)]

    for line in body.split("\n"):
        text = escape(line) if line.strip() else " "
        story.append(Paragraph(text, body_style))
        story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)

    return buffer.getvalue()


# =========================================================
# 6. SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:
    st.markdown(
        '<div class="brand">📚 Study Buddy AI</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="brand-sub">Your personal AI study space</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-label">YOUR WORKSPACE</div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        PAGES,
        key="selected_page",
        label_visibility="collapsed",
    )

    st.markdown("---")

    st.markdown("**Study smarter, every day.**")
    st.caption("AI support for learning, practice and revision.")

    st.markdown("---")
    if get_api_key():
        st.caption("AI connection · Key detected")
    else:
        st.caption("AI connection · Setup required")

# =========================================================
# 7. DASHBOARD
# =========================================================

if page == "Dashboard":
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">YOUR PERSONAL STUDY SPACE</div>
            <h1>Learn smarter.<br>Achieve more.</h1>
            <p>
                Your AI-powered study companion for clearer notes,
                focused practice and more confident learning.
            </p>
            <div class="hero-note">
                <strong>One workspace. Better learning.</strong><br>
                <span>Ask questions, practise with quizzes and turn PDFs into revision notes.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    hour = datetime.now().hour
    greeting = (
        "Good morning" if hour < 12
        else "Good afternoon" if hour < 17
        else "Good evening"
    )

    st.markdown(
        f"## {greeting}, {html_escape(st.session_state.user_name)}"
    )
    st.markdown(
        '<div class="section-caption">'
        'Here is your learning overview.</div>',
        unsafe_allow_html=True,
    )

    history = st.session_state.quiz_score_history
    quiz_total = len(history)

    average = (
        round(sum(x["score"] for x in history) / quiz_total)
        if quiz_total else 0
    )

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Quizzes completed", quiz_total)
    m2.metric("Average score", f"{average}%")
    m3.metric("Study sessions", st.session_state.study_activity)
    m4.metric("PDF uploaded", "Yes" if st.session_state.pdf_text else "No")

    st.markdown("## Your learning tools")
    st.markdown(
        '<div class="section-caption">'
        'Choose a tool to continue your study session.</div>',
        unsafe_allow_html=True,
    )
    st.write("")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-number">01 / LEARN</div>
                <div class="feature-title">Study Chat</div>
                <div class="feature-copy">
                    Understand difficult concepts with clear,
                    step-by-step AI explanations.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Open Study Chat", key="go_chat", use_container_width=True):
            st.session_state["_navigate"] = "Study Chat"
            st.rerun()

    with c2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-number">02 / PRACTISE</div>
                <div class="feature-title">AI Quiz</div>
                <div class="feature-copy">
                    Create topic-based MCQs and review
                    your understanding.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Create a Quiz", key="go_quiz", use_container_width=True):
            st.session_state["_navigate"] = "AI Quiz"
            st.rerun()

    with c3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-number">03 / ORGANISE</div>
                <div class="feature-title">PDF Notes</div>
                <div class="feature-copy">
                    Transform text-based PDFs into
                    structured revision material.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Open PDF Notes", key="go_pdf", use_container_width=True):
            st.session_state["_navigate"] = "PDF Notes"
            st.rerun()

    st.markdown("---")
    st.markdown("## Continue learning")

    left, right = st.columns(2)

    with left:
        st.markdown("### Recent document")

        if st.session_state.pdf_name:
            st.success(st.session_state.pdf_name)
        else:
            st.caption("Your uploaded PDF will appear here.")

    with right:
        st.markdown("### Latest quiz")

        if history:
            latest = history[-1]
            st.write(f"**{latest['topic']}**")
            st.write(f"Score: {latest['score']}%")
        else:
            st.caption("Complete a quiz to see your latest result.")

# =========================================================
# 8. STUDY CHAT
# =========================================================

elif page == "Study Chat":
    st.title("Study Chat")
    st.markdown(
        '<div class="section-caption">'
        'Ask questions and learn at your own pace.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("Tips for better answers"):
        st.write(
            "- Mention the subject and topic.\n"
            "- Ask for examples if a concept is difficult.\n"
            "- Request exam-style answers for revision."
        )

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask anything about your studies...")

    if prompt:
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt,
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Preparing your explanation..."):
                answer = ask_ai(
                    prompt,
                    system_prompt=(
                        "You are Study Buddy AI, a helpful academic tutor. "
                        "Explain concepts accurately in simple language. "
                        "Use headings and examples when useful. "
                        "Give structured exam answers when requested. "
                        "Do not invent facts."
                    ),
                )
                st.markdown(answer)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
        })

        st.session_state.study_activity += 1

    if st.session_state.chat_history:
        chat_text = "\n\n".join(
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in st.session_state.chat_history
        )

        st.download_button(
            "Download conversation as TXT",
            data=chat_text,
            file_name="study_chat.txt",
            mime="text/plain",
        )

        if st.button("Clear conversation"):
            st.session_state.chat_history = []
            st.rerun()

# =========================================================
# 9. AI QUIZ
# =========================================================

elif page == "AI Quiz":
    st.title("AI Quiz")
    st.markdown(
        '<div class="section-caption">'
        'Build a practice quiz for the topic you are studying.</div>',
        unsafe_allow_html=True,
    )

    with st.form("quiz_generation_form"):
        topic = st.text_input(
            "Study topic",
            placeholder="e.g. Semiconductor, C programming, Linear algebra",
        )

        q1, q2 = st.columns(2)

        with q1:
            difficulty = st.selectbox(
                "Difficulty",
                ["Easy", "Medium", "Hard"],
                index=1,
            )

        with q2:
            count = st.selectbox(
                "Number of questions",
                [5, 10],
            )

        generate = st.form_submit_button(
            "Generate quiz",
            use_container_width=True,
        )

    if generate:
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            prompt = f"""
Create exactly {count} multiple-choice questions about {topic}.
Difficulty: {difficulty}.

Return only valid JSON:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": 0,
      "explanation": "Short explanation"
    }}
  ]
}}

Requirements:
- answer is an integer from 0 to 3.
- Each question has exactly four options.
- Keep questions accurate, relevant and distinct.
- Do not include Markdown fences.
"""

            with st.spinner("Creating your quiz..."):
                raw = ask_ai(
                    prompt,
                    system_prompt=(
                        "You create accurate academic MCQs. "
                        "Return valid JSON following the requested schema."
                    ),
                    temperature=0.3,
                )

            try:
                start = raw.find("{")
                end = raw.rfind("}") + 1

                if start < 0 or end <= start:
                    raise ValueError("No JSON found")

                parsed = json.loads(raw[start:end])
                questions = parsed.get("questions", [])
                valid = []

                for q in questions[:count]:
                    options = q.get("options", [])
                    answer = q.get("answer")

                    if (
                        isinstance(q.get("question"), str)
                        and isinstance(options, list)
                        and len(options) == 4
                        and all(isinstance(x, str) for x in options)
                        and isinstance(answer, int)
                        and not isinstance(answer, bool)
                        and 0 <= answer <= 3
                    ):
                        valid.append({
                            "question": q["question"],
                            "options": options,
                            "answer": answer,
                            "explanation": q.get("explanation", ""),
                        })

                if not valid:
                    raise ValueError("No valid questions")

                st.session_state.quiz_questions = valid
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_result_saved = False
                st.session_state.quiz_topic = topic.strip()
                st.session_state.difficulty = difficulty
                st.rerun()

            except (ValueError, KeyError, TypeError, json.JSONDecodeError):
                st.error(
                    "Quiz generate nahi ho saka. "
                    "Please dobara try karein."
                )

    questions = st.session_state.quiz_questions

    if questions:
        st.markdown("---")
        st.subheader(st.session_state.quiz_topic)
        st.caption(
            f"{st.session_state.difficulty} · "
            f"{len(questions)} questions"
        )

        # Use widget state directly. Do not overwrite answers on every rerun.
        if not st.session_state.quiz_submitted:
            with st.form("quiz_answer_form"):
                for i, q in enumerate(questions):
                    st.markdown(f"**Question {i + 1}. {q['question']}**")

                    selected = st.radio(
                        f"Answer for question {i + 1}",
                        options=range(4),
                        format_func=lambda idx, opts=q["options"]: opts[idx],
                        index=st.session_state.quiz_answers.get(i),
                        key=f"answer_{i}",
                        label_visibility="collapsed",
                    )

                    st.session_state.quiz_answers[i] = selected
                    st.markdown("---")

                submitted = st.form_submit_button(
                    "Submit answers",
                    use_container_width=True,
                )

            if submitted:
                # Form state is the authoritative source at submission time.
                answers = {}
                for i in range(len(questions)):
                    value = st.session_state.get(f"answer_{i}")
                    answers[i] = value

                st.session_state.quiz_answers = answers

                score = sum(
                    1
                    for i, q in enumerate(questions)
                    if answers.get(i) == q["answer"]
                )

                percentage = round(score / len(questions) * 100)

                st.session_state.quiz_submitted = True

                if not st.session_state.quiz_result_saved:
                    st.session_state.quiz_score_history.append({
                        "topic": st.session_state.quiz_topic,
                        "score": percentage,
                        "correct": score,
                        "total": len(questions),
                        "date": datetime.now().strftime("%d %b %Y"),
                    })
                    st.session_state.quiz_result_saved = True

                st.rerun()

        if st.session_state.quiz_submitted:
            answers = st.session_state.quiz_answers
            score = sum(
                1
                for i, q in enumerate(questions)
                if answers.get(i) == q["answer"]
            )
            percentage = round(score / len(questions) * 100)

            st.success(
                f"Your score: {score}/{len(questions)} · {percentage}%"
            )
            st.progress(percentage / 100)

            for i, q in enumerate(questions):
                chosen = answers.get(i)
                correct = q["answer"]

                if chosen == correct:
                    st.markdown(f"**Question {i + 1} — Correct**")
                else:
                    st.markdown(f"**Question {i + 1} — Review**")
                    st.write(f"Correct answer: {q['options'][correct]}")

                if q["explanation"]:
                    st.caption(q["explanation"])

                st.markdown("---")

            if st.button("Create another quiz", use_container_width=True):
                for i in range(len(questions)):
                    key = f"answer_{i}"
                    if key in st.session_state:
                        del st.session_state[key]

                st.session_state.quiz_questions = []
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_result_saved = False
                st.rerun()

# =========================================================
# 10. PDF NOTES
# =========================================================

elif page == "PDF Notes":
    st.title("PDF Notes")
    st.markdown(
        '<div class="section-caption">'
        'Turn your study material into organised revision notes.</div>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Upload a PDF document",
        type=["pdf"],
        help="Text-based PDFs are supported. Image-only PDFs may require OCR.",
    )

    if uploaded is not None:
        is_new_file = uploaded.name != st.session_state.pdf_name

        if is_new_file or not st.session_state.pdf_text:
            try:
                reader = PdfReader(uploaded)

                extracted = "\n".join(
                    page.extract_text() or ""
                    for page in reader.pages
                )

                if not extracted.strip():
                    st.warning(
                        "Text extract nahi hua. "
                        "PDF scanned image ho sakta hai."
                    )
                else:
                    st.session_state.pdf_text = extracted[:60000]
                    st.session_state.pdf_name = uploaded.name
                    st.session_state.notes_text = ""
                    st.success(f"Uploaded: {uploaded.name}")

            except Exception:
                st.error("PDF read nahi ho saka. Please check the file.")

    if st.session_state.pdf_text:
        word_count = len(st.session_state.pdf_text.split())

        st.markdown("### Document overview")

        a, b = st.columns(2)
        a.metric("Extracted words", word_count)
        b.metric("Document", st.session_state.pdf_name)

        with st.expander("Preview extracted text"):
            st.text(st.session_state.pdf_text[:5000])

        task = st.selectbox(
            "Choose your study material",
            [
                "Simple revision notes",
                "Detailed summary",
                "Important exam questions",
                "Key definitions",
                "Explain in simple English",
            ],
        )

        if st.button(
            "Generate study material",
            use_container_width=True,
        ):
            prompt = f"""
Task: {task}

Use only the supplied source material.
Keep the result clear, accurate and structured.
Do not invent source-specific facts. If information is absent,
say so instead of guessing.

SOURCE MATERIAL:
{st.session_state.pdf_text}
"""

            with st.spinner("Preparing your notes..."):
                notes = ask_ai(
                    prompt,
                    system_prompt=(
                        "You are a careful academic notes assistant. "
                        "Stay grounded in the supplied source."
                    ),
                    temperature=0.2,
                )

                st.session_state.notes_text = notes
                st.session_state.last_summary = notes

        if st.session_state.notes_text:
            st.markdown("---")
            st.markdown("### Your study material")
            st.markdown(st.session_state.notes_text)

            st.download_button(
                "Download notes as TXT",
                data=st.session_state.notes_text,
                file_name="study_notes.txt",
                mime="text/plain",
                use_container_width=True,
            )

            try:
                pdf_data = export_pdf(
                    "Study Buddy AI - Study Notes",
                    st.session_state.notes_text,
                )

                st.download_button(
                    "Download notes as PDF",
                    data=pdf_data,
                    file_name="study_notes.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )

            except Exception:
                st.caption("PDF export unavailable. Download the TXT version.")

# =========================================================
# 11. PERFORMANCE
# =========================================================

elif page == "Performance":
    st.title("Your Performance")
    st.markdown(
        '<div class="section-caption">'
        'Review your quiz scores and track your progress.</div>',
        unsafe_allow_html=True,
    )

    history = st.session_state.quiz_score_history

    if not history:
        st.info(
            "Complete your first AI quiz to see your performance here."
        )

    else:
        total = len(history)
        average = round(sum(x["score"] for x in history) / total)
        best = max(x["score"] for x in history)

        a, b, c = st.columns(3)
        a.metric("Quizzes completed", total)
        b.metric("Average score", f"{average}%")
        c.metric("Best score", f"{best}%")

        st.markdown("---")
        st.subheader("Score history")

        for item in reversed(history):
            with st.container(border=True):
                left, right = st.columns([3, 1])

                with left:
                    st.markdown(f"**{item['topic']}**")
                    st.caption(
                        f"{item['date']} · "
                        f"{item['correct']}/{item['total']} correct"
                    )

                with right:
                    st.metric("Score", f"{item['score']}%")

                st.progress(item["score"] / 100)

        report = "\n".join(
            f"{x['date']} | {x['topic']} | "
            f"{x['correct']}/{x['total']} | {x['score']}%"
            for x in history
        )

        st.download_button(
            "Export performance report",
            data="Date | Topic | Result | Score\n" + report,
            file_name="performance_report.txt",
            mime="text/plain",
        )

# =========================================================
# 12. SETTINGS
# =========================================================

elif page == "Settings":
    st.title("Settings")
    st.markdown(
        '<div class="section-caption">'
        'Manage your profile and application settings.</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Your profile")

    with st.form("profile_form"):
        name = st.text_input(
            "Display name",
            value=st.session_state.user_name,
        )

        save_profile = st.form_submit_button("Save profile")

    if save_profile:
        st.session_state.user_name = name.strip() or "Student"
        st.success("Profile updated.")

    st.markdown("---")
    st.subheader("AI connection")

    if get_api_key():
        st.success("Groq API key detected.")
    else:
        st.warning(
            "Groq API key not found. Add GROQ_API_KEY to Streamlit secrets."
        )

    st.markdown("---")
    st.subheader("Workspace data")

    st.caption(
        "This version uses Streamlit session state. "
        "Data may reset when the session restarts."
    )

    if st.button("Clear chat history"):
        st.session_state.chat_history = []
        st.success("Chat history cleared.")

    if st.button("Reset quiz results"):
        st.session_state.quiz_score_history = []
        st.success("Quiz results cleared.")

    st.markdown("---")
    st.subheader("About Study Buddy AI")

    st.write(
        "A student-focused workspace for AI explanations, "
        "practice quizzes and PDF-based study notes."
    )

# =========================================================
# 13. FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
    <div class="app-footer">
        STUDY BUDDY AI &nbsp; · &nbsp; YOUR LEARNING WORKSPACE
    </div>
    """,
    unsafe_allow_html=True,
)
