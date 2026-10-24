import streamlit as st
from groq import Groq
from pypdf import PdfReader
from io import BytesIO
from datetime import datetime

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #f5f8fe;
    color: #172b4d;
}
header[data-testid="stHeader"] {
    background: rgba(245,248,254,0.95);
}
.block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}
section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e5eaf3;
}
section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}
.brand {
    font-size: 24px;
    font-weight: 800;
    color: #183b72;
    letter-spacing: -0.8px;
}
.brand-sub {
    color: #7888a3;
    font-size: 12px;
    margin-top: 3px;
}
.eyebrow {
    color: #3975d5;
    text-transform: uppercase;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.5px;
}
.page-title {
    color: #172b4d;
    font-size: 31px;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 4px;
}
.page-subtitle {
    color: #71809a;
    font-size: 14px;
    margin-bottom: 22px;
}
.hero {
    background: linear-gradient(120deg, #12376e 0%, #1c5bb0 62%, #3985e7 100%);
    border-radius: 22px;
    padding: 30px 32px;
    color: white;
    min-height: 235px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 12px 30px rgba(28, 91, 176, 0.14);
}
.hero:after {
    content: "";
    position: absolute;
    width: 240px;
    height: 240px;
    border: 35px solid rgba(255,255,255,0.09);
    border-radius: 50%;
    right: -45px;
    top: -70px;
}
.hero h1 {
    font-size: 31px;
    line-height: 1.25;
    font-weight: 800;
    margin: 10px 0;
    color: white;
}
.hero p {
    color: #dceaff;
    font-size: 14px;
    line-height: 1.7;
    max-width: 540px;
}
.hero-label {
    display: inline-block;
    padding: 6px 11px;
    background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .3px;
}
.section-heading {
    color: #172b4d;
    font-size: 19px;
    font-weight: 800;
    margin-top: 25px;
    margin-bottom: 4px;
}
.section-caption {
    color: #7a89a2;
    font-size: 12px;
    margin-bottom: 15px;
}
.metric-card {
    background: #ffffff;
    border: 1px solid #e7edf6;
    border-radius: 16px;
    padding: 18px;
    min-height: 120px;
    box-shadow: 0 4px 16px rgba(35,65,110,0.025);
}
.metric-label {
    color: #7b8aa3;
    font-size: 12px;
    font-weight: 600;
}
.metric-value {
    color: #17396f;
    font-size: 28px;
    font-weight: 800;
    margin-top: 8px;
}
.metric-note {
    color: #7e8ba2;
    font-size: 11px;
    margin-top: 4px;
}
.feature-card {
    background: #ffffff;
    border: 1px solid #e5ebf5;
    border-radius: 16px;
    padding: 20px;
    min-height: 175px;
}
.feature-card h3 {
    color: #193c73;
    font-size: 16px;
    margin: 12px 0 7px;
}
.feature-card p {
    color: #71809a;
    font-size: 12px;
    line-height: 1.7;
}
.feature-icon {
    display: inline-block;
    background: #edf4ff;
    color: #2c67c7;
    border-radius: 11px;
    padding: 10px 12px;
    font-size: 18px;
    font-weight: 800;
}
.info-card {
    background: white;
    border: 1px solid #e5ebf5;
    border-radius: 16px;
    padding: 20px;
}
.info-title {
    color: #1b3e76;
    font-weight: 800;
    font-size: 15px;
    margin-bottom: 12px;
}
.small-muted {
    color: #7c8ba3;
    font-size: 12px;
    line-height: 1.7;
}
div.stButton > button {
    background: #245fc0;
    color: white;
    border: 1px solid #245fc0;
    border-radius: 10px;
    min-height: 42px;
    font-weight: 600;
    transition: all .2s ease;
}
div.stButton > button:hover {
    background: #174b9f;
    color: white;
    border-color: #174b9f;
}
div[data-testid="stDownloadButton"] > button {
    border-radius: 10px;
    font-weight: 600;
}
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    border-radius: 10px;
}
hr {
    border-color: #e5ebf5;
}
div[data-testid="stChatMessage"] {
    border: 1px solid #e8eef7;
    border-radius: 14px;
}
.footer {
    color: #8a97ad;
    text-align: center;
    font-size: 11px;
    padding-top: 30px;
}
</style>
""", unsafe_allow_html=True)


def get_client():
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        api_key = ""

    if not api_key:
        return None

    try:
        return Groq(api_key=api_key)
    except Exception:
        return None


def ask_ai(prompt, system_message="You are Study Buddy AI, a helpful study assistant. Explain concepts clearly in simple English."):
    client = get_client()

    if client is None:
        return None, "Groq API key is missing. Add GROQ_API_KEY in Streamlit Secrets."

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content, None
    except Exception as error:
        return None, "AI request failed: " + str(error)


def initialize_state():
    defaults = {
        "page_choice": "Dashboard",
        "chat_history": [],
        "generated_quizzes": 0,
        "notes_created": 0,
        "chat_messages": 0,
        "last_activity": "Your study activity will appear here.",
        "last_result": ""
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def go_to_page(page):
    st.session_state.page_choice = page


def page_header(title, subtitle):
    st.markdown(f"""
    <div class="eyebrow">STUDY BUDDY AI</div>
    <div class="page-title">{title}</div>
    <div class="page-subtitle">{subtitle}</div>
    """, unsafe_allow_html=True)


def metric_card(label, value, note):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)


def feature_card(icon, title, description):
    st.markdown(f"""
    <div class="feature-card">
        <div class="feature-icon">{icon}</div>
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)


initialize_state()

with st.sidebar:
    st.markdown("""
    <div class="brand">Study Buddy AI</div>
    <div class="brand-sub">INTELLIGENT LEARNING ASSISTANT</div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("**WORKSPACE**")
    st.radio(
        "Navigate",
        [
            "Dashboard",
            "AI Quiz",
            "PDF Notes",
            "Study Chat",
            "Performance",
            "Settings"
        ],
        key="page_choice",
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("**YOUR STUDY SPACE**")
    st.markdown(
        "<div class='small-muted'>Create practice questions, understand difficult topics, and turn PDF material into revision notes.</div>",
        unsafe_allow_html=True
    )

    st.divider()

    client_ready = get_client() is not None
    if client_ready:
        st.success("AI connection configured")
    else:
        st.warning("AI setup required")

    st.markdown(
        "<div class='small-muted'>Built for focused and organised learning.</div>",
        unsafe_allow_html=True
    )


page = st.session_state.page_choice


if page == "Dashboard":
    st.markdown("""
    <div class="hero">
        <div class="hero-label">YOUR PERSONAL STUDY WORKSPACE</div>
        <h1>Learn smarter.<br>Prepare with confidence.</h1>
        <p>
            Your learning companion for creating practice quizzes,
            simplifying study material, and getting help with difficult topics.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div class='section-heading'>Your workspace</div>"
        "<div class='section-caption'>A quick overview of your learning tools.</div>",
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Quizzes generated", st.session_state.generated_quizzes, "Practice sets created")
    with c2:
        metric_card("Notes created", st.session_state.notes_created, "PDF note sessions")
    with c3:
        metric_card("Chat messages", st.session_state.chat_messages, "Messages sent to AI")
    with c4:
        metric_card("AI assistant", "Ready" if get_client() else "Setup", "Connection status")

    st.markdown(
        "<div class='section-heading'>Learning tools</div>"
        "<div class='section-caption'>Choose a tool to get started.</div>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        feature_card("Q", "AI Quiz Generator", "Generate topic-based multiple-choice questions for revision.")
        st.button("Open AI Quiz", key="open_quiz", use_container_width=True,
                  on_click=go_to_page, args=("AI Quiz",))
    with col2:
        feature_card("N", "PDF Notes Maker", "Upload a study PDF and turn its text into structured revision notes.")
        st.button("Create PDF Notes", key="open_notes", use_container_width=True,
                  on_click=go_to_page, args=("PDF Notes",))
    with col3:
        feature_card("S", "Study Chat", "Ask questions and get explanations in simple, student-friendly language.")
        st.button("Ask Study Buddy", key="open_chat", use_container_width=True,
                  on_click=go_to_page, args=("Study Chat",))

    left, right = st.columns([1.35, 1], gap="large")

    with left:
        st.markdown("<div class='section-heading'>How to use your workspace</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="info-card">
            <div class="info-title">A simple study routine</div>
            <p class="small-muted"><b>01 — Understand</b><br>Use Study Chat to learn a concept step by step.</p>
            <p class="small-muted"><b>02 — Revise</b><br>Upload your PDF and create organised revision notes.</p>
            <p class="small-muted"><b>03 — Practise</b><br>Generate questions from a topic and test your understanding.</p>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("<div class='section-heading'>Recent activity</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-card">
            <div class="info-title">Latest update</div>
            <p class="small-muted">{st.session_state.last_activity}</p>
            <hr>
            <p class="small-muted">Activity is stored for the current app session. It may reset when the app restarts.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        "<div class='footer'>Study Buddy AI · Intelligent Learning Assistant</div>",
        unsafe_allow_html=True
    )


elif page == "AI Quiz":
    page_header("AI Quiz Generator", "Create practice questions for a subject or topic.")

    with st.container(border=True):
        st.markdown("#### Quiz details")
        subject = st.text_input("Subject", placeholder="e.g. Applied Mathematics")
        topic = st.text_input("Topic", placeholder="e.g. Matrices and determinants")
        difficulty = st.selectbox("Difficulty level", ["Easy", "Medium", "Hard", "Mixed"])
        number = st.selectbox("Number of questions", [5, 10, 15, 20])
        question_type = st.selectbox("Question format", ["Multiple-choice questions", "Short-answer questions"])

        if st.button("Generate Questions", use_container_width=True):
            if not subject.strip() or not topic.strip():
                st.warning("Please enter both the subject and topic.")
            else:
                prompt = f"""
Create {number} {question_type.lower()} for a college student.

Subject: {subject}
Topic: {topic}
Difficulty: {difficulty}

Requirements:
- Number questions from 1 to {number}.
- Keep wording clear and accurate.
- For multiple-choice questions, provide four options labelled A, B, C, and D.
- Give the correct answer and a short explanation after each question.
- Do not skip any question.
- Use simple English and proper formatting.
"""
                with st.spinner("Preparing your questions..."):
                    result, error = ask_ai(
                        prompt,
                        "You are an educational quiz creator. Produce accurate, clearly formatted practice questions."
                    )

                if error:
                    st.error(error)
                else:
                    st.session_state.quiz_result = result
                    st.session_state.generated_quizzes += 1
                    st.session_state.last_activity = f"Generated a quiz on {topic}."
                    st.rerun()

    if st.session_state.get("quiz_result"):
        st.markdown("### Generated quiz")
        st.markdown(st.session_state.quiz_result)
        st.download_button(
            "Download quiz as text",
            data=st.session_state.quiz_result,
            file_name="study_buddy_quiz.txt",
            mime="text/plain",
            use_container_width=True
        )


elif page == "PDF Notes":
    page_header("PDF Notes Maker", "Turn your PDF study material into revision-friendly notes.")

    st.markdown("""
    <div class="info-card">
        <div class="info-title">Create organised notes</div>
        <p class="small-muted">Upload a text-based PDF, select the note style, and let Study Buddy AI organise the important content.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_pdf = st.file_uploader("Upload your PDF file", type=["pdf"])
    note_style = st.selectbox(
        "Choose note style",
        ["Detailed revision notes", "Short exam notes", "Important questions and answers", "Key points and definitions"]
    )

    if st.button("Generate Notes", use_container_width=True):
        if uploaded_pdf is None:
            st.warning("Please upload a PDF first.")
        else:
            try:
                reader = PdfReader(BytesIO(uploaded_pdf.getvalue()))
                extracted_text = "\n".join(
                    page.extract_text() or "" for page in reader.pages
                )
                extracted_text = extracted_text.strip()

                if not extracted_text:
                    st.error("No readable text was found. This may be a scanned PDF.")
                elif len(extracted_text) < 30:
                    st.error("The PDF contains too little readable text.")
                else:
                    if len(extracted_text) > 24000:
                        extracted_text = extracted_text[:24000]

                    prompt = f"""
Create {note_style.lower()} from the study material below.

Instructions:
- Use clear headings and subheadings.
- Use simple English.
- Keep facts and definitions accurate to the supplied material.
- Highlight important formulas and terms when present.
- Do not invent details that are not supported by the material.
- Make the result useful for student revision.

Study material:
{extracted_text}
"""
                    with st.spinner("Reading the PDF and preparing notes..."):
                        result, error = ask_ai(
                            prompt,
                            "You are a careful study-notes assistant. Organise source material without making up facts."
                        )

                    if error:
                        st.error(error)
                    else:
                        st.session_state.notes_result = result
                        st.session_state.notes_created += 1
                        st.session_state.last_activity = f"Created notes from {uploaded_pdf.name}."
                        st.rerun()

            except Exception as error:
                st.error("Could not read this PDF: " + str(error))

    if st.session_state.get("notes_result"):
        st.markdown("### Your notes")
        st.markdown(st.session_state.notes_result)
        st.download_button(
            "Download revision notes",
            data=st.session_state.notes_result,
            file_name="study_buddy_notes.txt",
            mime="text/plain",
            use_container_width=True
        )


elif page == "Study Chat":
    page_header("Study Chat", "Ask questions and get explanations for your studies.")

    st.markdown("""
    <div class="info-card">
        <div class="info-title">Your AI study assistant</div>
        <p class="small-muted">Ask about concepts, formulas, examples, programming, or exam preparation. For important academic work, verify answers with your textbook or teacher.</p>
    </div>
    """, unsafe_allow_html=True)

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Ask a study question...")

    if user_prompt:
        st.session_state.chat_history.append(
            {"role": "user", "content": user_prompt}
        )
        st.session_state.chat_messages += 1

        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                history = st.session_state.chat_history[-10:]
                client = get_client()

                if client is None:
                    answer = "Please configure GROQ_API_KEY in Streamlit Secrets before using Study Chat."
                else:
                    try:
                        response = client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are Study Buddy AI, a patient tutor. Explain in simple English, step by step, with examples when useful."
                                }
                            ] + history,
                            temperature=0.5
                        )
                        answer = response.choices[0].message.content
                    except Exception as error:
                        answer = "I could not get a response. Please check your API setup. Details: " + str(error)

            st.markdown(answer)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer}
        )
        st.session_state.last_activity = "Used Study Chat."
        st.rerun()

    if st.session_state.chat_history:
        if st.button("Clear chat history"):
            st.session_state.chat_history = []
            st.rerun()


elif page == "Performance":
    page_header("Performance", "Review activity from your current app session.")

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Quiz sets", st.session_state.generated_quizzes, "Generated in this session")
    with c2:
        metric_card("Note sessions", st.session_state.notes_created, "PDF notes created")
    with c3:
        metric_card("Chat messages", st.session_state.chat_messages, "Questions submitted")

    st.markdown("<div class='section-heading'>Your learning activity</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="info-card">
        <div class="info-title">Most recent activity</div>
        <p class="small-muted">{st.session_state.last_activity}</p>
        <hr>
        <p class="small-muted">These are usage counts, not marks or quiz scores. They are stored in the current session and may reset when the app restarts.</p>
    </div>
    """, unsafe_allow_html=True)

    st.info("Quiz scoring and long-term progress tracking are not enabled in this version.")


elif page == "Settings":
    page_header("Settings", "Check the app configuration and session preferences.")

    st.markdown("### AI connection")
    if get_client():
        st.success("Groq API key is configured.")
    else:
        st.warning("Groq API key has not been detected.")

    st.markdown("### Configure your API key")
    st.markdown("""
    Add your API key in Streamlit Cloud:

    1. Open your app in Streamlit Cloud.
    2. Open the app menu and select **Settings** or **Manage app**.
    3. Find **Secrets**.
    4. Add the following setting, replacing the example with your own key.
    """)
    st.code('GROQ_API_KEY = "your_groq_api_key"', language="toml")

    st.markdown("### Session data")
    st.markdown(
        "Chat history, usage counts, and generated results are held in the current session. This version does not save personal study data to a database."
    )

    if st.button("Reset session activity"):
        st.session_state.generated_quizzes = 0
        st.session_state.notes_created = 0
        st.session_state.chat_messages = 0
        st.session_state.chat_history = []
        st.session_state.last_activity = "Your study activity will appear here."
        st.session_state.last_result = ""
        st.session_state.pop("quiz_result", None)
        st.session_state.pop("notes_result", None)
        st.success("Session activity reset.")
