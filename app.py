import streamlit as st
from groq import Groq
from pypdf import PdfReader
from io import BytesIO
from datetime import datetime
import json
import re

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #F6F7F1;
    --surface: #FFFFFF;
    --green: #315940;
    --green-dark: #203D2B;
    --green-soft: #E8EFE5;
    --text: #25382B;
    --muted: #788579;
    --border: #E1E7DD;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: var(--bg);
    color: var(--text);
}

.block-container {
    max-width: 1450px;
    padding-top: 1.3rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background: #EAF0E6;
    border-right: 1px solid #DCE5D8;
}

[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}

[data-testid="stSidebar"] * {
    color: var(--text);
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 5px;
}

.brand-icon {
    background: #315940;
    color: white;
    width: 44px;
    height: 44px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
}

.brand-name {
    color: #243D2D;
    font-size: 17px;
    font-weight: 800;
}

.brand-sub {
    color: #788579;
    font-size: 11px;
    margin-top: 3px;
}

.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: white;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 15px 20px;
    margin-bottom: 22px;
}

.topbar-title {
    color: #25382B;
    font-size: 15px;
    font-weight: 700;
}

.topbar-sub {
    color: #788579;
    font-size: 11px;
    margin-top: 4px;
}

.hero {
    background:
    linear-gradient(100deg, rgba(27,53,37,.96), rgba(48,83,57,.78)),
    url("https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1800&q=85");
    background-position: center;
    background-size: cover;
    padding: 36px;
    border-radius: 22px;
    margin-bottom: 24px;
}

.hero-label {
    color: #D3E5D2;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
}

.hero h1 {
    color: white;
    font-size: 34px;
    font-weight: 800;
    margin: 15px 0 10px;
}

.hero p {
    color: #E5EDE4;
    font-size: 13px;
    line-height: 1.8;
    max-width: 600px;
}

.section-title {
    font-size: 23px;
    font-weight: 800;
    color: #263C2D;
    margin: 26px 0 5px;
}

.section-subtitle {
    font-size: 12px;
    color: #788579;
    margin-bottom: 18px;
}

.stat-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 17px;
    padding: 19px;
    min-height: 126px;
}

.stat-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .7px;
    color: #788579;
}

.stat-value {
    color: #315940;
    font-size: 29px;
    font-weight: 800;
    margin-top: 13px;
}

.stat-foot {
    color: #879287;
    font-size: 11px;
    margin-top: 5px;
}

.tool-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px;
    min-height: 180px;
}

.tool-icon {
    width: 43px;
    height: 43px;
    border-radius: 13px;
    background: #EAF0E6;
    color: #315940;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    margin-bottom: 17px;
}

.tool-card h3 {
    color: #2A4632;
    font-size: 16px;
    margin: 0 0 8px;
}

.tool-card p {
    color: #788579;
    font-size: 12px;
    line-height: 1.8;
}

.info-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 16px;
}

.info-card h3 {
    color: #2B4833;
    font-size: 16px;
}

.info-card p {
    color: #788579;
    font-size: 12px;
    line-height: 1.8;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid var(--border);
    padding: 17px;
    border-radius: 15px;
}

div[data-testid="stMetricLabel"] {
    color: #788579;
}

div[data-testid="stMetricValue"] {
    color: #315940;
}

div.stButton > button {
    background: #315940;
    color: white;
    border: 1px solid #315940;
    border-radius: 10px;
    font-weight: 600;
    min-height: 42px;
}

div.stButton > button:hover {
    background: #203D2B;
    color: white;
    border-color: #203D2B;
}

div[data-testid="stDownloadButton"] button {
    background: #E8EFE5;
    color: #315940;
    border: 1px solid #D7E3D3;
    border-radius: 10px;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    border-radius: 10px;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

.footer {
    color: #879287;
    font-size: 11px;
    text-align: center;
    padding-top: 25px;
}

</style>
""", unsafe_allow_html=True)


def init_state():
    defaults = {
        "generated_quizzes": 0,
        "notes_created": 0,
        "chat_messages": 0,
        "quiz_history": [],
        "chat_history": [],
        "last_activity": "No activity yet",
        "pdf_text": "",
        "notes_text": "",
        "latest_quiz": "",
        "page": "Dashboard"
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


def get_client():
    try:
        return Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception:
        return None


def ask_ai(prompt, system_message="You are a helpful study assistant. Explain in simple English."):
    client = get_client()

    if client is None:
        st.error(
            "GROQ_API_KEY nahi mili. Streamlit app ke Settings → Secrets "
            "mein apni API key add karo."
        )
        return None

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content
    except Exception as error:
        st.error("AI response generate nahi ho saka. Dobara try karo.")
        st.caption(str(error))
        return None


def activity(key):
    st.session_state[key] += 1
    st.session_state.last_activity = datetime.now().strftime(
        "%d %b %Y, %I:%M %p"
    )


def go_to(page_name):
    st.session_state.page = page_name


with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div class="brand-icon">✦</div>
        <div>
            <div class="brand-name">Study Buddy AI</div>
            <div class="brand-sub">YOUR PERSONAL STUDY SPACE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.caption("WORKSPACE")

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "AI Quiz",
            "PDF Notes",
            "Study Chat",
            "Performance",
            "Settings"
        ],
        index=[
            "Dashboard",
            "AI Quiz",
            "PDF Notes",
            "Study Chat",
            "Performance",
            "Settings"
        ].index(st.session_state.page)
        if st.session_state.page in [
            "Dashboard",
            "AI Quiz",
            "PDF Notes",
            "Study Chat",
            "Performance",
            "Settings"
        ] else 0,
        label_visibility="collapsed"
    )

    st.session_state.page = page

    st.divider()

    st.markdown("""
    <div class="info-card">
        <h3>Study at your pace</h3>
        <p>Use your notes, practise questions and ask doubts in one place.</p>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Study Buddy AI · Personal learning workspace")


page = st.session_state.page

top_left, top_right = st.columns([8, 1])

with top_left:
    st.markdown(f"""
    <div class="topbar">
        <div>
            <div class="topbar-title">{page}</div>
            <div class="topbar-sub">Your learning workspace</div>
        </div>
        <div class="topbar-sub">{datetime.now().strftime("%d %b %Y")}</div>
    </div>
    """, unsafe_allow_html=True)

with top_right:
    with st.popover("⋮", use_container_width=True):
        st.markdown("**Quick menu**")
        st.caption("Choose a workspace")
        if st.button("Dashboard", use_container_width=True):
            go_to("Dashboard")
            st.rerun()
        if st.button("AI Quiz", use_container_width=True):
            go_to("AI Quiz")
            st.rerun()
        if st.button("PDF Notes", use_container_width=True):
            go_to("PDF Notes")
            st.rerun()
        if st.button("Study Chat", use_container_width=True):
            go_to("Study Chat")
            st.rerun()
        if st.button("Performance", use_container_width=True):
            go_to("Performance")
            st.rerun()
        if st.button("Settings", use_container_width=True):
            go_to("Settings")
            st.rerun()


if page == "Dashboard":
    hour = datetime.now().hour
    greeting = (
        "Good morning" if hour < 12
        else "Good afternoon" if hour < 17
        else "Good evening"
    )

    st.markdown(f"""
    <div class="hero">
        <div class="hero-label">YOUR PERSONAL LEARNING SPACE</div>
        <h1>{greeting} 👋</h1>
        <p>Learn with clarity, practise with purpose and keep your study
        material organised. Your next study session starts here.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Your overview</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">A quick look at your learning activity.</div>',
                unsafe_allow_html=True)

    cols = st.columns(4)
    metrics = [
        ("QUIZZES CREATED", st.session_state.generated_quizzes, "Practice sessions"),
        ("NOTES SESSIONS", st.session_state.notes_created, "Notes created"),
        ("CHAT MESSAGES", st.session_state.chat_messages, "Questions explored"),
        ("LEARNING TOOLS", "03", "Available in workspace")
    ]

    for col, (label, value, foot) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">{label}</div>
                <div class="stat-value">{value}</div>
                <div class="stat-foot">{foot}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Your learning tools</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Select a tool to continue.</div>',
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="tool-card">
            <div class="tool-icon">✦</div>
            <h3>AI Quiz Studio</h3>
            <p>Generate practice questions from a topic or your own notes.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Quiz Studio →", key="home_quiz", use_container_width=True):
            go_to("AI Quiz")
            st.rerun()

    with c2:
        st.markdown("""
        <div class="tool-card">
            <div class="tool-icon">▤</div>
            <h3>PDF Notes</h3>
            <p>Extract study material from PDF files and make revision notes.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open PDF Notes →", key="home_pdf", use_container_width=True):
            go_to("PDF Notes")
            st.rerun()

    with c3:
        st.markdown("""
        <div class="tool-card">
            <div class="tool-icon">✎</div>
            <h3>Study Chat</h3>
            <p>Ask doubts and get easy explanations of difficult concepts.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Study Chat →", key="home_chat", use_container_width=True):
            go_to("Study Chat")
            st.rerun()

    left, right = st.columns([1.3, 1])

    with left:
        st.markdown("""
        <div class="info-card">
            <h3>Today's study reminder</h3>
            <p>Focus on understanding one concept at a time. A short
            practice session can help you identify what to revise next.</p>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="info-card">
            <h3>Recent activity</h3>
        """, unsafe_allow_html=True)
        st.write(st.session_state.last_activity)
        st.markdown("</div>", unsafe_allow_html=True)


elif page == "AI Quiz":
    st.title("AI Quiz Studio")
    st.write("Create practice questions from your subject or study material.")

    topic = st.text_input("Topic or chapter", placeholder="Example: Semiconductor, C programming, NLP")
    material = st.text_area("Study material (optional)", height=150, placeholder="Paste your notes here...")

    c1, c2 = st.columns(2)

    with c1:
        count = st.selectbox("Number of questions", list(range(10, 101, 10)))

    with c2:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"])

    kind = st.selectbox(
        "Question format",
        ["MCQs with answers", "Short answer questions", "Mixed questions"]
    )

    if st.button("Generate quiz", use_container_width=True):
        if not topic.strip() and not material.strip():
            st.warning("Topic ya study material enter karo.")
        else:
            batches = (count + 9) // 10
            results = []
            progress = st.progress(0)
            status = st.empty()

            for batch in range(batches):
                how_many = min(10, count - len(results))
                status.write(f"Generating batch {batch + 1} of {batches}...")

                prompt = f"""
Create exactly {how_many} new questions for this batch.
Topic: {topic or "Use the supplied study material"}
Difficulty: {difficulty}
Format: {kind}
Study material:
{(material or topic)[:16000]}

Give clear questions. For MCQs, include four options A, B, C, D.
Give the correct answer and a brief explanation for each.
Avoid repeating questions from this batch.
Number the questions from 1 to {how_many}.
Use simple English.
"""
                answer = ask_ai(
                    prompt,
                    "You are an accurate educational quiz generator."
                )

                if not answer:
                    break

                results.append(answer)
                progress.progress((batch + 1) / batches)

            progress.empty()
            status.empty()

            if results:
                st.session_state.latest_quiz = "\n\n".join(results)
                st.session_state.quiz_history.append({
                    "topic": topic or "Study material",
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "batches": len(results)
                })
                activity("generated_quizzes")
                st.rerun()

    if st.session_state.latest_quiz:
        st.subheader("Generated questions")
        st.text_area("Your quiz", st.session_state.latest_quiz, height=420)
        st.download_button(
            "Download quiz",
            st.session_state.latest_quiz,
            file_name="study_buddy_quiz.txt",
            mime="text/plain",
            use_container_width=True
        )

        if st.button("Clear quiz"):
            st.session_state.latest_quiz = ""
            st.rerun()


elif page == "PDF Notes":
    st.title("PDF Notes")
    st.write("Upload a PDF, extract its text and generate revision notes.")

    file = st.file_uploader("Upload your PDF", type=["pdf"])

    if file and st.button("Extract text", use_container_width=True):
        try:
            reader = PdfReader(BytesIO(file.getvalue()))
            text_parts = [p.extract_text() or "" for p in reader.pages]
            extracted = "\n\n".join(text_parts).strip()

            if extracted:
                st.session_state.pdf_text = extracted
                st.success("PDF text extracted successfully.")
            else:
                st.warning("Text nahi mila. PDF scanned image ho sakti hai.")
        except Exception as error:
            st.error("PDF read nahi ho saki.")
            st.caption(str(error))

    if st.session_state.pdf_text:
        st.caption(f"Extracted characters: {len(st.session_state.pdf_text)}")
        st.text_area("Extracted text", st.session_state.pdf_text[:30000], height=230)

        if st.button("Create revision notes", use_container_width=True):
            with st.spinner("Creating notes..."):
                notes = ask_ai(
                    "Create detailed revision notes from the material below. "
                    "Use headings, definitions, key points and examples. "
                    "Use simple English and do not skip important topics.\n\n"
                    + st.session_state.pdf_text[:18000]
                )

            if notes:
                st.session_state.notes_text = notes
                activity("notes_created")
                st.rerun()

    if st.session_state.notes_text:
        st.subheader("Your revision notes")
        st.text_area("Notes", st.session_state.notes_text, height=350)
        st.download_button(
            "Download notes",
            st.session_state.notes_text,
            file_name="study_buddy_notes.txt",
            mime="text/plain",
            use_container_width=True
        )


elif page == "Study Chat":
    st.title("Study Chat")
    st.write("Ask questions about your subject and get simple explanations.")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a study question...")

    if question:
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_ai(
                    question,
                    "You are Study Buddy AI, a patient study tutor. "
                    "Explain step by step in simple English. Use examples "
                    "when useful. If asked for code, provide complete code."
                )

            if answer:
                st.markdown(answer)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer
                })
                activity("chat_messages")

    if st.session_state.chat_history:
        if st.button("Clear chat history"):
            st.session_state.chat_history = []
            st.rerun()


elif page == "Performance":
    st.title("Performance")
    st.write("Review your activity in this current app session.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Quizzes created", st.session_state.generated_quizzes)
    c2.metric("Notes sessions", st.session_state.notes_created)
    c3.metric("Chat messages", st.session_state.chat_messages)

    st.subheader("Quiz history")

    if st.session_state.quiz_history:
        st.dataframe(
            st.session_state.quiz_history,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Your quiz history will appear here after you create a quiz.")

    st.subheader("Recent activity")
    st.write(st.session_state.last_activity)

    st.caption(
        "Activity counters are stored in the current session. "
        "They are not a permanent account-wide record."
    )


elif page == "Settings":
    st.title("Settings")
    st.write("Manage your workspace preferences.")

    st.subheader("Appearance")
    st.write("Theme: Sage green and off-white")
    st.write("Layout: Wide desktop-style workspace")

    st.subheader("AI connection")
    if get_client() is not None:
        st.success("Groq API key is configured.")
    else:
        st.warning("Groq API key is missing or could not be read.")
        st.markdown("""
        Add your key in Streamlit → app Settings → Secrets:
        """)
        st.code('GROQ_API_KEY = "your_groq_api_key_here"', language="toml")
        st.caption("Apni real API key public GitHub repository mein mat daalna.")

    st.subheader("Session data")
    st.write("Clear the temporary chat, quiz and notes data for this session.")

    if st.button("Clear session data", use_container_width=True):
        for key in [
            "generated_quizzes",
            "notes_created",
            "chat_messages",
            "quiz_history",
            "chat_history",
            "last_activity",
            "pdf_text",
            "notes_text",
            "latest_quiz"
        ]:
            if key in st.session_state:
                del st.session_state[key]

        st.rerun()


st.markdown(
    '<div class="footer">STUDY BUDDY AI · LEARN WITH CLARITY</div>',
    unsafe_allow_html=True
)
