
import os
import io
import json
import random
import requests
import streamlit as st
from datetime import datetime
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from xml.sax.saxutils import escape

# --------------------------------------------------
# APP CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

GREEN = "#245C43"
DARK_GREEN = "#173D2D"
LIGHT_GREEN = "#E7EFE5"
CREAM = "#F7F5EC"
WHITE = "#FFFFFF"
MUTED = "#6C786F"
BORDER = "#E2E7DE"

# --------------------------------------------------
# PROFESSIONAL DESIGN
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --green: #245C43;
    --dark-green: #173D2D;
    --cream: #F7F5EC;
    --light-green: #E7EFE5;
    --border: #E2E7DE;
    --muted: #6C786F;
}

.stApp {
    background: var(--cream);
    color: var(--dark-green);
    font-family: 'DM Sans', sans-serif;
}

.stAppHeader {
    background: var(--cream) !important;
    border-bottom: 1px solid var(--border) !important;
}

[data-testid="stHeader"] {
    background: var(--cream) !important;
}

.stAppHeader button,
.stAppHeader button svg,
[data-testid="stHeader"] button,
[data-testid="stHeader"] button svg {
    color: var(--dark-green) !important;
    fill: var(--dark-green) !important;
    stroke: var(--dark-green) !important;
    opacity: 1 !important;
}

.stAppHeader button:hover,
[data-testid="stHeader"] button:hover {
    background: var(--light-green) !important;
    border-radius: 8px !important;
}

h1, h2, h3, h4 {
    font-family: 'Manrope', sans-serif !important;
    color: var(--dark-green) !important;
    letter-spacing: -0.5px;
}

h1 {
    font-size: clamp(1.8rem, 4vw, 2.6rem) !important;
    font-weight: 800 !important;
}

h2 { font-weight: 750 !important; }
h3 { font-weight: 700 !important; }

p, label, li {
    color: var(--dark-green);
}

[data-testid="stSidebar"] {
    background: #F0F1E8 !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: var(--dark-green);
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 8px 10px;
    border-radius: 10px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #E2EADD;
}

div.stButton > button,
div[data-testid="stDownloadButton"] > button {
    background: var(--green);
    color: white !important;
    border: 1px solid var(--green);
    border-radius: 10px;
    padding: 0.62rem 1rem;
    font-weight: 650;
    transition: all 0.2s ease;
}

div.stButton > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
    background: var(--dark-green);
    border-color: var(--dark-green);
    color: white !important;
    transform: translateY(-1px);
}

div.stButton > button p,
div[data-testid="stDownloadButton"] > button p {
    color: white !important;
}

input, textarea, [data-baseweb="select"] {
    border-radius: 10px !important;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #FFFFFF !important;
    border-color: var(--border) !important;
    color: var(--dark-green) !important;
}

[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 18px 20px;
    box-shadow: 0 3px 12px rgba(23,61,45,0.035);
}

[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    color: var(--dark-green) !important;
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 8px 8px 0 0;
    color: var(--muted);
    padding: 10px 15px;
}

.stTabs [aria-selected="true"] {
    color: var(--green) !important;
    border-bottom: 3px solid var(--green) !important;
}

hr {
    border-color: var(--border) !important;
}

.hero {
    background: linear-gradient(125deg, #173D2D 0%, #245C43 65%, #397356 100%);
    border-radius: 22px;
    padding: clamp(24px, 4vw, 42px);
    color: white;
    margin: 8px 0 25px 0;
    position: relative;
    overflow: hidden;
}

.hero h1, .hero h2, .hero p, .hero span {
    color: white !important;
}

.hero h1 {
    line-height: 1.2;
    margin-bottom: 12px;
}

.hero p {
    color: #E3EEE4 !important;
    font-size: 1.02rem;
    max-width: 620px;
}

.eyebrow {
    font-size: 0.74rem;
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #D5E6D7 !important;
    margin-bottom: 12px;
}

.hero-bubble {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 16px;
    padding: 18px;
    margin-top: 20px;
}

.panel {
    background: #FFFFFF;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    min-height: 130px;
}

.panel-title {
    font-weight: 750;
    font-size: 1.04rem;
    color: var(--dark-green);
    margin-bottom: 8px;
}

.panel-copy {
    color: var(--muted);
    font-size: 0.91rem;
    line-height: 1.6;
}

.small-label {
    font-size: 0.76rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 700;
}

.brand {
    font-family: 'Manrope', sans-serif;
    font-size: 1.25rem;
    font-weight: 800;
    color: var(--dark-green);
    padding: 8px 0 3px 0;
}

.brand-sub {
    color: var(--muted);
    font-size: 0.83rem;
    margin-bottom: 20px;
}

div[data-testid="stFileUploader"] {
    background: white;
    border: 1px dashed #B6C9B7;
    border-radius: 14px;
    padding: 12px;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

[data-testid="stChatMessage"] {
    background: white;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 12px;
}

footer { visibility: hidden; }

@media (max-width: 700px) {
    .hero { padding: 24px 20px; border-radius: 17px; }
    [data-testid="stMetric"] { padding: 12px; }
    h1 { font-size: 1.8rem !important; }
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------
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
    "last_summary": "",
    "user_name": "Student",
    "quiz_topic": "",
    "quiz_count": 5,
    "difficulty": "Medium",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --------------------------------------------------
# AI CONNECTION
# --------------------------------------------------
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
            "Streamlit secrets mein GROQ_API_KEY add karein."
        )

    messages = []
    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    messages.append({"role": "user", "content": prompt})

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-oss-20b",
                "messages": messages,
                "temperature": temperature
            },
            timeout=90
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

def export_pdf(title, body):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=48,
        leftMargin=48,
        topMargin=48,
        bottomMargin=48
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "AppTitle",
        parent=styles["Title"],
        textColor=colors.HexColor(GREEN),
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=28,
        spaceAfter=18
    )
    body_style = ParagraphStyle(
        "AppBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=16,
        spaceAfter=10
    )

    story = [Paragraph(escape(title), title_style)]
    for paragraph in body.split("\n"):
        safe_text = escape(paragraph) if paragraph.strip() else " "
        story.append(Paragraph(safe_text, body_style))
        story.append(Spacer(1, 5))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------
with st.sidebar:
    st.markdown('<div class="brand">📚 Study Buddy AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-sub">Your personal AI study space</div>', unsafe_allow_html=True)

    st.markdown("---")
    page = st.radio(
        "WORKSPACE",
        [
            "Dashboard",
            "Study Chat",
            "AI Quiz",
            "PDF Notes",
            "Performance",
            "Settings"
        ],
        label_visibility="visible"
    )

    st.markdown("---")
    st.markdown("**Your workspace**")
    st.caption("Learn smarter. Stay consistent.")
    st.markdown("---")
    st.caption("Study Buddy AI · Student edition")

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
if page == "Dashboard":
    st.markdown("""
    <div class="hero">
        <div class="eyebrow">YOUR PERSONAL STUDY SPACE</div>
        <h1>Learn smarter.<br>Achieve more.</h1>
        <p>Your AI-powered study companion for clearer notes,
        focused practice and better learning sessions.</p>
        <div class="hero-bubble">
            <strong>One workspace. Better learning.</strong><br>
            <span>Ask questions, create quizzes and turn PDFs into notes.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    current_hour = datetime.now().hour
    greeting = (
        "Good morning" if current_hour < 12 else
        "Good afternoon" if current_hour < 17 else
        "Good evening"
    )

    st.markdown(f"## {greeting}, {st.session_state.user_name} 👋")
    st.write("Here's your study workspace at a glance.")

    total_quizzes = len(st.session_state.quiz_score_history)
    avg_score = (
        round(sum(x["score"] for x in st.session_state.quiz_score_history)
              / total_quizzes)
        if total_quizzes else 0
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Quizzes completed", total_quizzes)
    c2.metric("Average score", f"{avg_score}%")
    c3.metric("Study sessions", st.session_state.study_activity)
    c4.metric("PDF uploaded", "Yes" if st.session_state.pdf_text else "No")

    st.markdown("## Your learning tools")
    a, b, c = st.columns(3)

    with a:
        st.markdown("""
        <div class="panel">
          <div class="small-label">01 · LEARN</div>
          <div class="panel-title">AI Study Chat</div>
          <div class="panel-copy">Ask questions and understand difficult concepts in simple language.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Study Chat", use_container_width=True):
            st.session_state.study_activity += 1
            st.session_state["_navigate"] = "Study Chat"
            st.rerun()

    with b:
        st.markdown("""
        <div class="panel">
          <div class="small-label">02 · PRACTICE</div>
          <div class="panel-title">AI Quiz</div>
          <div class="panel-copy">Generate topic-based MCQs and test your understanding.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Create a Quiz", use_container_width=True):
            st.session_state["_navigate"] = "AI Quiz"
            st.rerun()

    with c:
        st.markdown("""
        <div class="panel">
          <div class="small-label">03 · ORGANISE</div>
          <div class="panel-title">PDF Notes</div>
          <div class="panel-copy">Upload study material and turn it into concise notes.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open PDF Notes", use_container_width=True):
            st.session_state["_navigate"] = "PDF Notes"
            st.rerun()

    if "_navigate" in st.session_state:
        target = st.session_state.pop("_navigate")
        st.info(f"Select **{target}** from the sidebar to open it.")

    st.markdown("---")
    st.markdown("### Continue your learning")
    if st.session_state.pdf_name:
        st.write(f"Last uploaded document: **{st.session_state.pdf_name}**")
    else:
        st.caption("Your uploaded documents will appear here after you add a PDF.")

    if st.session_state.quiz_score_history:
        latest = st.session_state.quiz_score_history[-1]
        st.write(
            f"Latest quiz: **{latest['topic']}** · "
            f"Score: **{latest['score']}%**"
        )
    else:
        st.caption("Complete your first quiz to start tracking your progress.")

# --------------------------------------------------
# STUDY CHAT
# --------------------------------------------------
elif page == "Study Chat":
    st.title("Study Chat")
    st.write("Ask a question. Get a clear, student-friendly explanation.")

    with st.expander("Tips for better answers"):
        st.write(
            "- Mention your subject and topic.\n"
            "- Ask for examples when a concept feels difficult.\n"
            "- Request exam-style answers when revising."
        )

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_prompt = st.chat_input("Ask anything about your studies...")

    if user_prompt:
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_prompt
        })

        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Preparing your explanation..."):
                system = (
                    "You are Study Buddy AI, a helpful academic tutor. "
                    "Explain concepts accurately in clear, simple language. "
                    "Use headings and examples when useful. "
                    "If the student requests exam notes, provide structured "
                    "answers suitable for their level. Do not invent facts."
                )
                answer = ask_ai(
                    user_prompt,
                    system_prompt=system
                )
                st.markdown(answer)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })
        st.session_state.study_activity += 1

    if st.session_state.chat_history:
        chat_text = "\n\n".join(
            f"{m['role'].upper()}: {m['content']}"
            for m in st.session_state.chat_history
        )
        st.download_button(
            "Download conversation as TXT",
            data=chat_text,
            file_name="study_chat.txt",
            mime="text/plain"
        )

        if st.button("Clear conversation"):
            st.session_state.chat_history = []
            st.rerun()

# --------------------------------------------------
# AI QUIZ
# --------------------------------------------------
elif page == "AI Quiz":
    st.title("AI Quiz")
    st.write("Create a practice quiz for the topic you're studying.")

    with st.form("quiz_form"):
        topic = st.text_input(
            "Topic",
            placeholder="e.g. Semiconductor, C programming, Linear algebra"
        )

        col1, col2 = st.columns(2)
        with col1:
            difficulty = st.selectbox(
                "Difficulty",
                ["Easy", "Medium", "Hard"]
            )
        with col2:
            count = st.selectbox(
                "Number of questions",
                [5, 10]
            )

        generate = st.form_submit_button(
            "Generate Quiz",
            use_container_width=True
        )

    if generate:
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            prompt = f"""
Create exactly {count} multiple-choice questions about: {topic}.
Difficulty: {difficulty}.

Return ONLY valid JSON in this format:
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

Rules:
- answer must be a zero-based integer from 0 to 3.
- Each question must have exactly four options.
- The questions must be accurate and relevant.
- Avoid duplicate questions.
- Do not put Markdown fences around the JSON.
"""
            with st.spinner("Creating your quiz..."):
                raw = ask_ai(
                    prompt,
                    system_prompt=(
                        "You create accurate academic MCQs. "
                        "Follow the requested JSON structure exactly."
                    ),
                    temperature=0.3
                )

            try:
                start = raw.find("{")
                end = raw.rfind("}") + 1
                parsed = json.loads(raw[start:end])
                questions = parsed["questions"]

                valid = []
                for q in questions[:count]:
                    options = q.get("options", [])
                    answer = q.get("answer")
                    if (
                        isinstance(q.get("question"), str)
                        and len(options) == 4
                        and isinstance(answer, int)
                        and 0 <= answer <= 3
                    ):
                        valid.append({
                            "question": q["question"],
                            "options": options,
                            "answer": answer,
                            "explanation": q.get("explanation", "")
                        })

                if not valid:
                    raise ValueError("No valid questions")

                st.session_state.quiz_questions = valid
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_topic = topic
                st.session_state.difficulty = difficulty
                st.rerun()

            except (ValueError, KeyError, TypeError, json.JSONDecodeError):
                st.error(
                    "Quiz generate nahi ho saka. Please try again with another topic."
                )

    if st.session_state.quiz_questions:
        st.markdown("---")
        st.markdown(
            f"### {st.session_state.quiz_topic} "
            f"<span style='color:#6C786F;font-size:14px'>"
            f"· {st.session_state.difficulty}</span>",
            unsafe_allow_html=True
        )

        with st.form("answer_quiz"):
            for i, q in enumerate(st.session_state.quiz_questions):
                st.markdown(f"**Q{i + 1}. {q['question']}**")
                selected = st.radio(
                    f"Choose your answer for question {i + 1}",
                    options=list(range(4)),
                    format_func=lambda x, opts=q["options"]: opts[x],
                    key=f"quiz_answer_{i}",
                    index=None,
                    label_visibility="collapsed",
                    disabled=st.session_state.quiz_submitted
                )
                st.session_state.quiz_answers[i] = selected
                st.markdown("---")

            if not st.session_state.quiz_submitted:
                submit = st.form_submit_button(
                    "Submit Answers",
                    use_container_width=True
                )
            else:
                submit = False

        if submit:
            score = sum(
                1 for i, q in enumerate(st.session_state.quiz_questions)
                if st.session_state.quiz_answers.get(i) == q["answer"]
            )
            total = len(st.session_state.quiz_questions)
            percentage = round(score / total * 100)

            st.session_state.quiz_submitted = True
            st.session_state.quiz_score_history.append({
                "topic": st.session_state.quiz_topic,
                "score": percentage,
                "correct": score,
                "total": total,
                "date": datetime.now().strftime("%d %b %Y")
            })
            st.rerun()

        if st.session_state.quiz_submitted:
            total = len(st.session_state.quiz_questions)
            score = sum(
                1 for i, q in enumerate(st.session_state.quiz_questions)
                if st.session_state.quiz_answers.get(i) == q["answer"]
            )
            percentage = round(score / total * 100)

            st.success(f"Your score: {score}/{total} · {percentage}%")
            st.progress(percentage / 100)

            for i, q in enumerate(st.session_state.quiz_questions):
                chosen = st.session_state.quiz_answers.get(i)
                correct = q["answer"]

                if chosen == correct:
                    st.markdown(f"**Q{i + 1}. Correct**")
                else:
                    st.markdown(f"**Q{i + 1}. Review this answer**")
                    st.write(f"Correct answer: {q['options'][correct]}")

                if q["explanation"]:
                    st.caption(q["explanation"])

            if st.button("Create another quiz"):
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.rerun()

# --------------------------------------------------
# PDF NOTES
# --------------------------------------------------
elif page == "PDF Notes":
    st.title("PDF Notes")
    st.write("Upload your study material to create clear revision notes.")

    uploaded = st.file_uploader(
        "Upload a PDF document",
        type=["pdf"],
        help="Text-based PDFs are supported. Scanned image-only PDFs may need OCR."
    )

    if uploaded is not None:
        if (
            uploaded.name != st.session_state.pdf_name
            or not st.session_state.pdf_text
        ):
            try:
                reader = PdfReader(uploaded)
                extracted = "\n".join(
                    page.extract_text() or ""
                    for page in reader.pages
                )

                if not extracted.strip():
                    st.warning(
                        "Is PDF se text extract nahi hua. "
                        "Ho sakta hai document scanned image ho."
                    )
                else:
                    st.session_state.pdf_text = extracted[:60000]
                    st.session_state.pdf_name = uploaded.name
                    st.success(
                        f"Uploaded successfully: {uploaded.name}"
                    )
            except Exception:
                st.error("PDF read nahi ho saka. Please check the file.")

    if st.session_state.pdf_text:
        st.markdown("### Document overview")
        st.caption(
            f"{st.session_state.pdf_name} · "
            f"{len(st.session_state.pdf_text.split())} words extracted"
        )

        with st.expander("Preview extracted text"):
            st.text(st.session_state.pdf_text[:5000])

        task = st.selectbox(
            "What would you like to create?",
            [
                "Simple revision notes",
                "Detailed summary",
                "Important exam questions",
                "Key definitions",
                "Explain in simple English"
            ]
        )

        if st.button("Generate study material", use_container_width=True):
            prompt = f"""
Use ONLY the source material below to complete this task:
{task}

Keep the notes accurate, clear and well-structured.
Do not invent details absent from the source.
If information is missing, state that clearly.

SOURCE MATERIAL:
{st.session_state.pdf_text}
"""
            with st.spinner("Preparing your study material..."):
                notes = ask_ai(
                    prompt,
                    system_prompt=(
                        "You are a careful academic notes assistant. "
                        "Stay grounded in the provided source material."
                    ),
                    temperature=0.2
                )
                st.session_state.notes_text = notes
                st.session_state.last_summary = notes

        if st.session_state.notes_text:
            st.markdown("### Your study material")
            st.markdown(st.session_state.notes_text)

            st.download_button(
                "Download notes as TXT",
                data=st.session_state.notes_text,
                file_name="study_notes.txt",
                mime="text/plain",
                use_container_width=True
            )

            try:
                pdf_data = export_pdf(
                    "Study Buddy AI — Study Notes",
                    st.session_state.notes_text
                )
                st.download_button(
                    "Download notes as PDF",
                    data=pdf_data,
                    file_name="study_notes.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception:
                st.caption("PDF export unavailable. You can download the TXT file.")

# --------------------------------------------------
# PERFORMANCE
# --------------------------------------------------
elif page == "Performance":
    st.title("Your Performance")
    st.write("Review your quiz results and keep track of your progress.")

    history = st.session_state.quiz_score_history

    if not history:
        st.info(
            "Your progress will appear here after you complete your first AI quiz."
        )
    else:
        total = len(history)
        avg = round(sum(x["score"] for x in history) / total)
        best = max(x["score"] for x in history)

        c1, c2, c3 = st.columns(3)
        c1.metric("Quizzes completed", total)
        c2.metric("Average score", f"{avg}%")
        c3.metric("Best score", f"{best}%")

        st.markdown("### Score history")

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

        history_text = "\n".join(
            f"{x['date']} | {x['topic']} | "
            f"{x['correct']}/{x['total']} | {x['score']}%"
            for x in history
        )

        st.download_button(
            "Export performance report",
            data="Date | Topic | Result | Score\n" + history_text,
            file_name="performance_report.txt",
            mime="text/plain"
        )

# --------------------------------------------------
# SETTINGS
# --------------------------------------------------
elif page == "Settings":
    st.title("Settings")
    st.write("Personalise your Study Buddy AI workspace.")

    st.markdown("### Your profile")
    name = st.text_input(
        "What should we call you?",
        value=st.session_state.user_name
    )

    if st.button("Save profile"):
        st.session_state.user_name = name.strip() or "Student"
        st.success("Profile updated.")

    st.markdown("---")
    st.markdown("### AI connection")

    if get_api_key():
        st.success("Groq API key detected.")
    else:
        st.warning(
            "Groq API key not found. Add GROQ_API_KEY to Streamlit secrets."
        )

    st.markdown("---")
    st.markdown("### Workspace data")

    st.caption(
        "This version keeps session data in Streamlit session state. "
        "Some data may reset when the session restarts."
    )

    if st.button("Clear chat history"):
        st.session_state.chat_history = []
        st.success("Chat history cleared.")

    if st.button("Reset quiz results"):
        st.session_state.quiz_score_history = []
        st.success("Quiz results cleared.")

    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    **Study Buddy AI**

    A student-focused learning workspace for AI-assisted explanations,
    practice quizzes and PDF-based study notes.
    """)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#6C786F;"
    "font-size:12px;padding:10px 0;'>"
    "STUDY BUDDY AI · YOUR LEARNING WORKSPACE"
    "</div>",
    unsafe_allow_html=True
)
