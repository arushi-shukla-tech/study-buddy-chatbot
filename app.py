import streamlit as st
from groq import Groq
from pypdf import PdfReader
from io import BytesIO

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp {
    background: #f3f6fb;
    color: #243650;
    font-family: 'Inter', sans-serif;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e0e7f0;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}

.brand {
    font-size: 24px;
    font-weight: 700;
    color: #1b416f;
    letter-spacing: -0.8px;
}

.brand-sub {
    font-size: 10px;
    color: #8290a4;
    margin-top: 5px;
    letter-spacing: 1px;
}

.eyebrow {
    color: #3973b9;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.3px;
    margin-bottom: 7px;
}

.page-title {
    color: #203752;
    font-size: 30px;
    font-weight: 700;
    letter-spacing: -0.8px;
    margin-bottom: 4px;
}

.page-subtitle {
    color: #78879b;
    font-size: 13px;
    margin-bottom: 22px;
}

.hero {
    background: #1c416d;
    border-radius: 13px;
    padding: 30px;
    color: white;
    min-height: 225px;
    border-bottom: 4px solid #5b91cc;
    position: relative;
    overflow: hidden;
}

.hero h1 {
    font-size: 31px;
    line-height: 1.3;
    font-weight: 700;
    margin: 13px 0 8px;
    color: white;
}

.hero p {
    color: #e0eaf6;
    font-size: 13px;
    line-height: 1.8;
    max-width: 570px;
}

.hero-label {
    display: inline-block;
    padding: 6px 10px;
    border: 1px solid #56769a;
    border-radius: 5px;
    color: #e4edf8;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
}

.section-heading {
    color: #253d5b;
    font-size: 18px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 4px;
}

.section-caption {
    color: #8290a3;
    font-size: 12px;
    margin-bottom: 15px;
}

.metric-card {
    background: white;
    border: 1px solid #e0e7f0;
    border-radius: 11px;
    padding: 17px;
    min-height: 112px;
    box-shadow: 0 2px 8px rgba(35, 57, 87, 0.025);
}

.metric-label {
    color: #7b899d;
    font-size: 12px;
    font-weight: 500;
}

.metric-value {
    color: #244d80;
    font-size: 27px;
    font-weight: 700;
    margin-top: 9px;
}

.metric-note {
    color: #8794a7;
    font-size: 10px;
    margin-top: 4px;
}

.feature-card, .info-card {
    background: #ffffff;
    border: 1px solid #e0e7f0;
    border-radius: 11px;
    padding: 19px;
    box-shadow: 0 2px 8px rgba(35, 57, 87, 0.025);
}

.feature-card {
    min-height: 160px;
}

.feature-icon {
    display: inline-block;
    background: #eaf1fb;
    color: #2c5e98;
    border-radius: 7px;
    padding: 9px 12px;
    font-size: 16px;
    font-weight: 700;
}

.feature-card h3 {
    color: #25456d;
    font-size: 15px;
    margin: 12px 0 7px;
}

.feature-card p, .small-muted {
    color: #77869a;
    font-size: 12px;
    line-height: 1.8;
}

.info-title {
    color: #29496e;
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 10px;
}

div.stButton > button {
    background: #285b96;
    color: white;
    border: 1px solid #285b96;
    border-radius: 8px;
    min-height: 41px;
    font-weight: 600;
}

div.stButton > button:hover {
    background: #1c416d;
    color: white;
    border-color: #1c416d;
}

div[data-testid="stDownloadButton"] > button {
    border-radius: 8px;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 8px;
}

div[data-testid="stChatMessage"] {
    border: 1px solid #e1e8f1;
    border-radius: 11px;
}

hr {
    border-color: #e2e8f0;
}

.footer {
    color: #8592a5;
    text-align: center;
    font-size: 11px;
    padding-top: 28px;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e0e7f0;
    border-radius: 10px;
    padding: 15px;
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


def ask_ai(prompt, system_message):
    client = get_client()

    if client is None:
        return None, "Groq API key is missing. Please configure it in Streamlit Secrets."

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
        "last_activity": "No recent activity yet.",
        "quiz_result": "",
        "notes_result": ""
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def go_to_page(page):
    st.session_state.page_choice = page


def page_header(title, subtitle):
    st.markdown(
        f"""
        <div class="eyebrow">STUDY BUDDY AI / WORKSPACE</div>
        <div class="page-title">{title}</div>
        <div class="page-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True
    )


def metric_card(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def feature_card(icon, title, description):
    st.markdown(
        f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


initialize_state()

with st.sidebar:
    st.markdown(
        """
        <div class="brand">Study Buddy AI</div>
        <div class="brand-sub">INTELLIGENT LEARNING ASSISTANT</div>
        """,
        unsafe_allow_html=True
    )

    st.divider()
    st.markdown("**MAIN MENU**")

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
    st.markdown("**ABOUT THIS WORKSPACE**")
    st.markdown(
        """
        <div class="small-muted">
        A study space to practise questions, organise notes and understand
        difficult topics with AI assistance.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    if get_client():
        st.success("AI connection configured")
    else:
        st.warning("AI setup required")

    st.markdown(
        "<div class='small-muted'>Study tools for everyday learning.</div>",
        unsafe_allow_html=True
    )


page = st.session_state.page_choice


if page == "Dashboard":
    page_header(
        "Dashboard",
        "Your study tools and recent activity in one place."
    )

    st.markdown(
        """
        <div class="hero">
            <div class="hero-label">YOUR STUDY WORKSPACE</div>
            <h1>Make time for learning.</h1>
            <p>
                Prepare for your next class, organise your study material,
                and practise important topics with Study Buddy AI.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "<div class='section-heading'>Workspace overview</div>"
        "<div class='section-caption'>Your activity in the current session.</div>",
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Quizzes generated",
            st.session_state.generated_quizzes,
            "Practice sets created"
        )

    with c2:
        metric_card(
            "Notes created",
            st.session_state.notes_created,
            "PDF note sessions"
        )

    with c3:
        metric_card(
            "Chat messages",
            st.session_state.chat_messages,
            "Questions sent to AI"
        )

    with c4:
        metric_card(
            "AI assistant",
            "Ready" if get_client() else "Setup",
            "Connection status"
        )

    st.markdown(
        "<div class='section-heading'>Your learning tools</div>"
        "<div class='section-caption'>Choose a tool to continue.</div>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        feature_card(
            "Q",
            "AI Quiz Generator",
            "Create topic-based questions to practise what you have studied."
        )
        st.button(
            "Open AI Quiz",
            key="open_quiz",
            use_container_width=True,
            on_click=go_to_page,
            args=("AI Quiz",)
        )

    with col2:
        feature_card(
            "N",
            "PDF Notes Maker",
            "Convert readable PDF study material into organised revision notes."
        )
        st.button(
            "Open PDF Notes",
            key="open_notes",
            use_container_width=True,
            on_click=go_to_page,
            args=("PDF Notes",)
        )

    with col3:
        feature_card(
            "S",
            "Study Chat",
            "Ask questions about concepts, formulas, programming and more."
        )
        st.button(
            "Open Study Chat",
            key="open_chat",
            use_container_width=True,
            on_click=go_to_page,
            args=("Study Chat",)
        )

    left, right = st.columns([1.2, 1], gap="medium")

    with left:
        st.markdown(
            "<div class='section-heading'>A simple study routine</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div class="info-card">
                <div class="info-title">Study in three steps</div>
                <p class="small-muted">
                <b>01 &nbsp; Understand</b><br>
                Use Study Chat to understand a difficult concept.
                </p>
                <p class="small-muted">
                <b>02 &nbsp; Organise</b><br>
                Create revision notes from your study PDF.
                </p>
                <p class="small-muted">
                <b>03 &nbsp; Practise</b><br>
                Generate questions and review the answers.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with right:
        st.markdown(
            "<div class='section-heading'>Recent activity</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-title">Latest update</div>
                <p class="small-muted">{st.session_state.last_activity}</p>
                <hr>
                <p class="small-muted">
                Activity counts apply to the current session and may reset
                when the app restarts.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        "<div class='footer'>Study Buddy AI | Intelligent Learning Assistant</div>",
        unsafe_allow_html=True
    )


elif page == "AI Quiz":
    page_header(
        "AI Quiz Generator",
        "Create practice questions from the topics you are studying."
    )

    with st.container(border=True):
        st.markdown("### Quiz details")

        subject = st.text_input(
            "Subject",
            placeholder="e.g. Applied Mathematics"
        )

        topic = st.text_input(
            "Topic",
            placeholder="e.g. Matrices and determinants"
        )

        difficulty = st.selectbox(
            "Difficulty level",
            ["Easy", "Medium", "Hard", "Mixed"]
        )

        number = st.selectbox(
            "Number of questions",
            [5, 10, 15, 20]
        )

        question_type = st.selectbox(
            "Question format",
            ["Multiple-choice questions", "Short-answer questions"]
        )

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
- Number all questions.
- Use clear and accurate wording.
- For multiple-choice questions, provide four options A, B, C and D.
- Give the correct answer and a short explanation after each question.
- Use simple English.
- Do not skip any question.
"""

                with st.spinner("Preparing your questions..."):
                    result, error = ask_ai(
                        prompt,
                        "You are an educational quiz creator. Write accurate, well-organised practice questions."
                    )

                if error:
                    st.error(error)
                else:
                    st.session_state.quiz_result = result
                    st.session_state.generated_quizzes += 1
                    st.session_state.last_activity = (
                        f"Generated a quiz on {topic}."
                    )
                    st.rerun()

    if st.session_state.quiz_result:
        st.markdown("### Generated quiz")
        st.markdown(st.session_state.quiz_result)

        st.download_button(
            "Download quiz",
            data=st.session_state.quiz_result,
            file_name="study_buddy_quiz.txt",
            mime="text/plain",
            use_container_width=True
        )


elif page == "PDF Notes":
    page_header(
        "PDF Notes Maker",
        "Turn your study material into revision-friendly notes."
    )

    st.markdown(
        """
        <div class="info-card">
            <div class="info-title">Create organised notes</div>
            <p class="small-muted">
            Upload a text-based PDF, choose the style of notes you need,
            and generate a structured revision document.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_pdf = st.file_uploader(
        "Upload your PDF file",
        type=["pdf"]
    )

    note_style = st.selectbox(
        "Choose note style",
        [
            "Detailed revision notes",
            "Short exam notes",
            "Important questions and answers",
            "Key points and definitions"
        ]
    )

    if st.button("Generate Notes", use_container_width=True):
        if uploaded_pdf is None:
            st.warning("Please upload a PDF first.")
        else:
            try:
                reader = PdfReader(
                    BytesIO(uploaded_pdf.getvalue())
                )

                extracted_text = "\n".join(
                    page.extract_text() or ""
                    for page in reader.pages
                ).strip()

                if not extracted_text:
                    st.error(
                        "No readable text was found. This may be a scanned PDF."
                    )

                elif len(extracted_text) < 30:
                    st.error(
                        "The PDF contains too little readable text."
                    )

                else:
                    extracted_text = extracted_text[:24000]

                    prompt = f"""
Create {note_style.lower()} from the material below.

Instructions:
- Use clear headings and subheadings.
- Write in simple English.
- Keep facts and definitions accurate to the source.
- Highlight important formulas and terms when present.
- Do not invent information that is not supported by the material.
- Make the notes useful for student revision.

Study material:
{extracted_text}
"""

                    with st.spinner("Preparing your notes..."):
                        result, error = ask_ai(
                            prompt,
                            "You are a careful study-notes assistant. Organise source material accurately."
                        )

                    if error:
                        st.error(error)
                    else:
                        st.session_state.notes_result = result
                        st.session_state.notes_created += 1
                        st.session_state.last_activity = (
                            f"Created notes from {uploaded_pdf.name}."
                        )
                        st.rerun()

            except Exception as error:
                st.error("Could not read this PDF: " + str(error))

    if st.session_state.notes_result:
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
    page_header(
        "Study Chat",
        "Ask questions and work through difficult topics step by step."
    )

    st.markdown(
        """
        <div class="info-card">
            <div class="info-title">Your study assistant</div>
            <p class="small-muted">
            Ask about concepts, formulas, programming, examples or exam
            preparation. Verify important academic answers with your
            textbook or teacher.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

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
            with st.spinner("Preparing an explanation..."):
                client = get_client()
                history = st.session_state.chat_history[-10:]

                if client is None:
                    answer = (
                        "Please configure GROQ_API_KEY in Streamlit Secrets "
                        "before using Study Chat."
                    )
                else:
                    try:
                        response = client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "You are Study Buddy AI, a patient tutor. "
                                        "Explain concepts in simple English, "
                                        "step by step, using examples when useful."
                                    )
                                }
                            ] + history,
                            temperature=0.5
                        )

                        answer = response.choices[0].message.content

                    except Exception as error:
                        answer = (
                            "I could not get a response. Check your API setup. "
                            + str(error)
                        )

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
    page_header(
        "Performance",
        "Review your activity in the current app session."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card(
            "Quiz sets",
            st.session_state.generated_quizzes,
            "Generated in this session"
        )

    with c2:
        metric_card(
            "Notes created",
            st.session_state.notes_created,
            "PDF note sessions"
        )

    with c3:
        metric_card(
            "Chat messages",
            st.session_state.chat_messages,
            "Questions submitted"
        )

    st.markdown(
        "<div class='section-heading'>Recent learning activity</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-title">Latest update</div>
            <p class="small-muted">{st.session_state.last_activity}</p>
            <hr>
            <p class="small-muted">
            These figures count app usage, not academic marks.
            Data is held in the current session and may reset when
            the app restarts.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "Automatic quiz scoring and permanent progress tracking "
        "are not included in this version."
    )


elif page == "Settings":
    page_header(
        "Settings",
        "Check the AI connection and session information."
    )

    st.markdown("### AI connection")

    if get_client():
        st.success("Groq API key is configured.")
    else:
        st.warning("Groq API key has not been detected.")

    st.markdown("### Configure your API key")

    st.markdown("""
    1. Open your app in Streamlit Cloud.
    2. Open the app settings or Manage app section.
    3. Find Secrets.
    4. Add your API key using the format below.
    """)

    st.code(
        'GROQ_API_KEY = "your_groq_api_key"',
        language="toml"
    )

    st.markdown("### Session data")

    st.markdown(
        "Chat history, generated results and activity counts are stored "
        "in the current session. This version does not save personal "
        "study data to a database."
    )

    if st.button("Reset session activity"):
        st.session_state.generated_quizzes = 0
        st.session_state.notes_created = 0
        st.session_state.chat_messages = 0
        st.session_state.chat_history = []
        st.session_state.last_activity = "No recent activity yet."
        st.session_state.quiz_result = ""
        st.session_state.notes_result = ""
        st.success("Session activity reset.")
