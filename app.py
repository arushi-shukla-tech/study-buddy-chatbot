import streamlit as st
from groq import Groq
from pypdf import PdfReader
from io import BytesIO
from datetime import datetime
from html import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

MODEL = "openai/gpt-oss-20b"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --green:#126B50;
    --deep:#103D30;
    --cream:#F7F6F0;
    --mint:#DDF1E6;
    --ink:#192D26;
    --muted:#718078;
    --line:#E4E8DF;
}

html, body, [class*="css"] {
    font-family:'DM Sans',sans-serif;
}

.stApp {
    background:var(--cream);
    color:var(--ink);
}

#MainMenu, footer {
    visibility:hidden;
}

header[data-testid="stHeader"] {
    background:transparent;
}

.block-container {
    max-width:1300px;
    padding:1.4rem 1.8rem 3rem;
}

h1,h2,h3 {
    font-family:'Manrope',sans-serif !important;
    color:var(--ink);
    letter-spacing:-1px;
}

p {
    line-height:1.75;
}

section[data-testid="stSidebar"] {
    background:linear-gradient(160deg,#103D30,#092B24);
    border-right:1px solid #315447;
}

section[data-testid="stSidebar"] * {
    color:#F0F7F1;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding:8px 6px;
    border-radius:10px;
    font-size:14px;
}

section[data-testid="stSidebar"] hr {
    border-color:#345548;
}

.sb-logo {
    display:flex;
    align-items:center;
    justify-content:center;
    width:54px;
    height:54px;
    border-radius:18px;
    background:linear-gradient(135deg,#53C69A,#138363);
    font:800 25px 'Manrope',sans-serif;
    color:white;
    margin-bottom:14px;
}

.sb-brand {
    padding:12px 4px 20px;
}

.sb-brand-name {
    font:800 23px 'Manrope',sans-serif;
    color:white;
}

.sb-caption {
    color:#B8D7C7;
    font-size:10px;
    letter-spacing:2px;
    margin-top:6px;
}

.sb-note {
    background:#FFFFFF0D;
    border:1px solid #FFFFFF1C;
    border-radius:16px;
    padding:16px;
    font-size:12px;
    line-height:1.8;
    margin-top:22px;
}

.sb-topbar {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    padding:4px 0 18px;
    margin-bottom:24px;
    border-bottom:1px solid var(--line);
}

.sb-top-title {
    font:800 19px 'Manrope',sans-serif;
}

.sb-top-caption {
    font-size:12px;
    color:var(--muted);
    margin-top:4px;
}

.sb-pill {
    background:var(--mint);
    color:var(--green);
    border:1px solid #C9E5D4;
    padding:8px 12px;
    border-radius:30px;
    font-size:10px;
    font-weight:800;
}

.sb-hero {
    position:relative;
    overflow:hidden;
    background:linear-gradient(125deg,#103D30,#126B50 65%,#178563);
    border-radius:25px;
    padding:36px;
    min-height:300px;
    color:white;
    box-shadow:0 18px 40px #103D3018;
}

.sb-hero:after {
    content:"";
    position:absolute;
    width:250px;
    height:250px;
    border:1px solid #FFFFFF30;
    border-radius:50%;
    right:-70px;
    top:-120px;
    box-shadow:0 0 0 30px #FFFFFF08,0 0 0 65px #FFFFFF06;
}

.sb-kicker {
    position:relative;
    z-index:1;
    color:#C8F0D9;
    font-size:10px;
    font-weight:800;
    letter-spacing:2px;
}

.sb-hero h1 {
    position:relative;
    z-index:1;
    color:white !important;
    font-size:clamp(33px,4vw,52px);
    line-height:1.15;
    letter-spacing:-2px;
    margin:25px 0 15px;
}

.sb-hero h1 span {
    color:#D5F3A8;
}

.sb-hero-copy {
    position:relative;
    z-index:1;
    max-width:580px;
    color:#E1F1E8;
    font-size:13px;
    line-height:1.9;
}

.sb-section {
    margin:30px 0 15px;
}

.sb-eyebrow {
    color:var(--green);
    font-size:10px;
    font-weight:800;
    letter-spacing:1.7px;
}

.sb-section-title {
    font:800 25px 'Manrope',sans-serif;
    letter-spacing:-1px;
    margin-top:6px;
}

.sb-muted {
    color:var(--muted);
    font-size:12px;
    line-height:1.8;
    margin-top:5px;
}

.sb-stat,.sb-feature,.sb-panel {
    background:white;
    border:1px solid var(--line);
    border-radius:18px;
    padding:20px;
    margin-bottom:12px;
    box-shadow:0 5px 20px #193D2906;
}

.sb-stat {
    min-height:135px;
}

.sb-stat-icon,.sb-feature-icon {
    display:flex;
    align-items:center;
    justify-content:center;
    background:var(--mint);
    color:var(--green);
    width:42px;
    height:42px;
    border-radius:14px;
    font-size:20px;
}

.sb-stat-number {
    font:800 31px 'Manrope',sans-serif;
    color:var(--ink);
    margin-top:12px;
}

.sb-stat-label {
    font-size:11px;
    font-weight:700;
    letter-spacing:.6px;
    color:var(--green);
}

.sb-feature {
    min-height:175px;
}

.sb-feature-title {
    font:800 17px 'Manrope',sans-serif;
    margin-top:13px;
}

.sb-feature-copy {
    color:var(--muted);
    font-size:12px;
    line-height:1.8;
    margin-top:6px;
}

.sb-panel-label {
    color:var(--green);
    font-size:10px;
    font-weight:800;
    letter-spacing:1.5px;
}

.sb-panel-title {
    font:800 20px 'Manrope',sans-serif;
    margin-top:8px;
}

.sb-footer {
    border-top:1px solid var(--line);
    margin-top:28px;
    padding-top:16px;
    color:var(--muted);
    font-size:10px;
    letter-spacing:.5px;
}

div.stButton > button,
div.stDownloadButton > button {
    min-height:44px;
    border-radius:12px;
    font-weight:700;
    border:1px solid var(--line);
}

div.stButton > button[kind="primary"] {
    background:var(--green);
    border-color:var(--green);
    color:white;
}

div.stButton > button[kind="primary"]:hover {
    background:var(--deep);
    color:white;
}

div.stButton > button:not([kind="primary"]) {
    background:white;
    color:var(--ink);
}

div.stButton > button:not([kind="primary"]):hover {
    border-color:var(--green);
    color:var(--green);
}

.stTextInput input,.stTextArea textarea {
    border-radius:11px !important;
}

[data-testid="stFileUploader"] {
    background:white;
    border:1px dashed #9ACBB0;
    border-radius:15px;
    padding:12px;
}

[data-testid="stMetric"] {
    background:white;
    border:1px solid var(--line);
    border-radius:15px;
    padding:15px;
}

[data-testid="stMetricValue"] {
    color:var(--green);
    font-family:'Manrope',sans-serif;
}

[data-testid="stChatMessage"] {
    background:white;
    border:1px solid var(--line);
    border-radius:15px;
}

@media(max-width:700px) {
    .block-container {
        padding:.8rem .85rem 2rem;
    }

    .sb-hero {
        padding:24px 20px;
        min-height:260px;
        border-radius:20px;
    }

    .sb-hero h1 {
        font-size:35px;
        letter-spacing:-1.5px;
    }

    .sb-hero-copy {
        font-size:12px;
    }

    .sb-top-title {
        font-size:16px;
    }

    .sb-pill {
        font-size:8px;
        padding:7px 9px;
    }

    .sb-section-title {
        font-size:22px;
    }

    .sb-stat,.sb-feature,.sb-panel {
        padding:15px;
    }
}
</style>
""", unsafe_allow_html=True)

defaults = {
    "page": "Dashboard",
    "chat": [],
    "quiz_history": [],
    "notes_history": [],
    "last_quiz": "",
    "last_notes": "",
    "quiz_topic": "",
    "pdf_text": "",
    "notes_title": "",
    "activity": "Your learning journey starts here"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

PAGES = [
    "Dashboard", "AI Quiz", "PDF Notes",
    "Study Chat", "Performance", "Settings"
]

def get_client():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        key = ""

    return Groq(api_key=key) if key else None

def ask_ai(prompt="", max_tokens=3000, messages=None):
    client = get_client()

    if client is None:
        st.error(
            "GROQ_API_KEY missing. Add it in Streamlit Cloud "
            "App settings > Secrets."
        )
        return None

    if messages is None:
        messages = [{"role": "user", "content": prompt}]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.35,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception:
        st.error(
            "AI request failed. Check your Groq API key and model access."
        )
        return None

def page_header(number, title, description):
    st.markdown(f"""
    <div class="sb-section" style="margin-top:0">
        <div class="sb-eyebrow">STUDY BUDDY AI / {escape(number)}</div>
        <div class="sb-section-title" style="font-size:clamp(28px,4vw,40px)">
            {escape(title)}
        </div>
        <div class="sb-muted">{escape(description)}</div>
    </div>
    """, unsafe_allow_html=True)

def section(label, title, description=""):
    st.markdown(f"""
    <div class="sb-section">
        <div class="sb-eyebrow">{escape(label)}</div>
        <div class="sb-section-title">{escape(title)}</div>
        <div class="sb-muted">{escape(description)}</div>
    </div>
    """, unsafe_allow_html=True)

def panel(label, title, description):
    st.markdown(f"""
    <div class="sb-panel">
        <div class="sb-panel-label">{escape(label)}</div>
        <div class="sb-panel-title">{escape(title)}</div>
        <div class="sb-muted">{escape(description)}</div>
    </div>
    """, unsafe_allow_html=True)

def make_pdf(content, title="Study Buddy AI Notes"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=45, leftMargin=45,
        topMargin=45, bottomMargin=45
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "StudyTitle", parent=styles["Title"],
        textColor=colors.HexColor("#126B50"),
        fontSize=22, leading=28, spaceAfter=18
    )
    body_style = ParagraphStyle(
        "StudyBody", parent=styles["BodyText"],
        fontSize=10, leading=16,
        textColor=colors.HexColor("#24392E"),
        spaceAfter=8
    )

    story = [
        Paragraph(escape(title), title_style),
        Paragraph("Created with Study Buddy AI", styles["Normal"]),
        Spacer(1, 18)
    ]

    for line in content.splitlines():
        line = line.strip()
        if not line:
            story.append(Spacer(1, 5))
        elif line.startswith("#"):
            story.append(Paragraph(
                escape(line.lstrip("#").strip()),
                styles["Heading2"]
            ))
        elif line.startswith(("- ", "* ", "• ")):
            story.append(Paragraph(
                "&#8226; " + escape(line[2:].strip()),
                body_style
            ))
        else:
            story.append(Paragraph(escape(line), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
        <div class="sb-logo">S.</div>
        <div class="sb-brand-name">Study Buddy AI</div>
        <div class="sb-caption">YOUR LEARNING SPACE</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.caption("WORKSPACE MENU")

    st.session_state.page = st.radio(
        "Navigate",
        PAGES,
        index=PAGES.index(st.session_state.page),
        label_visibility="collapsed",
        key="navigation"
    )

    st.divider()
    st.markdown("""
    <div class="sb-note">
        <strong>YOUR AI STUDY PARTNER</strong><br><br>
        Create quizzes, organise study notes and understand
        difficult concepts one step at a time.
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.caption("POWERED BY GROQ AI")

st.markdown("""
<div class="sb-topbar">
    <div>
        <div class="sb-top-title">Study Buddy AI</div>
        <div class="sb-top-caption">Your personal learning workspace</div>
    </div>
    <div class="sb-pill">AI WORKSPACE</div>
</div>
""", unsafe_allow_html=True)

def dashboard():
    st.markdown("""
    <div class="sb-hero">
        <div class="sb-kicker">YOUR PERSONAL AI STUDY SPACE</div>
        <h1>Study smarter.<br><span>Achieve more.</span></h1>
        <div class="sb-hero-copy">
            Your personal workspace for practice quizzes, clear study notes
            and personalised doubt solving. Make every study session count.
        </div>
    </div>
    """, unsafe_allow_html=True)

    quizzes = len(st.session_state.quiz_history)
    notes = len(st.session_state.notes_history)
    chats = sum(1 for m in st.session_state.chat if m["role"] == "user")

    section("YOUR WORKSPACE / 01", "Study overview",
            "A snapshot of your activity in this session.")

    for col, item in zip(st.columns(3), [
        ("✳", quizzes, "QUIZ SETS"),
        ("▤", notes, "NOTES CREATED"),
        ("◉", chats, "QUESTIONS ASKED")
    ]):
        icon, number, label = item
        with col:
            st.markdown(f"""
            <div class="sb-stat">
                <div class="sb-stat-icon">{icon}</div>
                <div class="sb-stat-number">{number}</div>
                <div class="sb-stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    section("YOUR TOOLKIT / 02", "Everything you need to learn",
            "Choose a workspace and get started.")

    features = [
        ("✳", "AI Quiz Lab",
         "Generate topic-based questions with answers and explanations.",
         "AI Quiz"),
        ("▤", "Notes Studio",
         "Transform readable PDFs into organised revision notes.",
         "PDF Notes"),
        ("◉", "Personal AI Tutor",
         "Ask doubts and get step-by-step explanations.",
         "Study Chat"),
        ("↗", "Progress Centre",
         "Review your quizzes, notes and recent activity.",
         "Performance")
    ]

    for i in range(0, 4, 2):
        left, right = st.columns(2)
        for col, feature in zip([left, right], features[i:i+2]):
            icon, title, description, page = feature
            with col:
                st.markdown(f"""
                <div class="sb-feature">
                    <div class="sb-feature-icon">{icon}</div>
                    <div class="sb-feature-title">{title}</div>
                    <div class="sb-feature-copy">{description}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(
                    f"Open {title} →",
                    key=f"open_{page}",
                    type="primary",
                    width="stretch"
                ):
                    st.session_state.page = page
                    st.rerun()

    section("RECENT ACTIVITY / 03", "Your learning trail")
    panel("LATEST UPDATE", "Keep moving forward",
          st.session_state.activity)

def ai_quiz():
    page_header("01 / PRACTISE", "AI Quiz Lab",
                "Create a personalised practice set.")

    panel("QUIZ BUILDER", "Configure your practice",
          "Choose the topic, difficulty and question style.")

    topic = st.text_input("Subject or topic",
                          placeholder="e.g. BJT, recursion, chemistry")
    difficulty = st.selectbox("Difficulty",
                              ["Easy", "Medium", "Hard", "Mixed"])
    qtype = st.selectbox("Question type",
                         ["MCQ", "Short Answer", "Mixed"])
    language = st.selectbox("Language",
                            ["Simple English", "Hindi", "Hinglish"])
    count = st.select_slider("Number of questions",
                             options=[5, 10, 15, 20, 30, 40, 50],
                             value=10)

    if st.button("Generate my quiz", type="primary",
                 width="stretch"):
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            output = []
            failed = False
            with st.spinner("Creating your quiz..."):
                for start in range(1, count + 1, 10):
                    batch = min(10, count - start + 1)
                    prompt = f"""
Create exactly {batch} educational questions about {topic}.
Difficulty: {difficulty}
Format: {qtype}
Language: {language}
Number questions starting from {start}.
For MCQs provide four options, correct answer and explanation.
For short answers provide a model answer.
For mixed format use both. Use accurate facts and clear headings.
"""
                    result = ask_ai(prompt, 4000)
                    if not result:
                        failed = True
                        break
                    output.append(result)

            if output:
                content = "\n\n".join(output)
                st.session_state.last_quiz = content
                st.session_state.quiz_topic = topic
                st.session_state.quiz_history.append({
                    "topic": topic,
                    "count": count,
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "content": content
                })
                st.session_state.activity = f"Generated quiz: {topic}"
                if failed:
                    st.warning("Only part of the quiz was generated.")
                else:
                    st.success("Your quiz is ready!")

    if st.session_state.last_quiz:
        section("YOUR PRACTICE SET", st.session_state.quiz_topic)
        st.markdown(st.session_state.last_quiz)
        st.download_button(
            "Download quiz as TXT",
            st.session_state.last_quiz,
            file_name="study_buddy_quiz.txt",
            mime="text/plain",
            width="stretch"
        )

def pdf_notes():
    page_header("02 / ORGANISE", "Notes Studio",
                "Turn readable PDFs into structured revision notes.")

    panel("DOCUMENT WORKSPACE", "Your study material",
          "Upload a PDF, choose a format and generate notes.")

    uploaded = st.file_uploader("Upload study PDF",
                                type=["pdf"])
    if uploaded:
        try:
            reader = PdfReader(uploaded)
            extracted = "\n".join(
                page.extract_text() or "" for page in reader.pages
            ).strip()
            if extracted:
                st.session_state.pdf_text = extracted
                st.session_state.notes_title = uploaded.name
                st.success(f"PDF ready: {len(reader.pages)} pages")
            else:
                st.warning("No selectable text found. Scanned PDFs may need OCR.")
        except Exception:
            st.error("Could not read this PDF.")

    style = st.selectbox("Notes format", [
        "Detailed notes with headings",
        "Exam revision notes",
        "Short summary",
        "Question and answer format",
        "Bullet-point notes"
    ])
    language = st.selectbox("Output language",
                            ["Simple English", "Hindi", "Hinglish"])

    if st.button("Generate study notes", type="primary",
                 width="stretch"):
        if not st.session_state.pdf_text:
            st.warning("Upload a readable PDF first.")
        else:
            prompt = f"""
Create study notes using only the source text below.
Format: {style}
Language: {language}
Use headings, bullet points, definitions, formulas and examples.
Explain difficult ideas simply. Do not invent facts.

SOURCE TEXT:
{st.session_state.pdf_text[:26000]}
"""
            with st.spinner("Creating your notes..."):
                notes = ask_ai(prompt, 6000)

            if notes:
                st.session_state.last_notes = notes
                st.session_state.notes_history.append({
                    "title": st.session_state.notes_title or "Study Notes",
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "content": notes
                })
                st.session_state.activity = "Created PDF study notes"
                st.success("Your notes are ready!")

    if st.session_state.last_notes:
        section("YOUR STUDY RESOURCE", "Ready for revision")
        st.markdown(st.session_state.last_notes)

        left, right = st.columns(2)
        with left:
            st.download_button(
                "Download TXT",
                st.session_state.last_notes,
                file_name="study_buddy_notes.txt",
                mime="text/plain",
                width="stretch"
            )
        with right:
            try:
                pdf = make_pdf(st.session_state.last_notes)
                st.download_button(
                    "Download PDF", pdf,
                    file_name="study_buddy_notes.pdf",
                    mime="application/pdf",
                    width="stretch"
                )
            except Exception:
                st.error("PDF export failed. Download TXT instead.")

def study_chat():
    page_header("03 / UNDERSTAND", "Personal AI Tutor",
                "Ask questions and get clear explanations.")

    panel("CONVERSATION SPACE", "What would you like to understand?",
          "Ask one question at a time for focused help.")

    for message in st.session_state.chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask your study question...")
    if prompt:
        st.session_state.chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        messages = [{
            "role": "system",
            "content": (
                "You are Study Buddy AI, a patient and accurate tutor. "
                "Explain in simple language, show steps when useful, "
                "and do not invent facts."
            )
        }]
        messages.extend(st.session_state.chat[-12:])

        with st.chat_message("assistant"):
            with st.spinner("Preparing explanation..."):
                answer = ask_ai(messages=messages, max_tokens=3000)
            if answer:
                st.markdown(answer)
                st.session_state.chat.append({
                    "role": "assistant", "content": answer
                })
                st.session_state.activity = "Asked a question in Study Chat"

    if st.session_state.chat and st.button("Clear conversation"):
        st.session_state.chat = []
        st.rerun()

def performance():
    page_header("04 / REFLECT", "Progress Centre",
                "Review your activity in this session.")

    quizzes = len(st.session_state.quiz_history)
    notes = len(st.session_state.notes_history)
    chats = sum(1 for m in st.session_state.chat if m["role"] == "user")

    a, b, c = st.columns(3)
    a.metric("Quiz sets", quizzes)
    b.metric("Notes created", notes)
    c.metric("Questions asked", chats)

    section("ACTIVITY", "Latest work")
    panel("RECENT UPDATE", "Learning activity",
          st.session_state.activity)

    section("PRACTICE", "Quiz history")
    if st.session_state.quiz_history:
        for i, item in enumerate(reversed(st.session_state.quiz_history)):
            with st.expander(
                f"{item['topic']} · {item['count']} questions · {item['date']}"
            ):
                st.markdown(item["content"])
                st.download_button(
                    "Download quiz", item["content"],
                    file_name="study_buddy_quiz.txt",
                    key=f"quiz_history_{i}"
                )
    else:
        st.info("Your generated quizzes will appear here.")

    section("RESOURCES", "Notes history")
    if st.session_state.notes_history:
        for i, item in enumerate(reversed(st.session_state.notes_history)):
            with st.expander(f"{item['title']} · {item['date']}"):
                st.markdown(item["content"])
                st.download_button(
                    "Download notes", item["content"],
                    file_name="study_buddy_notes.txt",
                    key=f"notes_history_{i}"
                )
    else:
        st.info("Your generated notes will appear here.")

def settings():
    page_header("05 / SETTINGS", "Workspace settings",
                "Manage the app and current session.")

    panel("PRODUCT", "Study Buddy AI",
          "Your learning workspace for quizzes, notes and chat.")
    panel("AI ENGINE", MODEL,
          "Groq API key is configured privately using Streamlit Secrets.")
    panel("SESSION HISTORY", "Temporary session data",
          "History is held in the active session, not a permanent database.")

    st.subheader("Clear current history")
    confirm = st.checkbox(
        "I understand that clearing data removes my current session history."
    )

    if st.button("Clear session history", type="primary"):
        if not confirm:
            st.warning("Confirm the checkbox before clearing.")
        else:
            for key, value in {
                "chat": [],
                "quiz_history": [],
                "notes_history": [],
                "last_quiz": "",
                "last_notes": "",
                "quiz_topic": "",
                "pdf_text": "",
                "notes_title": "",
                "activity": "Your learning journey starts here"
            }.items():
                st.session_state[key] = value
            st.success("Session history cleared.")
            st.rerun()

if st.session_state.page == "Dashboard":
    dashboard()
elif st.session_state.page == "AI Quiz":
    ai_quiz()
elif st.session_state.page == "PDF Notes":
    pdf_notes()
elif st.session_state.page == "Study Chat":
    study_chat()
elif st.session_state.page == "Performance":
    performance()
elif st.session_state.page == "Settings":
    settings()

st.markdown("""
<div class="sb-footer">
    STUDY BUDDY AI · PERSONAL LEARNING WORKSPACE
    <br><br>
    LEARN WITH PURPOSE · GROW WITH CONFIDENCE
</div>
""", unsafe_allow_html=True)
