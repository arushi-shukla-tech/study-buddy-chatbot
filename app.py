import os
import io
import re
import html
from datetime import datetime

import streamlit as st
from groq import Groq
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_NAME = "Study Buddy AI"
MODEL_NAME = "openai/gpt-oss-20b"

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --green: #087f5b;
        --green-dark: #07533e;
        --green-light: #e8f7ef;
        --text: #18352c;
        --muted: #738279;
        --border: #e3ebe6;
        --background: #f5f8f6;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background: var(--background);
        color: var(--text);
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background: #102e25;
        border-right: 1px solid #25483b;
    }

    [data-testid="stSidebar"] * {
        color: #edf8f1;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #c0d8cb;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 0 22px;
    }

    .brand-icon {
        width: 49px;
        height: 49px;
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 27px;
        background: linear-gradient(135deg, #16a875, #70dca8);
        box-shadow: 0 8px 22px rgba(0,0,0,.18);
    }

    .brand-name {
        font-family: 'Manrope', sans-serif;
        font-size: 22px;
        line-height: 1.2;
        font-weight: 800;
        letter-spacing: -.7px;
        color: #ffffff;
    }

    .brand-tag {
        font-size: 10px;
        letter-spacing: 1.7px;
        text-transform: uppercase;
        color: #b5d4c4;
        margin-top: 5px;
    }

    .hero {
        background:
          linear-gradient(105deg, rgba(7,55,39,.97), rgba(8,127,91,.88)),
          url('https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=1600&q=85');
        background-position: center;
        background-size: cover;
        padding: 35px;
        border-radius: 23px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 12px 30px rgba(8,75,51,.12);
    }

    .hero-kicker {
        color: #b5f3d0;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .hero h1 {
        color: white;
        font-family: 'Manrope', sans-serif;
        font-size: clamp(29px, 4vw, 43px);
        line-height: 1.15;
        font-weight: 800;
        letter-spacing: -1.2px;
        margin: 0 0 13px;
    }

    .hero p {
        color: #e1f2e9;
        font-size: 14px;
        line-height: 1.8;
        max-width: 650px;
        margin: 0;
    }

    .section-title {
        font-family: 'Manrope', sans-serif;
        font-size: 23px;
        font-weight: 800;
        color: var(--text);
        margin: 8px 0 5px;
    }

    .section-subtitle {
        color: var(--muted);
        font-size: 13px;
        margin-bottom: 19px;
    }

    .metric-card, .feature-card {
        background: white;
        border: 1px solid var(--border);
        border-radius: 17px;
        padding: 20px;
        box-shadow: 0 4px 17px rgba(18,55,39,.035);
    }

    .metric-card {
        min-height: 125px;
    }

    .metric-label {
        font-size: 12px;
        color: var(--muted);
        font-weight: 600;
        margin-bottom: 12px;
    }

    .metric-value {
        font-family: 'Manrope', sans-serif;
        font-size: 29px;
        font-weight: 800;
        color: var(--text);
        line-height: 1.2;
    }

    .metric-note {
        font-size: 11px;
        color: var(--green);
        margin-top: 9px;
    }

    .feature-card {
        min-height: 175px;
        margin-bottom: 8px;
    }

    .feature-icon {
        display: flex;
        width: 44px;
        height: 44px;
        align-items: center;
        justify-content: center;
        border-radius: 13px;
        background: var(--green-light);
        font-size: 23px;
        margin-bottom: 13px;
    }

    .feature-card h3 {
        font-family: 'Manrope', sans-serif;
        font-size: 16px;
        color: var(--text);
        margin: 0 0 8px;
    }

    .feature-card p {
        font-size: 12px;
        line-height: 1.7;
        color: var(--muted);
        margin: 0;
    }

    .info-banner {
        background: #eaf7ef;
        border: 1px solid #d2eddd;
        border-radius: 13px;
        padding: 15px 17px;
        color: #176548;
        font-size: 13px;
        line-height: 1.7;
        margin: 12px 0 20px;
    }

    .app-footer {
        border-top: 1px solid var(--border);
        padding-top: 17px;
        margin-top: 32px;
        color: #819087;
        text-align: center;
        font-size: 11px;
    }

    .stButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-weight: 700;
        border: 1px solid #dce8e1;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(110deg, #087f5b, #11a982);
        color: #ffffff !important;
        border: none;
    }

    .stButton > button[kind="primary"]:hover {
        background: #056347;
        color: #ffffff !important;
    }

    .stDownloadButton > button {
        background: linear-gradient(110deg, #087f5b, #11a982) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 0 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }

    .stDownloadButton > button * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    .stDownloadButton > button:hover {
        background: #056347 !important;
        color: #ffffff !important;
    }

    .stTextInput input, .stTextArea textarea,
    .stNumberInput input, div[data-baseweb="select"] {
        border-radius: 10px;
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 15px;
        border: 1px solid var(--border);
        border-radius: 13px;
    }

    div[data-testid="stExpander"] {
        background: white;
        border: 1px solid var(--border);
        border-radius: 12px;
    }

    @media (max-width: 768px) {
        .hero {
            padding: 25px 20px;
            border-radius: 17px;
        }
        .metric-value {
            font-size: 24px;
        }
        .feature-card {
            padding: 16px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DEFAULTS = {
    "quiz_history": [],
    "notes_history": [],
    "chat_messages": [],
    "current_notes": "",
    "current_quiz": "",
    "pdf_text": "",
    "last_uploaded_name": "",
    "student_name": "Student",
    "study_goal": 2,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def get_api_key():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        if key:
            return str(key).strip()
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY", "").strip()


def get_client():
    key = get_api_key()
    if not key:
        return None
    try:
        return Groq(api_key=key)
    except Exception:
        return None


def ask_ai(prompt, system_message=None, temperature=0.4):
    client = get_client()

    if client is None:
        return "GROQ_API_KEY is missing. Configure it in Streamlit Secrets."

    messages = []

    if system_message:
        messages.append({
            "role": "system",
            "content": system_message,
        })

    messages.append({
        "role": "user",
        "content": prompt,
    })

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content or "No response received."
    except Exception as error:
        return f"AI request failed: {error}"


def clean_filename(value):
    value = re.sub(r"[^a-zA-Z0-9_-]+", "_", value.strip())
    return value[:65] or "study_notes"


def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages).strip()


def make_pointwise_notes(raw_notes):
    output = []

    for line in raw_notes.splitlines():
        line = line.strip()

        if not line:
            output.append("")
        elif line.startswith("#"):
            output.append(line)
        elif re.match(r"^(\d+[\.\)]|[-*•])\s*", line):
            output.append(line)
        elif len(line) > 180:
            sentences = re.split(r"(?<=[.!?])\s+", line)
            output.extend("- " + sentence.strip() for sentence in sentences if sentence.strip())
        else:
            output.append("- " + line)

    return "\n".join(output).strip()


def build_pdf(title, content):
    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
        title=title,
        author=APP_NAME,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocumentTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=27,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#087f5b"),
        spaceAfter=10,
    )

    heading_style = ParagraphStyle(
        "DocumentHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#087f5b"),
        spaceBefore=11,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        "DocumentBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#263c32"),
        spaceAfter=6,
        wordWrap="CJK",
    )

    story = [
        Paragraph(html.escape(title), title_style),
        Paragraph(
            "Created with Study Buddy AI",
            ParagraphStyle(
                "Subtitle",
                parent=body_style,
                alignment=TA_CENTER,
                textColor=colors.HexColor("#71817a"),
            ),
        ),
        Spacer(1, 13),
        HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor("#d8e9df"),
        ),
        Spacer(1, 13),
    ]

    for line in content.splitlines():
        stripped = line.strip()

        if not stripped:
            story.append(Spacer(1, 4))
        elif stripped.startswith("### "):
            story.append(Paragraph(html.escape(stripped[4:]), heading_style))
        elif stripped.startswith("## "):
            story.append(Paragraph(html.escape(stripped[3:]), heading_style))
        elif stripped.startswith("# "):
            story.append(Paragraph(html.escape(stripped[2:]), heading_style))
        elif stripped.startswith(("- ", "* ", "• ")):
            story.append(
                Paragraph(
                    "&#8226;&nbsp; " + html.escape(stripped[2:].strip()),
                    body_style,
                )
            )
        else:
            story.append(Paragraph(html.escape(stripped), body_style))

    document.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def make_hero(kicker, title, description):
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-kicker">{html.escape(kicker)}</div>
            <h1>{html.escape(title)}</h1>
            <p>{html.escape(description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def make_section(title, subtitle=""):
    st.markdown(
        f"""
        <div class="section-title">{html.escape(title)}</div>
        <div class="section-subtitle">{html.escape(subtitle)}</div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(label)}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
            <div class="metric-note">{html.escape(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feature_card(icon, title, description):
    st.markdown(
        f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <h3>{html.escape(title)}</h3>
            <p>{html.escape(description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_footer():
    st.markdown(
        """
        <div class="app-footer">
            STUDY BUDDY AI · Learn smarter, one concept at a time.
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">🎓</div>
            <div>
                <div class="brand-name">Study Buddy AI</div>
                <div class="brand-tag">Your smart study space</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### WORKSPACE")

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "AI Quiz",
            "PDF Notes",
            "Study Chat",
            "Performance",
            "Settings",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### STUDY OVERVIEW")
    st.caption(f"Quizzes created: {len(st.session_state.quiz_history)}")
    st.caption(f"Notes created: {len(st.session_state.notes_history)}")
    st.caption(f"Chat messages: {len(st.session_state.chat_messages)}")


if page == "Dashboard":
    make_hero(
        "YOUR PERSONAL LEARNING SPACE",
        "Study smarter with AI.",
        "Create revision notes, practise with custom quizzes, "
        "and understand difficult concepts with your AI study companion.",
    )

    make_section(
        f"Welcome back, {st.session_state.student_name}",
        "Everything you need for a focused study session.",
    )

    cols = st.columns(4)
    metrics = [
        ("QUIZZES CREATED", len(st.session_state.quiz_history), "Practice sessions"),
        ("NOTES CREATED", len(st.session_state.notes_history), "Revision library"),
        ("CHAT MESSAGES", len(st.session_state.chat_messages), "Learning conversations"),
        ("DAILY STUDY GOAL", f"{st.session_state.study_goal} hrs", "Daily target"),
    ]

    for col, item in zip(cols, metrics):
        with col:
            metric_card(*item)

    make_section("Your study workspace", "Choose a tool to get started.")

    col1, col2 = st.columns(2)

    with col1:
        feature_card("🧠", "AI Quiz Generator", "Create custom MCQs and review your answers.")
        feature_card("📄", "Smart PDF Notes", "Transform study PDFs into point-wise revision notes.")
        if st.button("Open PDF Notes", use_container_width=True):
            st.session_state["_next_page"] = "PDF Notes"
            st.rerun()

    with col2:
        feature_card("💬", "Study Chat", "Ask questions and understand concepts step by step.")
        feature_card("📊", "Performance", "Review your quiz and notes history.")
        if st.button("Open AI Quiz", use_container_width=True):
            st.session_state["_next_page"] = "AI Quiz"
            st.rerun()

    show_footer()


elif page == "AI Quiz":
    make_hero(
        "PRACTISE • LEARN • IMPROVE",
        "AI Quiz Studio",
        "Create personalised practice questions and revise important concepts.",
    )

    make_section("Create a new quiz", "Choose a topic and customise your session.")

    with st.form("quiz_form"):
        topic = st.text_input("Subject or topic", placeholder="e.g. Semiconductors, Python, NLP")
        col1, col2 = st.columns(2)

        with col1:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)

        with col2:
            question_count = st.selectbox("Number of questions", [5, 10, 15, 20])

        include_explanations = st.checkbox("Include answer explanations", value=True)
        submitted = st.form_submit_button("Generate Quiz", type="primary", use_container_width=True)

    if submitted:
        if not topic.strip():
            st.warning("Enter a topic to generate your quiz.")
        else:
            prompt = f"""
Create exactly {question_count} multiple-choice questions about {topic}.
Difficulty: {difficulty}.

For every question:
- Number the question.
- Give four options labelled A, B, C and D.
- Provide exactly one correct answer.
- Use clear student-friendly language.
- {"Explain each correct answer briefly." if include_explanations else "Do not include explanations."}

Finish with a separate answer key.
Use this structure:

## Question 1
Question text

A. Option
B. Option
C. Option
D. Option

## Answer Key
1. Correct option
"""

            with st.spinner("Creating quiz..."):
                result = ask_ai(
                    prompt,
                    system_message="You are a professional teacher who creates accurate educational quizzes.",
                )

            if result and not result.startswith(("GROQ_API_KEY is missing", "AI request failed:")):
                st.session_state.current_quiz = result
                st.session_state.quiz_history.append({
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Topic": topic,
                    "Difficulty": difficulty,
                    "Questions": question_count,
                })

    if st.session_state.current_quiz:
        make_section("Your generated quiz", "Review or download your questions.")
        st.markdown(st.session_state.current_quiz)

        st.download_button(
            "Download Quiz TXT",
            data=st.session_state.current_quiz.encode("utf-8"),
            file_name="study_buddy_quiz.txt",
            mime="text/plain",
            use_container_width=True,
        )

    show_footer()


elif page == "PDF Notes":
    make_hero(
        "READ LESS • UNDERSTAND MORE",
        "Smart PDF Notes",
        "Transform your study material into organised point-wise revision notes.",
    )

    make_section("Upload study material", "Text-based PDF files work best.")

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None:
        if st.session_state.last_uploaded_name != uploaded_file.name:
            st.session_state.pdf_text = ""
            st.session_state.current_notes = ""
            st.session_state.last_uploaded_name = uploaded_file.name

        st.success(f"Uploaded: {uploaded_file.name}")

        col1, col2 = st.columns(2)

        with col1:
            note_style = st.selectbox(
                "Notes style",
                ["Exam-ready notes", "Detailed notes", "Quick revision notes"],
            )

        with col2:
            note_language = st.selectbox(
                "Language",
                ["Simple English", "Hindi", "Hinglish"],
            )

        if st.button("Extract PDF Text", use_container_width=True):
            try:
                with st.spinner("Reading PDF..."):
                    st.session_state.pdf_text = extract_pdf_text(uploaded_file)

                if not st.session_state.pdf_text:
                    st.warning("No selectable text was found in this PDF.")
                else:
                    st.success("PDF text extracted.")

            except Exception as error:
                st.error(f"Could not read PDF: {error}")

        if st.session_state.pdf_text:
            with st.expander("Preview extracted text"):
                st.text(st.session_state.pdf_text[:5000])

            if st.button("Generate Point-wise Notes", type="primary", use_container_width=True):
                style_rules = {
                    "Exam-ready notes": "Include definitions, headings, key points, examples, applications and a short conclusion.",
                    "Detailed notes": "Explain important concepts thoroughly using headings and bullet points.",
                    "Quick revision notes": "Create concise revision notes with key definitions, formulas and short bullet points.",
                }

                prompt = f"""
Create accurate study notes from the source text below.

Language: {note_language}
Style: {note_style}

{style_rules[note_style]}

Formatting requirements:
1. Use clear headings and subheadings.
2. Write point-wise, not in long paragraphs.
3. Put every important idea in a separate bullet point.
4. Explain definitions in simple language.
5. Preserve important formulas and explain symbols.
6. Include relevant examples.
7. Do not invent facts that are absent from the source.
8. Finish with a Quick Revision section.
9. Do not add unnecessary introductory messages.

Source:
{st.session_state.pdf_text[:24000]}
"""

                with st.spinner("Preparing notes..."):
                    notes = ask_ai(
                        prompt,
                        system_message="You are a professional academic note-maker. Create accurate, exam-friendly, point-wise notes.",
                    )

                if notes and not notes.startswith(("GROQ_API_KEY is missing", "AI request failed:")):
                    st.session_state.current_notes = make_pointwise_notes(notes)
                    st.session_state.notes_history.append({
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "File": uploaded_file.name,
                        "Style": note_style,
                        "Language": note_language,
                    })

    if st.session_state.current_notes:
        make_section("Your study notes", "Point-wise notes ready to download.")
        st.markdown(st.session_state.current_notes)

        filename = clean_filename(
            st.session_state.last_uploaded_name.replace(".pdf", "")
        )

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "Download TXT",
                data=st.session_state.current_notes.encode("utf-8"),
                file_name=f"{filename}_notes.txt",
                mime="text/plain; charset=utf-8",
                use_container_width=True,
            )

        with col2:
            try:
                pdf_data = build_pdf(
                    "Study Buddy AI - Study Notes",
                    st.session_state.current_notes,
                )

                st.download_button(
                    "Download PDF",
                    data=pdf_data,
                    file_name=f"{filename}_notes.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as error:
                st.error(f"PDF export failed: {error}")

    show_footer()


elif page == "Study Chat":
    make_hero(
        "ASK • EXPLORE • UNDERSTAND",
        "Your AI Study Partner",
        "Get clear explanations and step-by-step help with academic concepts.",
    )

    make_section("Study conversation", "Ask a question to begin or continue learning.")

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask a question about your studies...")

    if prompt:
        st.session_state.chat_messages.append({
            "role": "user",
            "content": prompt,
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                client = get_client()

                if client is None:
                    answer = "GROQ_API_KEY is missing. Configure it in Streamlit Secrets."
                else:
                    try:
                        messages = [{
                            "role": "system",
                            "content": (
                                "You are Study Buddy AI, a helpful academic tutor. "
                                "Use clear explanations, headings and bullet points. "
                                "Provide complete working code when requested."
                            ),
                        }]

                        messages.extend(st.session_state.chat_messages[-12:])

                        response = client.chat.completions.create(
                            model=MODEL_NAME,
                            messages=messages,
                            temperature=0.4,
                        )

                        answer = response.choices[0].message.content or "No response received."

                    except Exception as error:
                        answer = f"AI request failed: {error}"

                st.markdown(answer)

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": answer,
        })
        st.rerun()

    if st.session_state.chat_messages:
        chat_text = "\n\n".join(
            f"{message['role'].title()}:\n{message['content']}"
            for message in st.session_state.chat_messages
        )

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "Download Chat TXT",
                data=chat_text.encode("utf-8"),
                file_name="study_buddy_chat.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with col2:
            if st.button("Clear Conversation", use_container_width=True):
                st.session_state.chat_messages = []
                st.rerun()

    show_footer()


elif page == "Performance":
    make_hero(
        "YOUR LEARNING JOURNEY",
        "Performance Overview",
        "Review your quiz history and created study materials.",
    )

    cols = st.columns(3)
    metrics = [
        ("QUIZZES GENERATED", len(st.session_state.quiz_history), "Total quiz sessions"),
        ("NOTES CREATED", len(st.session_state.notes_history), "Total notes sessions"),
        ("CHAT MESSAGES", len(st.session_state.chat_messages), "Current conversation"),
    ]

    for col, item in zip(cols, metrics):
        with col:
            metric_card(*item)

    make_section("Quiz history", "Your recently generated quizzes.")

    if st.session_state.quiz_history:
        for quiz in reversed(st.session_state.quiz_history):
            with st.expander(f"{quiz.get('Topic', 'Quiz')} · {quiz.get('Date', '')}"):
                st.write(f"Difficulty: {quiz.get('Difficulty', 'N/A')}")
                st.write(f"Questions: {quiz.get('Questions', 'N/A')}")
    else:
        st.info("Your quiz history will appear here.")

    make_section("Notes history", "Your recently created notes.")

    if st.session_state.notes_history:
        for note in reversed(st.session_state.notes_history):
            with st.expander(note.get("File", "Study notes")):
                st.write(f"Date: {note.get('Date', 'N/A')}")
                st.write(f"Style: {note.get('Style', 'N/A')}")
                st.write(f"Language: {note.get('Language', 'N/A')}")
    else:
        st.info("Your notes history will appear here.")

    show_footer()


elif page == "Settings":
    make_hero(
        "PERSONALISE YOUR EXPERIENCE",
        "Settings",
        "Manage your study preferences and application data.",
    )

    make_section("Study preferences", "Customise your study workspace.")

    with st.form("settings_form"):
        student_name = st.text_input(
            "Display name",
            value=st.session_state.student_name,
            max_chars=50,
        )

        study_options = [1, 2, 3, 4, 5, 6, 8]
        current_goal = st.session_state.study_goal

        study_goal = st.selectbox(
            "Daily study goal",
            study_options,
            index=study_options.index(current_goal) if current_goal in study_options else 1,
            format_func=lambda hours: f"{hours} hour(s) per day",
        )

        save = st.form_submit_button(
            "Save Preferences",
            type="primary",
            use_container_width=True,
        )

    if save:
        st.session_state.student_name = student_name.strip() or "Student"
        st.session_state.study_goal = study_goal
        st.rerun()

    st.markdown("---")
    make_section("Data management", "Clear saved activity from this session.")

    confirm = st.checkbox("I understand that clearing activity cannot be undone.")

    if st.button("Clear All Activity", use_container_width=True):
        if confirm:
            st.session_state.quiz_history = []
            st.session_state.notes_history = []
            st.session_state.chat_messages = []
            st.session_state.current_notes = ""
            st.session_state.current_quiz = ""
            st.session_state.pdf_text = ""
            st.session_state.last_uploaded_name = ""
            st.rerun()

    st.markdown("---")
    make_section("Application", "Study Buddy AI configuration.")

    if get_api_key():
        st.success("Groq API key configured.")
    else:
        st.warning("Configure GROQ_API_KEY in Streamlit Secrets.")

    show_footer()
