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
import re

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="📗",
    layout="wide",
    initial_sidebar_state="expanded"
)

MODEL = "openai/gpt-oss-20b"

defaults = {
    "page": "Dashboard",
    "generated_quizzes": 0,
    "notes_created": 0,
    "chat_messages": [],
    "last_quiz": "",
    "last_notes": "",
    "last_activity": "Ready to study",
    "quiz_history": [],
    "notes_history": [],
    "pdf_text": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

.stApp {
    background:
    radial-gradient(ellipse at 5% 0%, #e7f2e4 0%, transparent 32%),
    radial-gradient(ellipse at 95% 5%, #edf6e9 0%, transparent 30%),
    #fbfdf9;
    color: #293c2e;
    font-family: 'DM Sans', sans-serif;
}

header[data-testid="stHeader"] {
    background: rgba(251,253,249,.94);
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

[data-testid="stSidebar"] {
    background: #f0f6ee;
    border-right: 1px solid #dce9d9;
}

h1, h2, h3 {
    color: #2d4533;
    font-family: 'Manrope', sans-serif;
}

p, label {
    color: #485d4b;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 5px 0 20px;
}

.brand-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 46px;
    height: 46px;
    border-radius: 15px;
    color: white;
    font-size: 23px;
    background: linear-gradient(135deg,#a9cfa9,#76a77d);
}

.brand-name {
    color: #2d4533;
    font-size: 19px;
    font-weight: 800;
}

.brand-name span {
    color: #6f9b73;
}

.brand-sub {
    color: #819582;
    font-size: 10px;
}

.hero {
    padding: 30px;
    border-radius: 23px;
    border: 1px solid #dce9d8;
    background: linear-gradient(120deg,#e8f3e5,#f8fbf5 60%,#e4f0e1);
    margin-bottom: 24px;
}

.hero h1 {
    font-size: clamp(27px,3.2vw,39px);
    margin: 8px 0;
}

.hero p {
    color: #5c725e;
    max-width: 620px;
}

.eyebrow {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #628b68;
    font-weight: 800;
}

.hero-pill, .tag {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 30px;
    background: #e1efde;
    border: 1px solid #cfe3ca;
    color: #557c5a;
    font-size: 12px;
}

.panel {
    background: linear-gradient(145deg,#ffffff,#f7faf5);
    border: 1px solid #e1eadf;
    border-radius: 17px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 5px 18px rgba(57,91,61,.035);
}

.panel-title {
    color: #304a35;
    font-size: 16px;
    font-weight: 700;
}

.panel-note, .section-sub {
    color: #778a78;
    font-size: 12px;
    margin-top: 5px;
}

.metric {
    padding: 20px;
    min-height: 120px;
    border-radius: 17px;
    border: 1px solid #dfebdc;
    background: linear-gradient(145deg,#fff,#f2f8ef);
    margin-bottom: 12px;
}

.metric-label {
    color: #718673;
    font-size: 12px;
    font-weight: 600;
}

.metric-value {
    color: #345b3b;
    font-size: 30px;
    font-weight: 800;
    margin: 7px 0;
}

.metric-foot, .small-muted {
    color: #849684;
    font-size: 11px;
}

.section-heading {
    color: #304a35;
    font-size: 23px;
    font-weight: 800;
    margin: 10px 0 4px;
}

div.stButton > button {
    border-radius: 11px;
    border: 1px solid #d3e4d0;
    background: #ffffff;
    color: #36583b;
    font-weight: 600;
    min-height: 42px;
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(110deg,#86b58a,#6e9e74);
    border: 1px solid #7eac82;
    color: white;
}

div.stButton > button:hover {
    border-color: #8bb58b;
    background: #edf5ea;
    color: #2d4c32;
}

div.stButton > button[kind="primary"]:hover {
    background: #628f69;
    color: white;
}

.stTextInput input, .stTextArea textarea,
.stNumberInput input {
    background: white;
    color: #304735;
    border: 1px solid #d7e5d4;
    border-radius: 10px;
}

[data-testid="stFileUploader"] {
    background: #f7fbf5;
    border: 1px dashed #b9d3b7;
    border-radius: 14px;
    padding: 10px;
}

[data-testid="stMetric"] {
    background: #f6faf3;
    border: 1px solid #e0ebdd;
    padding: 15px;
    border-radius: 13px;
}

[data-testid="stChatMessage"] {
    background: #f4f8f1;
    border: 1px solid #e3ecdf;
    border-radius: 14px;
}

hr {
    border-color: #e0eade;
}

footer {
    visibility: hidden;
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

    return Groq(api_key=key)


def ask_ai(prompt, max_tokens=5000, temperature=0.4):
    client = get_client()
    if client is None:
        return None

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"AI request failed: {e}")
        return None


def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    pages = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return "\n\n".join(pages).strip()


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
        textColor=colors.HexColor("#477750"),
        spaceAfter=18
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#477750"),
        spaceBefore=12,
        spaceAfter=7
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#334638"),
        spaceAfter=5
    )

    story = [Paragraph(escape(title), title_style)]

    for line in content.splitlines():
        line = line.strip()

        if not line:
            story.append(Spacer(1, 5))
        elif line.startswith("#"):
            heading = line.lstrip("#").strip()
            story.append(Paragraph(escape(heading), heading_style))
        elif line.startswith(("- ", "* ", "• ")):
            story.append(
                Paragraph("&#8226; " + escape(line[2:]), body_style)
            )
        else:
            story.append(Paragraph(escape(line), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def show_heading(title, subtitle):
    st.markdown(
        f'<div class="section-heading">{title}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="section-sub">{subtitle}</div>',
        unsafe_allow_html=True
    )


def go_to(page):
    st.session_state.page = page
    st.rerun()


with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-icon">✦</div>
        <div>
            <div class="brand-name">Study Buddy <span>AI</span></div>
            <div class="brand-sub">YOUR PERSONAL STUDY SPACE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="small-muted">WORKSPACE</div>',
                unsafe_allow_html=True)

    pages = [
        "Dashboard",
        "AI Quiz",
        "PDF Notes",
        "Study Chat",
        "Performance",
        "Settings"
    ]

    selected = st.radio(
        "Navigation",
        pages,
        index=pages.index(st.session_state.page),
        label_visibility="collapsed"
    )

    st.session_state.page = selected

    st.markdown("---")
    st.markdown("""
    <div class="panel">
        <div class="panel-title">Your study space</div>
        <div class="panel-note">
            Organise notes, practise questions and learn at your own pace.
        </div>
    </div>
    """, unsafe_allow_html=True)


top_left, top_right = st.columns([8, 1])

with top_left:
    st.markdown(
        '<div class="small-muted">YOUR PERSONAL LEARNING WORKSPACE</div>',
        unsafe_allow_html=True
    )

with top_right:
    with st.popover("⋮"):
        st.markdown("**Quick menu**")
        for name in pages:
            if st.button(name, key="menu_" + name, use_container_width=True):
                go_to(name)


page = st.session_state.page


if page == "Dashboard":
    st.markdown("""
    <div class="hero">
        <div class="eyebrow">WELCOME TO YOUR STUDY SPACE</div>
        <h1>Make learning feel simpler.</h1>
        <p>
            Turn your notes into useful revision material, practise with AI
            quizzes and clear your doubts in one organised workspace.
        </p>
        <span class="hero-pill">Your learning, your pace</span>
    </div>
    """, unsafe_allow_html=True)

    a, b, c = st.columns(3)

    with a:
        st.markdown(f"""
        <div class="metric">
            <div class="metric-label">QUIZZES CREATED</div>
            <div class="metric-value">{st.session_state.generated_quizzes}</div>
            <div class="metric-foot">Practice sessions started</div>
        </div>
        """, unsafe_allow_html=True)

    with b:
        st.markdown(f"""
        <div class="metric">
            <div class="metric-label">NOTES CREATED</div>
            <div class="metric-value">{st.session_state.notes_created}</div>
            <div class="metric-foot">Revision resources prepared</div>
        </div>
        """, unsafe_allow_html=True)

    with c:
        st.markdown(f"""
        <div class="metric">
            <div class="metric-label">CHAT MESSAGES</div>
            <div class="metric-value">{len(st.session_state.chat_messages)}</div>
            <div class="metric-foot">Study questions asked</div>
        </div>
        """, unsafe_allow_html=True)

    show_heading("Your workspace", "Choose what you want to work on today.")

    x, y, z = st.columns(3)

    with x:
        st.markdown("""
        <div class="panel">
            <div class="panel-title">AI Quiz</div>
            <div class="panel-note">
                Create practice questions from any subject or topic.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Create a quiz", use_container_width=True):
            go_to("AI Quiz")

    with y:
        st.markdown("""
        <div class="panel">
            <div class="panel-title">PDF Notes</div>
            <div class="panel-note">
                Convert your study PDF into organised revision notes.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Prepare notes", use_container_width=True):
            go_to("PDF Notes")

    with z:
        st.markdown("""
        <div class="panel">
            <div class="panel-title">Study Chat</div>
            <div class="panel-note">
                Ask questions and get simple explanations.
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ask a question", use_container_width=True):
            go_to("Study Chat")

    st.markdown("### Recent activity")
    st.write(st.session_state.last_activity)


elif page == "AI Quiz":
    show_heading("AI Quiz Studio", "Create practice questions for your revision.")

    topic = st.text_input(
        "Subject or topic",
        placeholder="Example: Semiconductor, C programming, AI"
    )

    level = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard", "Mixed"]
    )

    question_count = st.selectbox(
        "Number of questions",
        [5, 10, 20, 30, 40, 50, 75, 100],
        index=2
    )

    question_type = st.selectbox(
        "Question format",
        [
            "Multiple choice questions with answers",
            "Short answer questions with answers",
            "Mixed question types with answers"
        ]
    )

    if st.button("Generate quiz", type="primary", use_container_width=True):
        if not topic.strip():
            st.warning("Pehle subject ya topic enter karo.")
        else:
            results = []
            progress = st.progress(0)
            status = st.empty()
            batch_size = 10

            for start in range(0, question_count, batch_size):
                current = min(batch_size, question_count - start)
                first_num = start + 1
                last_num = start + current

                status.write(
                    f"Generating questions {first_num}–{last_num} "
                    f"of {question_count}..."
                )

                prompt = f"""
                Create exactly {current} study quiz questions about:
                {topic}

                Difficulty: {level}
                Format: {question_type}

                These are questions {first_num} to {last_num}
                in a quiz of {question_count} questions.

                Requirements:
                - Number every question.
                - Give accurate answers.
                - For MCQs, provide four options labelled A, B, C, D.
                - Clearly identify the correct answer.
                - Add a short explanation for each answer.
                - Keep questions distinct and relevant.
                - Do not add an introduction or conclusion.
                - Use clear, student-friendly language.
                """

                answer = ask_ai(prompt, max_tokens=3500)

                if not answer:
                    break

                results.append(answer)
                progress.progress(last_num / question_count)

            status.empty()
            progress.empty()

            if results:
                combined = "\n\n".join(results)
                st.session_state.last_quiz = combined
                st.session_state.generated_quizzes += 1
                st.session_state.quiz_history.append({
                    "topic": topic,
                    "count": question_count,
                    "date": datetime.now().strftime("%d %b %Y %H:%M")
                })
                st.session_state.last_activity = f"Created quiz: {topic}"
                st.success("Quiz generation complete.")

    if st.session_state.last_quiz:
        st.markdown("---")
        show_heading("Your quiz", "Review your questions and answers below.")
        st.markdown(st.session_state.last_quiz)

        st.download_button(
            "Download quiz as TXT",
            data=st.session_state.last_quiz,
            file_name="study_buddy_quiz.txt",
            mime="text/plain",
            use_container_width=True
        )


elif page == "PDF Notes":
    show_heading(
        "PDF Notes Studio",
        "Upload notes and turn them into clear, point-wise revision material."
    )

    uploaded_file = st.file_uploader(
        "Upload your study PDF",
        type=["pdf"]
    )

    if uploaded_file:
        if st.button("Read PDF", type="primary"):
            try:
                extracted = extract_pdf_text(uploaded_file)

                if not extracted:
                    st.warning(
                        "Is PDF se text nahi mila. Ho sakta hai PDF scanned ho."
                    )
                else:
                    st.session_state.pdf_text = extracted
                    st.success("PDF successfully read.")
                    st.write(f"Extracted text: {len(extracted)} characters")
            except Exception as e:
                st.error(f"PDF read nahi ho payi: {e}")

    if st.session_state.pdf_text:
        notes_style = st.selectbox(
            "Notes format",
            [
                "Short Notes",
                "Detailed Notes",
                "Key Points",
                "Summary Notes",
                "Question–Answer Notes"
            ]
        )

        length = st.selectbox(
            "Detail level",
            ["Concise", "Balanced", "Detailed"]
        )

        if st.button("Generate notes", type="primary", use_container_width=True):
            instructions = {
                "Short Notes": "Write short, exam-ready notes with headings and bullets.",
                "Detailed Notes": "Explain each important concept clearly with examples where useful.",
                "Key Points": "Give the most important points as organised bullet lists.",
                "Summary Notes": "Summarise the material under clear topic headings.",
                "Question–Answer Notes": "Create important questions with clear answers from the material."
            }

            prompt = f"""
            Prepare student-friendly notes using only the source material below.

            Format: {notes_style}
            Detail level: {length}

            Instructions:
            - Use clear headings and subheadings.
            - Prefer numbered points and bullet lists.
            - Avoid huge paragraphs.
            - Explain difficult terms in simple English.
            - Preserve important definitions, formulas and examples.
            - Do not invent information missing from the source.
            - Keep the notes organised for revision.
            - Do not add comments about being an AI.

            Source material:
            {st.session_state.pdf_text[:26000]}
            """

            with st.spinner("Preparing your notes..."):
                notes = ask_ai(prompt, max_tokens=6000)

            if notes:
                st.session_state.last_notes = notes
                st.session_state.notes_created += 1
                st.session_state.notes_history.append({
                    "format": notes_style,
                    "date": datetime.now().strftime("%d %b %Y %H:%M")
                })
                st.session_state.last_activity = f"Created {notes_style}"

    if st.session_state.last_notes:
        st.markdown("---")
        show_heading("Your revision notes", "Your generated notes are ready.")

        st.markdown(st.session_state.last_notes)

        st.download_button(
            "Download notes as TXT",
            data=st.session_state.last_notes,
            file_name="study_buddy_notes.txt",
            mime="text/plain",
            use_container_width=True
        )

        try:
            pdf_data = make_pdf(
                st.session_state.last_notes,
                "Study Buddy AI - Revision Notes"
            )

            st.download_button(
                "Download notes as PDF",
                data=pdf_data,
                file_name="Study_Buddy_Revision_Notes.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.warning(f"PDF export issue: {e}")


elif page == "Study Chat":
    show_heading(
        "Study Chat",
        "Ask about concepts, examples, formulas or your revision topics."
    )

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Type your study question...")

    if question:
        st.session_state.chat_messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Preparing an explanation..."):
                history = st.session_state.chat_messages[-10:]

                client = get_client()
                reply = None

                if client:
                    try:
                        response = client.chat.completions.create(
                            model=MODEL,
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "You are a helpful study tutor. "
                                        "Explain concepts in simple, clear "
                                        "student-friendly language. Use steps, "
                                        "examples and headings when helpful."
                                    )
                                },
                                *history
                            ],
                            max_tokens=2500,
                            temperature=0.4
                        )
                        reply = response.choices[0].message.content
                    except Exception as e:
                        st.error(f"Chat error: {e}")

            if reply:
                st.markdown(reply)
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": reply
                })
                st.session_state.last_activity = "Used Study Chat"
                st.rerun()

    if st.session_state.chat_messages:
        if st.button("Clear chat"):
            st.session_state.chat_messages = []
            st.rerun()


elif page == "Performance":
    show_heading(
        "Performance",
        "A quick overview of your activity in this session."
    )

    a, b, c = st.columns(3)

    a.metric("Quizzes created", st.session_state.generated_quizzes)
    b.metric("Notes created", st.session_state.notes_created)
    c.metric("Chat messages", len(st.session_state.chat_messages))

    st.markdown("### Quiz history")

    if st.session_state.quiz_history:
        for item in reversed(st.session_state.quiz_history):
            st.markdown(
                f"- **{item['topic']}** — {item['count']} questions "
                f"· {item['date']}"
            )
    else:
        st.info("Your generated quizzes will appear here during this session.")

    st.markdown("### Notes history")

    if st.session_state.notes_history:
        for item in reversed(st.session_state.notes_history):
            st.markdown(f"- {item['format']} · {item['date']}")
    else:
        st.info("Your generated notes will appear here during this session.")

    st.caption(
        "Activity counts are stored in the current app session and may reset "
        "when the session restarts."
    )


elif page == "Settings":
    show_heading(
        "Settings",
        "Manage your study workspace."
    )

    st.markdown("""
    <div class="panel">
        <div class="panel-title">Appearance</div>
        <div class="panel-note">
            Pastel sage green and white theme is enabled.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### AI configuration")
    st.write(f"Configured model: `{MODEL}`")
    st.write("API provider: Groq")

    st.markdown("### Session data")

    if st.button("Clear quiz and notes history"):
        st.session_state.quiz_history = []
        st.session_state.notes_history = []
        st.session_state.last_quiz = ""
        st.session_state.last_notes = ""
        st.session_state.generated_quizzes = 0
        st.session_state.notes_created = 0
        st.success("Quiz and notes history cleared.")
        st.rerun()

    if st.button("Clear all chat messages"):
        st.session_state.chat_messages = []
        st.success("Chat cleared.")
        st.rerun()