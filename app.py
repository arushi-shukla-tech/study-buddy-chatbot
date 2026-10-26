import io
from datetime import datetime

import streamlit as st
from groq import Groq
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# SESSION STATE
# ==================================================

DEFAULTS = {
    "page": "Dashboard",
    "chat_history": [],
    "quiz_history": [],
    "notes_history": [],
    "activity": [],
    "last_quiz": "",
    "last_notes": "",
    "quiz_topic": "",
    "notes_title": "",
    "pdf_text": "",
    "pdf_name": "",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# CSS
# ==================================================

st.markdown(
    """
    <style>
    :root {
        --green: #176B50;
        --dark-green: #103B30;
        --light-green: #E8F5EE;
    }

    .stApp {
        background-color: #F5F8F6;
        color: #17382F;
    }

    [data-testid="stSidebar"] {
        background-color: #E8F2EB;
        border-right: 1px solid #D5E5D9;
    }

    [data-testid="stSidebar"] * {
        color: #17382F;
    }

    /* Toolbar visibility */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    header[data-testid="stHeader"] button,
    header[data-testid="stHeader"] button svg,
    header[data-testid="stHeader"] button svg path,
    header[data-testid="stHeader"] [data-testid="stToolbar"],
    header[data-testid="stHeader"] [data-testid="stToolbar"] button,
    header[data-testid="stHeader"] [data-testid="stToolbar"] button svg,
    header[data-testid="stHeader"] [data-testid="stToolbar"] button svg path {
        color: #103B30 !important;
        fill: #103B30 !important;
        stroke: #103B30 !important;
    }

    h1, h2, h3 {
        color: #103B30 !important;
    }

    .main-title {
        color: #103B30;
        font-size: 40px;
        font-weight: 800;
    }

    .subtitle {
        color: #557267;
        font-size: 16px;
        margin-bottom: 20px;
    }

    .hero {
        background: linear-gradient(135deg, #103B30, #23805F);
        color: white;
        padding: 28px;
        border-radius: 18px;
        margin: 15px 0 25px 0;
    }

    .hero h2 {
        color: white !important;
    }

    .hero p {
        color: #E4F4E9;
        font-size: 16px;
    }

    .stat-card {
        background: white;
        border: 1px solid #DCE9DF;
        border-radius: 15px;
        padding: 18px;
        min-height: 110px;
    }

    .stat-number {
        color: #176B50;
        font-size: 30px;
        font-weight: 800;
    }

    .stat-label {
        color: #557267;
        font-size: 14px;
    }

    .feature-card {
        background: white;
        border: 1px solid #DCE9DF;
        border-radius: 15px;
        padding: 18px;
        min-height: 135px;
        margin-bottom: 10px;
    }

    .feature-card h3 {
        font-size: 19px;
    }

    .feature-card p {
        color: #557267;
        font-size: 14px;
    }

    /* Green primary buttons */
    div.stButton > button[kind="primary"] {
        background-color: #176B50 !important;
        color: white !important;
        border: 1px solid #176B50 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        min-height: 44px;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #103B30 !important;
        color: white !important;
        border-color: #103B30 !important;
    }

    div.stButton > button[kind="secondary"] {
        color: #176B50 !important;
        border: 1px solid #176B50 !important;
        border-radius: 10px !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        background-color: #E8F5EE !important;
    }

    .stDownloadButton button {
        background-color: #176B50 !important;
        color: white !important;
        border: 1px solid #176B50 !important;
        border-radius: 10px !important;
    }

    .stDownloadButton button:hover {
        background-color: #103B30 !important;
    }

    hr {
        border-color: #DCE9DF;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# NAVIGATION
# ==================================================

PAGES = [
    "Dashboard",
    "AI Quiz",
    "PDF Notes",
    "Study Chat",
    "Performance",
    "Settings",
]


def go_to(page):
    st.session_state.page = page


# ==================================================
# AI FUNCTIONS
# ==================================================

MODEL = "openai/gpt-oss-20b"


def get_client():
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        api_key = ""

    if not api_key:
        return None

    return Groq(api_key=api_key)


def ask_ai(prompt, system_message=None):
    client = get_client()

    if client is None:
        return (
            "Groq API key is missing. Add GROQ_API_KEY to "
            "your Streamlit secrets before using AI features."
        )

    if system_message is None:
        system_message = (
            "You are Study Buddy AI, a helpful educational assistant. "
            "Explain concepts clearly and accurately. Use headings, "
            "bullet points, and examples when useful. Respond in English "
            "unless the user requests another language."
        )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=3000,
        )

        return response.choices[0].message.content or "No response received."

    except Exception as error:
        return (
            "The AI request failed. Check your Groq API key, model "
            "availability, and connection.\n\n"
            f"Error details: {error}"
        )


# ==================================================
# PDF FUNCTIONS
# ==================================================

def extract_pdf_text(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        text_parts = []

        for page in reader.pages:
            text_parts.append(page.extract_text() or "")

        return "\n\n".join(text_parts).strip()

    except Exception as error:
        st.error(f"Unable to read the PDF: {error}")
        return ""


def escape_html(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def make_pdf(title, content):
    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=25,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#103B30"),
        spaceAfter=18,
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#17382F"),
        spaceAfter=8,
    )

    story = [
        Paragraph(escape_html(title), title_style),
        Spacer(1, 10),
    ]

    for line in content.splitlines():
        if line.strip():
            story.append(
                Paragraph(escape_html(line.strip()), body_style)
            )
        else:
            story.append(Spacer(1, 6))

    document.build(story)
    buffer.seek(0)

    return buffer.getvalue()


def record_activity(action):
    st.session_state.activity.append({
        "action": action,
        "time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
    })


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:
    st.markdown("# 📚 Study Buddy AI")
    st.caption("Your personal learning assistant")
    st.divider()

    st.markdown("### Navigation")

    # A direct radio selection controls the active page.
    selected_page = st.radio(
        "Choose a page",
        PAGES,
        index=PAGES.index(st.session_state.page),
        key="page_navigation",
        label_visibility="collapsed",
    )

    # Keep the selected page in session state.
    st.session_state.page = selected_page

    st.divider()
    st.caption("Learn smarter, one step at a time.")


# ==================================================
# DASHBOARD
# ==================================================

if st.session_state.page == "Dashboard":

    st.markdown(
        '<div class="main-title">Study Dashboard</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">Everything you need to study smarter.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero">
            <h2>Welcome to Study Buddy AI!</h2>
            <p>
                Create practice quizzes, simplify study material,
                and get help with your questions.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)

    stats = [
        (len(st.session_state.quiz_history), "Quizzes Generated"),
        (len(st.session_state.notes_history), "Notes Created"),
        (len(st.session_state.chat_history), "Chat Messages"),
        (len(st.session_state.activity), "Activities"),
    ]

    for column, (number, label) in zip([c1, c2, c3, c4], stats):
        with column:
            st.markdown(
                f"""
                <div class="stat-card">
                    <div class="stat-number">{number}</div>
                    <div class="stat-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### Explore AI Tools")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            """
            <div class="feature-card">
                <h3>🧠 Explore AI Quiz</h3>
                <p>Generate topic-based questions to practice your knowledge.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Explore AI Quiz",
            key="dash_quiz",
            type="primary",
            use_container_width=True,
        ):
            go_to("AI Quiz")
            st.rerun()

    with col2:
        st.markdown(
            """
            <div class="feature-card">
                <h3>📝 Create Study Notes</h3>
                <p>Turn PDF study material into organized notes.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Create Study Notes",
            key="dash_notes",
            type="primary",
            use_container_width=True,
        ):
            go_to("PDF Notes")
            st.rerun()

    col3, col4 = st.columns(2, gap="large")

    with col3:
        st.markdown(
            """
            <div class="feature-card">
                <h3>💬 Ask a Question</h3>
                <p>Get clear explanations for study-related questions.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "Ask a Question",
            key="dash_chat",
            type="primary",
            use_container_width=True,
        ):
            go_to("Study Chat")
            st.rerun()

    with col4:
        st.markdown(
            """
            <div class="feature-card">
                <h3>📈 View My Progress</h3>
                <p>Review your quizzes, notes, and recent activity.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "View My Progress",
            key="dash_progress",
            type="primary",
            use_container_width=True,
        ):
            go_to("Performance")
            st.rerun()

    st.markdown("---")
    st.subheader("Recent Activity")

    if st.session_state.activity:
        for item in reversed(st.session_state.activity[-5:]):
            st.write(f"• {item['action']} — {item['time']}")
    else:
        st.info("Your recent activities will appear here.")


# ==================================================
# AI QUIZ
# ==================================================

elif st.session_state.page == "AI Quiz":

    st.title("AI Quiz Generator")
    st.caption("Create practice questions for any subject.")

    with st.form("quiz_form"):
        topic = st.text_input(
            "Subject or topic",
            placeholder="Example: BJT, C programming, semiconductors",
        )

        count = st.selectbox(
            "Number of questions",
            [5, 10, 15, 20],
            index=1,
        )

        difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard"],
            index=1,
        )

        question_type = st.selectbox(
            "Question format",
            [
                "Multiple-choice questions",
                "Short-answer questions",
                "Mixed questions",
            ],
        )

        submitted = st.form_submit_button(
            "Generate Quiz",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            prompt = f"""
Create an educational quiz in English.

Topic: {topic}
Number of questions: {count}
Difficulty: {difficulty}
Question format: {question_type}

Requirements:
1. Number every question.
2. Cover important concepts from the topic.
3. For multiple-choice questions, include options A, B, C, and D.
4. Include the correct answer and a brief explanation.
5. Keep the questions accurate and clearly written.
"""

            with st.spinner("Generating quiz..."):
                result = ask_ai(
                    prompt,
                    "You are an educational quiz creator. Create accurate quizzes in English.",
                )

            st.session_state.last_quiz = result
            st.session_state.quiz_topic = topic

            st.session_state.quiz_history.append({
                "topic": topic,
                "count": count,
                "difficulty": difficulty,
                "time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "content": result,
            })

            record_activity(f"Generated quiz: {topic}")

    if st.session_state.last_quiz:
        st.divider()
        st.subheader(f"Quiz: {st.session_state.quiz_topic}")
        st.markdown(st.session_state.last_quiz)

        st.download_button(
            "Download Quiz as TXT",
            data=st.session_state.last_quiz,
            file_name="study_quiz.txt",
            mime="text/plain",
            use_container_width=True,
        )

        st.download_button(
            "Download Quiz as PDF",
            data=make_pdf(
                f"Study Quiz - {st.session_state.quiz_topic}",
                st.session_state.last_quiz,
            ),
            file_name="study_quiz.pdf",
            mime="application/pdf",
            use_container_width=True,
        )


# ==================================================
# PDF NOTES
# ==================================================

elif st.session_state.page == "PDF Notes":

    st.title("PDF Study Notes")
    st.caption("Upload a PDF and create structured study notes.")

    uploaded_file = st.file_uploader(
        "Upload PDF",
        type=["pdf"],
    )

    if uploaded_file is not None:

        if st.session_state.pdf_name != uploaded_file.name:
            st.session_state.pdf_name = uploaded_file.name
            st.session_state.pdf_text = ""
            st.session_state.last_notes = ""

        if not st.session_state.pdf_text:
            with st.spinner("Reading PDF..."):
                st.session_state.pdf_text = extract_pdf_text(uploaded_file)

        if st.session_state.pdf_text:
            st.success(f"Text extracted from {uploaded_file.name}")

            with st.expander("Preview extracted text"):
                st.text(st.session_state.pdf_text[:5000])

            note_format = st.selectbox(
                "Notes format",
                [
                    "Detailed notes",
                    "Short revision notes",
                    "Exam-oriented notes",
                    "Important questions and answers",
                ],
            )

            extra_instructions = st.text_area(
                "Additional instructions",
                placeholder="Example: Include definitions and formulas.",
            )

            if st.button(
                "Generate Study Notes",
                key="generate_notes",
                type="primary",
                use_container_width=True,
            ):
                prompt = f"""
Create study notes in English using ONLY the source text below.

Format: {note_format}
Additional instructions: {extra_instructions}

Requirements:
- Cover the important information in the source.
- Use clear headings and bullet points.
- Explain difficult concepts in simple English.
- Preserve important formulas and definitions.
- Do not invent unsupported facts.
- Mention if the source text appears incomplete.

SOURCE TEXT:
{st.session_state.pdf_text[:24000]}
"""

                with st.spinner("Creating study notes..."):
                    result = ask_ai(
                        prompt,
                        "You are an educational note-making assistant. "
                        "Use the supplied source faithfully and write in English.",
                    )

                st.session_state.last_notes = result
                st.session_state.notes_title = uploaded_file.name

                st.session_state.notes_history.append({
                    "title": uploaded_file.name,
                    "format": note_format,
                    "time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "content": result,
                })

                record_activity(f"Created notes: {uploaded_file.name}")

        else:
            st.warning(
                "No readable text was found. This PDF may contain scanned pages."
            )

    else:
        st.info("Upload a PDF to begin.")

    if st.session_state.last_notes:
        st.divider()
        st.subheader("Generated Study Notes")
        st.markdown(st.session_state.last_notes)

        st.download_button(
            "Download Notes as TXT",
            data=st.session_state.last_notes,
            file_name="study_notes.txt",
            mime="text/plain",
            use_container_width=True,
        )

        st.download_button(
            "Download Notes as PDF",
            data=make_pdf(
                f"Study Notes - {st.session_state.notes_title}",
                st.session_state.last_notes,
            ),
            file_name="study_notes.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    if st.button("Clear Current PDF", type="secondary"):
        st.session_state.pdf_text = ""
        st.session_state.pdf_name = ""
        st.session_state.last_notes = ""
        st.session_state.notes_title = ""
        st.rerun()


# ==================================================
# STUDY CHAT
# ==================================================

elif st.session_state.page == "Study Chat":

    st.title("Study Chat")
    st.caption("Ask questions and receive step-by-step explanations.")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Type your study question...")

    if user_prompt:
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_prompt,
        })

        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_ai(
                    user_prompt,
                    "You are Study Buddy AI, a patient educational assistant. "
                    "Explain answers step by step in English by default. "
                    "Use examples when helpful.",
                )
            st.markdown(answer)

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer,
        })

        record_activity("Asked a question in Study Chat")
        st.rerun()

    if st.session_state.chat_history:
        if st.button("Clear Chat", type="secondary"):
            st.session_state.chat_history = []
            st.rerun()


# ==================================================
# PERFORMANCE
# ==================================================

elif st.session_state.page == "Performance":

    st.title("My Study Progress")
    st.caption("Review your generated quizzes, notes, and activity.")

    m1, m2, m3 = st.columns(3)

    m1.metric("Quizzes Generated", len(st.session_state.quiz_history))
    m2.metric("Notes Created", len(st.session_state.notes_history))
    m3.metric("Chat Messages", len(st.session_state.chat_history))

    st.divider()
    st.subheader("Quiz History")

    if st.session_state.quiz_history:
        for index, quiz in enumerate(
            reversed(st.session_state.quiz_history),
            start=1,
        ):
            with st.expander(f"{index}. {quiz['topic']} — {quiz['time']}"):
                st.write(f"Difficulty: {quiz['difficulty']}")
                st.write(f"Questions: {quiz['count']}")
                st.markdown(quiz["content"])

                st.download_button(
                    "Download Quiz",
                    data=quiz["content"],
                    file_name=f"quiz_{index}.txt",
                    mime="text/plain",
                    key=f"history_quiz_{index}",
                )
    else:
        st.info("No quizzes generated yet.")

    st.divider()
    st.subheader("Notes History")

    if st.session_state.notes_history:
        for index, notes in enumerate(
            reversed(st.session_state.notes_history),
            start=1,
        ):
            with st.expander(f"{index}. {notes['title']} — {notes['time']}"):
                st.write(f"Format: {notes['format']}")
                st.markdown(notes["content"])

                st.download_button(
                    "Download Notes",
                    data=notes["content"],
                    file_name=f"notes_{index}.txt",
                    mime="text/plain",
                    key=f"history_notes_{index}",
                )
    else:
        st.info("No notes created yet.")

    st.divider()
    st.subheader("Recent Activity")

    if st.session_state.activity:
        for item in reversed(st.session_state.activity):
            st.write(f"{item['time']} — {item['action']}")
    else:
        st.info("No activity recorded yet.")


# ==================================================
# SETTINGS
# ==================================================

elif st.session_state.page == "Settings":

    st.title("Settings")
    st.caption("Manage your app configuration and session data.")

    st.subheader("Groq API Configuration")

    try:
        api_key_exists = bool(st.secrets.get("GROQ_API_KEY", ""))
    except Exception:
        api_key_exists = False

    if api_key_exists:
        st.success("Groq API key is configured.")
    else:
        st.warning(
            "Groq API key is missing. Add GROQ_API_KEY to "
            "your Streamlit Cloud secrets."
        )

    st.markdown(
        """
        In Streamlit Cloud, open your app's settings and add this
        under Secrets:

        ```toml
        GROQ_API_KEY = "your_actual_groq_api_key"
        ```
        """
    )

    st.divider()
    st.subheader("Clear Session Data")

    confirm = st.checkbox(
        "I understand that this will clear the current session's data."
    )

    if st.button(
        "Clear All Session Data",
        type="primary",
        disabled=not confirm,
        use_container_width=True,
    ):
        for key, value in DEFAULTS.items():
            st.session_state[key] = value

        st.success("Session data cleared.")
        st.rerun()

    st.divider()
    st.caption("Study Buddy AI")


# ==================================================
# END
# ==================================================
