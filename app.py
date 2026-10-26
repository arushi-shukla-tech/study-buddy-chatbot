import streamlit as st
from groq import Groq
from pypdf import PdfReader
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from xml.sax.saxutils import escape

st.set_page_config(
    page_title="Study Buddy AI | Learning OS",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

MODEL = "openai/gpt-oss-20b"

DEFAULTS = {
    "page": "Overview",
    "generated_quizzes": 0,
    "notes_created": 0,
    "chat_messages": [],
    "last_quiz": "",
    "last_notes": "",
    "last_activity": "Your learning workspace is ready.",
    "quiz_history": [],
    "notes_history": [],
    "pdf_text": ""
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --bg: #080d18;
    --surface: #111b2b;
    --line: rgba(174,196,230,.16);
    --text: #edf3ff;
    --muted: #9aa9c2;
    --mint: #7cf5d1;
    --blue: #91adff;
    --purple: #c2a3ff;
}

.stApp {
    background:
        radial-gradient(ellipse at 8% 0%, rgba(70,112,196,.18), transparent 34%),
        radial-gradient(ellipse at 95% 8%, rgba(66,220,182,.11), transparent 30%),
        var(--bg);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}

header[data-testid="stHeader"] {
    background: rgba(8,13,24,.88);
}

.block-container {
    max-width: 1480px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0d1524,#090f1b);
    border-right: 1px solid var(--line);
}

[data-testid="stSidebar"] * {
    color: #dce7fa;
}

h1,h2,h3,h4 {
    color: var(--text) !important;
    font-family: 'Space Grotesk',sans-serif !important;
}

p,label,li {
    color: #d4deef;
}

.brand {
    display:flex;
    align-items:center;
    gap:12px;
    padding:8px 2px 25px;
}

.brand-icon {
    display:flex;
    align-items:center;
    justify-content:center;
    width:47px;
    height:47px;
    border-radius:16px;
    color:#08121c;
    font-size:26px;
    font-weight:900;
    background:linear-gradient(135deg,var(--mint),var(--blue));
    box-shadow:0 0 30px rgba(124,245,209,.2);
}

.brand-name {
    font-family:'Space Grotesk',sans-serif;
    font-size:19px;
    font-weight:700;
    color:#f4f7ff;
}

.brand-name span {
    color:var(--mint);
}

.brand-sub {
    color:#8192ae;
    font-size:9px;
    letter-spacing:1.6px;
    margin-top:3px;
}

.kicker {
    color:var(--mint);
    font-size:10px;
    font-weight:700;
    letter-spacing:2px;
    text-transform:uppercase;
}

.hero {
    padding:35px;
    border:1px solid rgba(124,245,209,.22);
    border-radius:27px;
    background:linear-gradient(120deg,#192d42,#131d31 55%,#202344);
    box-shadow:0 20px 60px rgba(0,0,0,.18);
    margin:10px 0 25px;
}

.hero h1 {
    font-size:clamp(32px,4vw,52px);
    line-height:1.08;
    margin:13px 0;
}

.hero p {
    max-width:700px;
    color:#afbed5;
    font-size:15px;
    line-height:1.8;
}

.hero-chip {
    display:inline-block;
    padding:8px 13px;
    margin-top:8px;
    border-radius:30px;
    border:1px solid rgba(124,245,209,.25);
    background:rgba(124,245,209,.08);
    color:var(--mint);
    font-size:11px;
}

.section-title {
    font-family:'Space Grotesk',sans-serif;
    font-size:25px;
    font-weight:700;
    color:#f1f5ff;
    margin:12px 0 3px;
}

.section-sub {
    color:var(--muted);
    font-size:13px;
    margin-bottom:18px;
}

.panel {
    border:1px solid var(--line);
    border-radius:20px;
    padding:21px;
    background:linear-gradient(145deg,#141f31,#0e1624);
    box-shadow:0 10px 30px rgba(0,0,0,.13);
    margin-bottom:15px;
    min-height:135px;
}

.panel-icon {
    font-size:24px;
    margin-bottom:13px;
}

.panel-title {
    font-family:'Space Grotesk',sans-serif;
    font-weight:700;
    color:#f1f5ff;
    font-size:17px;
}

.panel-note {
    color:#9eacc3;
    font-size:12px;
    line-height:1.7;
    margin-top:7px;
}

.metric {
    border:1px solid var(--line);
    border-radius:19px;
    padding:20px;
    background:linear-gradient(145deg,#121e30,#0f1726);
    min-height:125px;
}

.metric-label {
    color:#8fa0ba;
    font-size:10px;
    letter-spacing:1.3px;
    font-weight:700;
}

.metric-value {
    font-family:'Space Grotesk',sans-serif;
    color:#f4f7ff;
    font-size:34px;
    font-weight:700;
    margin:8px 0 3px;
}

.metric-foot {
    color:#8b9bb4;
    font-size:11px;
}

div.stButton > button,
div.stDownloadButton > button {
    border-radius:12px;
    min-height:44px;
    border:1px solid rgba(141,169,255,.28);
    background:#17243a;
    color:#eaf0ff;
    font-weight:650;
    transition:all .18s ease;
}

div.stButton > button:hover,
div.stDownloadButton > button:hover {
    border-color:var(--mint);
    background:#1a3040;
    color:var(--mint);
}

div.stButton > button[kind="primary"] {
    color:#06131a;
    background:linear-gradient(100deg,#7cf5d1,#91b3ff);
    border:0;
    font-weight:800;
}

div.stButton > button[kind="primary"]:hover {
    filter:brightness(1.08);
    color:#06131a;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background:#0d1726 !important;
    color:#eff5ff !important;
    border:1px solid #293851 !important;
    border-radius:11px !important;
}

div[data-baseweb="select"] > div {
    background:#0d1726 !important;
    border-color:#293851 !important;
    border-radius:11px !important;
}

div[data-baseweb="select"] span {
    color:#eaf0ff !important;
}

[data-testid="stFileUploader"] {
    border:1px dashed #405572;
    border-radius:15px;
    padding:12px;
    background:rgba(14,23,38,.65);
}

[data-testid="stMetric"] {
    background:#111c2c;
    border:1px solid var(--line);
    padding:15px;
    border-radius:14px;
}

[data-testid="stChatMessage"] {
    background:#111c2c;
    border:1px solid var(--line);
    border-radius:15px;
}

.stProgress > div > div > div > div {
    background:linear-gradient(90deg,#7cf5d1,#91b3ff);
}

hr {
    border-color:var(--line);
}

footer,#MainMenu {
    visibility:hidden;
}
</style>
""", unsafe_allow_html=True)


def get_client():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        key = ""

    if not key:
        st.error("GROQ_API_KEY ko Streamlit Secrets mein add karo.")
        return None

    return Groq(api_key=key, timeout=90, max_retries=2)


def ask_ai(prompt, max_tokens=3000, temperature=0.4, system_prompt=None):
    client = get_client()

    if client is None:
        return None

    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    messages.append({
        "role": "user",
        "content": prompt
    })

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )

        return response.choices[0].message.content or ""

    except Exception as e:
        error = str(e).lower()

        if "rate_limit" in error or "rate limit" in error or "429" in error:
            st.error("Groq ki rate limit aa gayi. Thodi der baad dobara try karo.")
        elif "401" in error or "authentication" in error or "api key" in error:
            st.error("Groq API key check karo. Streamlit Secrets mein GROQ_API_KEY sahi hona chahiye.")
        else:
            st.error(f"AI request complete nahi hui: {e}")

        return None


def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "\n\n".join(
        page.extract_text() or ""
        for page in reader.pages
    ).strip()


def make_pdf(content, title="Study Buddy AI Notes"):
    buffer = BytesIO()

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
        "CustomTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=26,
        textColor=colors.HexColor("#255d54"),
        spaceAfter=18
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#255d54"),
        spaceBefore=12,
        spaceAfter=7
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#263849"),
        spaceAfter=5
    )

    story = [Paragraph(escape(title), title_style)]

    for line in content.splitlines():
        line = line.strip()

        if not line:
            story.append(Spacer(1, 5))
        elif line.startswith("#"):
            story.append(
                Paragraph(
                    escape(line.lstrip("#").strip()),
                    heading_style
                )
            )
        elif line.startswith(("- ", "* ", "• ")):
            story.append(
                Paragraph("&#8226; " + escape(line[2:]), body_style)
            )
        else:
            story.append(Paragraph(escape(line), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def heading(title, subtitle):
    st.markdown(
        f'<div class="section-title">{title}</div>'
        f'<div class="section-sub">{subtitle}</div>',
        unsafe_allow_html=True
    )


PAGES = [
    "Overview",
    "AI Quiz Lab",
    "Notes Studio",
    "Study Chat",
    "Insights",
    "Settings"
]

with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-icon">✦</div>
        <div>
            <div class="brand-name">Study Buddy <span>AI</span></div>
            <div class="brand-sub">PERSONAL LEARNING OS</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="kicker">Workspace</div>',
        unsafe_allow_html=True
    )

    current = st.session_state.page

    if current not in PAGES:
        current = "Overview"

    st.session_state.page = st.radio(
        "Navigation",
        PAGES,
        index=PAGES.index(current),
        label_visibility="collapsed",
        format_func=lambda p: {
            "Overview": "⌂  Overview",
            "AI Quiz Lab": "✧  AI Quiz Lab",
            "Notes Studio": "▤  Notes Studio",
            "Study Chat": "◉  Study Chat",
            "Insights": "◫  Insights",
            "Settings": "⚙  Settings"
        }[p]
    )

    st.markdown("---")

    st.markdown("""
    <div class="panel" style="min-height:0;padding:16px">
        <div class="kicker">Your focus</div>
        <div class="panel-title" style="margin-top:8px">Learn smarter.</div>
        <div class="panel-note">
            Turn study material into notes, practice questions and explanations.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption(f"AI model · {MODEL}")

page = st.session_state.page

st.markdown(
    '<div class="kicker">YOUR PERSONAL LEARNING WORKSPACE</div>',
    unsafe_allow_html=True
)

if page == "Overview":
    st.markdown("""
    <div class="hero">
        <div class="kicker">WELCOME TO YOUR AI STUDY SPACE</div>
        <h1>Make every study session<br>count.</h1>
        <p>
            Your personal learning workspace to turn topics into practice,
            PDFs into revision notes, and doubts into clear explanations.
        </p>
        <span class="hero-chip">✦ LLM-powered · Built for focused learning</span>
    </div>
    """, unsafe_allow_html=True)

    a, b, c = st.columns(3)

    for col, label, value, foot in [
        (a, "QUIZ SESSIONS", st.session_state.generated_quizzes, "Practice sets created"),
        (b, "NOTES CREATED", st.session_state.notes_created, "Revision resources prepared"),
        (c, "CHAT MESSAGES", len(st.session_state.chat_messages), "Messages in this session")
    ]:
        with col:
            st.markdown(
                f'<div class="metric"><div class="metric-label">{label}</div>'
                f'<div class="metric-value">{value}</div>'
                f'<div class="metric-foot">{foot}</div></div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    heading(
        "Your toolkit",
        "Everything you need to move from reading to understanding."
    )

    x, y, z = st.columns(3)

    cards = [
        (x, "✧", "AI Quiz Lab", "Create practice questions by topic and difficulty.", "Open Quiz Lab", "AI Quiz Lab"),
        (y, "▤", "Notes Studio", "Transform a PDF into organised revision notes.", "Open Notes Studio", "Notes Studio"),
        (z, "◉", "Study Chat", "Ask questions and get clear explanations.", "Start chatting", "Study Chat")
    ]

    for col, icon, title, description, button, target in cards:
        with col:
            st.markdown(
                f'<div class="panel"><div class="panel-icon">{icon}</div>'
                f'<div class="panel-title">{title}</div>'
                f'<div class="panel-note">{description}</div></div>',
                unsafe_allow_html=True
            )

            if st.button(
                button,
                key="open_" + target,
                use_container_width=True,
                type="primary"
            ):
                st.session_state.page = target
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    heading("Latest activity", "A quick snapshot of your workspace.")

    st.markdown(
        f'<div class="panel" style="min-height:0">'
        f'<div class="panel-title">✦ {escape(st.session_state.last_activity)}</div>'
        f'<div class="panel-note">Activity is stored in this active session.</div></div>',
        unsafe_allow_html=True
    )


elif page == "AI Quiz Lab":
    heading(
        "AI Quiz Lab",
        "Build a practice set for almost any study topic."
    )

    topic = st.text_input(
        "Subject or topic",
        placeholder="e.g. Semiconductor, C programming, linear algebra"
    )

    c1, c2 = st.columns(2)

    with c1:
        level = st.selectbox(
            "Difficulty",
            ["Mixed", "Easy", "Medium", "Hard"]
        )

    with c2:
        question_type = st.selectbox(
            "Question format",
            [
                "Multiple choice questions with answers",
                "Short answer questions with answers",
                "Mixed question types with answers"
            ]
        )

    question_count = st.number_input(
        "Number of questions",
        min_value=1,
        max_value=1000,
        value=50,
        step=10
    )

    st.caption(
        "Custom count up to 1,000. Generation speed and availability depend on API limits."
    )

    if st.button(
        "✦ Generate practice set",
        type="primary",
        use_container_width=True
    ):
        if not topic.strip():
            st.warning("Pehle subject ya topic enter karo.")
        else:
            results = []
            total = int(question_count)
            batch_size = 5
            progress = st.progress(0)
            status = st.empty()
            failed = False

            for start in range(0, total, batch_size):
                current = min(batch_size, total - start)
                first_num = start + 1
                last_num = start + current

                status.write(
                    f"Generating questions {first_num}–{last_num} of {total}..."
                )

                prompt = f"""
Create exactly {current} study questions about: {topic}
Difficulty: {level}
Question format: {question_type}
These are questions {first_num} to {last_num} in a set of {total}.

Requirements:
- Number each question from {first_num} to {last_num}.
- Give an accurate answer and a short explanation for every question.
- For MCQs, include four options labelled A, B, C and D.
- Keep questions distinct and student-friendly.
- Do not add an introduction or conclusion.
"""

                answer = ask_ai(prompt, max_tokens=3000)

                if not answer:
                    failed = True
                    break

                results.append(answer.strip())
                progress.progress(last_num / total)

            status.empty()
            progress.empty()

            if results:
                st.session_state.last_quiz = "\n\n".join(results)
                st.session_state.generated_quizzes += 1

                st.session_state.quiz_history.append({
                    "topic": topic,
                    "count": total,
                    "generated_batches": len(results),
                    "date": datetime.now().strftime("%d %b %Y %H:%M")
                })

                st.session_state.last_activity = f"Created quiz: {topic}"

                if failed:
                    st.warning(
                        "Generation stopped after an API error. "
                        "The completed questions are saved below."
                    )
                else:
                    st.success("Practice set generated.")

            else:
                st.info(
                    "No questions were generated. Wait briefly and try again."
                )

    if st.session_state.last_quiz:
        st.markdown("---")
        heading("Your practice set", "Review or download your questions.")

        st.markdown(st.session_state.last_quiz)

        st.download_button(
            "↓ Download quiz as TXT",
            data=st.session_state.last_quiz,
            file_name="study_buddy_quiz.txt",
            mime="text/plain",
            use_container_width=True
        )


elif page == "Notes Studio":
    heading(
        "Notes Studio",
        "Turn course material into organised, exam-ready revision notes."
    )

    uploaded = st.file_uploader(
        "Upload your study PDF",
        type=["pdf"]
    )

    if uploaded:
        if st.button("Read PDF", type="primary", use_container_width=True):
            try:
                extracted = extract_pdf_text(uploaded)

                if not extracted:
                    st.warning(
                        "PDF se readable text nahi mila. "
                        "Ho sakta hai file scanned ho."
                    )
                else:
                    st.session_state.pdf_text = extracted
                    st.success(
                        f"PDF read successfully · {len(extracted):,} characters."
                    )

            except Exception as e:
                st.error(f"PDF read nahi ho payi: {e}")

    if st.session_state.pdf_text:
        st.markdown(
            f'<div class="panel" style="min-height:0">'
            f'<div class="panel-title">Source loaded</div>'
            f'<div class="panel-note">{len(st.session_state.pdf_text):,} characters ready.</div></div>',
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        with c1:
            notes_style = st.selectbox(
                "Notes format",
                [
                    "Detailed Notes",
                    "Short Notes",
                    "Key Points",
                    "Summary Notes",
                    "Question–Answer Notes"
                ]
            )

        with c2:
            detail = st.selectbox(
                "Detail level",
                ["Balanced", "Concise", "Detailed"]
            )

        if st.button(
            "✦ Generate revision notes",
            type="primary",
            use_container_width=True
        ):
            prompt = f"""
Prepare student-friendly notes using only the source material.
Format: {notes_style}
Detail level: {detail}

Instructions:
- Use clear headings and subheadings.
- Prefer numbered points and bullet lists.
- Explain difficult terms in simple English.
- Preserve important definitions, formulas and examples.
- Do not invent information missing from the source.
- Organise material for revision and exams.

Source material:
{st.session_state.pdf_text[:26000]}
"""

            with st.spinner("The AI is organising your notes..."):
                notes = ask_ai(
                    prompt,
                    max_tokens=6000,
                    temperature=0.3
                )

            if notes:
                st.session_state.last_notes = notes
                st.session_state.notes_created += 1

                st.session_state.notes_history.append({
                    "format": notes_style,
                    "date": datetime.now().strftime("%d %b %Y %H:%M")
                })

                st.session_state.last_activity = f"Created {notes_style}"
                st.success("Your revision notes are ready.")

    if st.session_state.last_notes:
        st.markdown("---")
        heading("Your revision notes", "Read or download your generated material.")

        st.markdown(st.session_state.last_notes)

        d1, d2 = st.columns(2)

        with d1:
            st.download_button(
                "↓ Download TXT",
                data=st.session_state.last_notes,
                file_name="study_buddy_notes.txt",
                mime="text/plain",
                use_container_width=True
            )

        with d2:
            try:
                pdf_data = make_pdf(
                    st.session_state.last_notes,
                    "Study Buddy AI - Revision Notes"
                )

                st.download_button(
                    "↓ Download PDF",
                    data=pdf_data,
                    file_name="Study_Buddy_Revision_Notes.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            except Exception as e:
                st.warning(f"PDF export issue: {e}")


elif page == "Study Chat":
    heading(
        "Study Chat",
        "Your AI study partner for concepts, formulas and explanations."
    )

    st.markdown(
        '<div class="panel" style="min-height:0">'
        '<div class="panel-title">Ask freely. Learn step by step.</div>'
        '<div class="panel-note">Include your subject and topic for a more useful answer.</div></div>',
        unsafe_allow_html=True
    )

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a study question...")

    if question:
        st.session_state.chat_messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking through your question..."):
                history = st.session_state.chat_messages[-10:]

                reply = ask_ai(
                    "\n".join(
                        f"{m['role'].upper()}: {m['content']}"
                        for m in history
                    ),
                    max_tokens=2200,
                    temperature=0.4,
                    system_prompt=(
                        "You are a patient, accurate study tutor. "
                        "Explain concepts in simple student-friendly language. "
                        "Use steps, examples, formulas and headings when helpful. "
                        "If unsure, say so."
                    )
                )

            if reply:
                st.markdown(reply)

                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": reply
                })

                st.session_state.last_activity = "Used Study Chat"
                st.rerun()

    if st.session_state.chat_messages:
        if st.button("Clear conversation"):
            st.session_state.chat_messages = []
            st.rerun()


elif page == "Insights":
    heading(
        "Learning insights",
        "Track your activity during this session."
    )

    a, b, c = st.columns(3)

    a.metric("Quiz sessions", st.session_state.generated_quizzes)
    b.metric("Notes created", st.session_state.notes_created)
    c.metric("Chat messages", len(st.session_state.chat_messages))

    st.markdown("---")
    heading("Quiz history", "Your recent practice sessions.")

    if st.session_state.quiz_history:
        for item in reversed(st.session_state.quiz_history):
            st.markdown(
                f'<div class="panel" style="min-height:0">'
                f'<div class="panel-title">{escape(item["topic"])}</div>'
                f'<div class="panel-note">{item["count"]} requested questions · {item["date"]}</div></div>',
                unsafe_allow_html=True
            )
    else:
        st.info("Your quiz sessions will appear here.")

    heading("Notes history", "Revision material you have created.")

    if st.session_state.notes_history:
        for item in reversed(st.session_state.notes_history):
            st.markdown(
                f'<div class="panel" style="min-height:0">'
                f'<div class="panel-title">{escape(item["format"])}</div>'
                f'<div class="panel-note">{item["date"]}</div></div>',
                unsafe_allow_html=True
            )
    else:
        st.info("Your notes history will appear here.")

    st.caption(
        "Activity is kept in the active Streamlit session and may reset when the session restarts."
    )


elif page == "Settings":
    heading(
        "Workspace settings",
        "AI configuration and session controls."
    )

    st.markdown(
        f'<div class="panel"><div class="kicker">AI ENGINE</div>'
        f'<div class="panel-title" style="margin-top:8px">{MODEL}</div>'
        f'<div class="panel-note">Provider: Groq API · Model runs on cloud servers.</div></div>',
        unsafe_allow_html=True
    )

    st.markdown("### Session data")

    if st.button("Clear quiz and notes history", use_container_width=True):
        st.session_state.quiz_history = []
        st.session_state.notes_history = []
        st.session_state.last_quiz = ""
        st.session_state.last_notes = ""
        st.session_state.generated_quizzes = 0
        st.session_state.notes_created = 0
        st.success("Quiz and notes history cleared.")
        st.rerun()

    if st.button("Clear all chat messages", use_container_width=True):
        st.session_state.chat_messages = []
        st.success("Chat cleared.")
        st.rerun()

   
