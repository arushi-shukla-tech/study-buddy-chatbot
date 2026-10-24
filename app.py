import os
import io
import streamlit as st
from groq import Groq
from pypdf import PdfReader

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #071326;
    --panel: #0c1d37;
    --panel2: #102747;
    --blue: #3185ff;
    --cyan: #35d5f2;
    --text: #edf4ff;
    --muted: #9eb4d4;
    --border: #1c3c64;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(ellipse at 12% 0%, #102b50 0%, transparent 35%),
        var(--bg);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: rgba(7,19,38,0.9);
}

[data-testid="stSidebar"] {
    background: #08172c;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem;
}

.block-container {
    max-width: 1500px;
    padding-top: 1.8rem;
    padding-bottom: 2rem;
}

h1, h2, h3, p, label {
    color: var(--text);
}

h1 {
    font-weight: 800;
    letter-spacing: -1px;
}

h2, h3 {
    letter-spacing: -0.4px;
}

small, .muted {
    color: var(--muted);
}

.brand {
    padding: 12px 8px 24px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 22px;
}

.brand-icon {
    font-size: 35px;
    margin-right: 9px;
}

.brand-name {
    font-size: 23px;
    font-weight: 800;
    color: #f4f8ff;
    letter-spacing: -0.7px;
}

.brand-name span {
    color: var(--cyan);
}

.brand-sub {
    font-size: 11px;
    color: #8fb4e8;
    margin-left: 48px;
    margin-top: -3px;
    letter-spacing: 1px;
}

.hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(115deg, #0d2d58 0%, #0a2142 56%, #102c53 100%);
    border: 1px solid #24568b;
    border-radius: 22px;
    padding: 30px;
    min-height: 245px;
    margin-bottom: 18px;
}

.hero:after {
    content: "📚";
    position: absolute;
    right: 7%;
    top: 30px;
    font-size: 112px;
    opacity: 0.85;
    transform: rotate(-8deg);
    filter: drop-shadow(0 12px 24px #020b1c);
}

.hero:before {
    content: "";
    position: absolute;
    width: 240px;
    height: 240px;
    border-radius: 50%;
    right: 3%;
    top: 10px;
    background: radial-gradient(circle, rgba(53,213,242,.19), transparent 70%);
}

.hero-content {
    position: relative;
    z-index: 1;
    max-width: 68%;
}

.eyebrow {
    color: #79dcff;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 12px;
}

.hero h1 {
    font-size: clamp(29px, 3.2vw, 43px);
    line-height: 1.1;
    margin: 0 0 12px;
}

.hero h1 span {
    color: #48d9f6;
}

.hero p {
    color: #c4d7f3;
    line-height: 1.7;
    max-width: 480px;
    font-size: 14px;
}

.hero-note {
    display: inline-block;
    margin-top: 8px;
    padding: 8px 13px;
    border: 1px solid #315f90;
    background: rgba(5,20,41,.45);
    border-radius: 10px;
    color: #d4e8ff;
    font-size: 12px;
}

.section-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 22px 0 12px;
}

.section-heading h3 {
    margin: 0;
    font-size: 18px;
}

.section-heading span {
    color: var(--muted);
    font-size: 12px;
}

.metric-card {
    min-height: 120px;
    background: linear-gradient(145deg, #102747, #0a1b33);
    border: 1px solid #1e416b;
    border-radius: 17px;
    padding: 17px;
}

.metric-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.metric-icon {
    width: 39px;
    height: 39px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    font-size: 20px;
    background: #173b70;
}

.metric-label {
    font-size: 12px;
    color: #a8bfdf;
    margin-top: 12px;
}

.metric-value {
    font-size: 27px;
    font-weight: 800;
    margin-top: 3px;
}

.metric-foot {
    font-size: 11px;
    color: #4bd8c1;
    margin-top: 3px;
}

.feature-card {
    background: linear-gradient(145deg, #102a4c, #0a1a30);
    border: 1px solid #21476f;
    border-radius: 17px;
    padding: 20px;
    min-height: 180px;
}

.feature-icon {
    font-size: 29px;
    margin-bottom: 13px;
}

.feature-card h3 {
    font-size: 16px;
    margin: 0 0 8px;
}

.feature-card p {
    font-size: 12px;
    color: #a8bdd9;
    line-height: 1.65;
    min-height: 40px;
}

.info-panel {
    background: #0b1e38;
    border: 1px solid #1d3e64;
    border-radius: 17px;
    padding: 20px;
    margin-bottom: 14px;
}

.info-panel h3 {
    margin-top: 0;
    font-size: 16px;
}

.tip {
    background: #102b4e;
    border-left: 3px solid #35d5f2;
    border-radius: 5px 12px 12px 5px;
    padding: 13px 15px;
    color: #c7d9f1;
    font-size: 12px;
    line-height: 1.7;
}

.stButton > button {
    background: linear-gradient(100deg, #2476f4, #3199ff);
    color: white;
    border: 1px solid #4199ff;
    border-radius: 10px;
    min-height: 42px;
    font-weight: 600;
    transition: .2s ease;
}

.stButton > button:hover {
    background: #3a9bff;
    border-color: #69c4ff;
    transform: translateY(-1px);
    color: white;
}

.stTextInput input, .stTextArea textarea,
.stNumberInput input, .stSelectbox div[data-baseweb="select"] {
    background: #091a30;
    color: #edf4ff;
    border-color: #29496d;
    border-radius: 10px;
}

[data-testid="stFileUploader"] {
    background: #0a1b32;
    border: 1px dashed #315d88;
    border-radius: 14px;
    padding: 10px;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid #244263;
}

.stTabs [data-baseweb="tab"] {
    background: #102441;
    border-radius: 9px 9px 0 0;
    padding: 10px 16px;
}

.stProgress > div > div {
    background: #35c7f3;
}

hr {
    border-color: #1c3656;
}

.app-footer {
    border-top: 1px solid #1d3858;
    margin-top: 30px;
    padding-top: 15px;
    color: #819fc6;
    font-size: 11px;
    display: flex;
    justify-content: space-between;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

@media (max-width: 700px) {
    .hero {
        padding: 22px;
        min-height: 260px;
    }
    .hero-content {
        max-width: 100%;
    }
    .hero:after {
        right: 8px;
        top: 8px;
        font-size: 52px;
        opacity: .25;
    }
}
</style>
""", unsafe_allow_html=True)


def get_client():
    key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
    if not key:
        return None
    return Groq(api_key=key)


def ask_ai(prompt, system_prompt="You are Study Buddy AI, a helpful student study assistant. Explain clearly in simple English with useful headings."):
    client = get_client()
    if client is None:
        raise ValueError("Groq API key is missing. Add GROQ_API_KEY in Streamlit Secrets.")
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6
    )
    return response.choices[0].message.content


def init_state():
    defaults = {
        "page_choice": "Dashboard",
        "quiz_result": "",
        "notes_result": "",
        "chat_history": [],
        "quiz_count": 0,
        "notes_count": 0,
        "chat_count": 0,
        "last_topic": "",
        "last_quiz": "",
        "last_notes": ""
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def metric_card(icon, label, value, foot, color="#35d5f2"):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-top">
            <div class="metric-icon">{icon}</div>
            <span style="color:{color};font-size:12px;">●</span>
        </div>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-foot">{foot}</div>
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


init_state()

with st.sidebar:
    st.markdown("""
    <div class="brand">
        <div><span class="brand-icon">📘</span><span class="brand-name">Study Buddy <span>AI</span></span></div>
        <div class="brand-sub">INTELLIGENT LEARNING ASSISTANT</div>
    </div>
    """, unsafe_allow_html=True)

    pages = [
        "Dashboard",
        "AI Quiz",
        "PDF Notes",
        "Study Chat",
        "Performance",
        "Settings"
    ]

    current_page = st.radio(
        "NAVIGATION",
        pages,
        key="page_choice",
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="info-panel">
        <div style="font-size:25px;">🎯</div>
        <div style="font-weight:700;margin:8px 0;">Small steps. Big progress.</div>
        <div style="font-size:12px;color:#9eb4d4;line-height:1.6;">
        Learn something new every day and keep moving forward.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("STUDY • PRACTICE • GROW")
    st.caption("Study Buddy AI · Student Project")


if current_page == "Dashboard":
    st.markdown("""
    <div class="hero">
        <div class="hero-content">
            <div class="eyebrow">YOUR PERSONAL LEARNING SPACE</div>
            <h1>Make every study session <span>count.</span></h1>
            <p>Your study companion for smarter practice, clearer notes and better understanding. Everything you need to keep learning, in one place.</p>
            <div class="hero-note">✦ Learn at your pace · Practice with purpose</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section-heading">
        <h3>Your Learning Overview</h3>
        <span>Activity in this session</span>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("🧠", "Quiz Sets Generated", st.session_state.quiz_count, "AI practice sessions", "#7c8cff")
    with m2:
        metric_card("📄", "Notes Created", st.session_state.notes_count, "Study material summaries", "#35d5c1")
    with m3:
        metric_card("💬", "Chat Messages", st.session_state.chat_count, "Questions explored", "#ffad70")
    with m4:
        metric_card("📚", "Learning Tools", "3", "Quiz · Notes · Chat", "#35d5f2")

    st.markdown("""
    <div class="section-heading">
        <h3>Pick Up Your Learning</h3>
        <span>Choose a tool to get started</span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        feature_card("🧠", "AI Quiz Generator", "Create topic-based questions and practise important concepts before an exam.")
        if st.button("Create a Quiz  →", key="go_quiz", use_container_width=True):
            st.session_state.page_choice = "AI Quiz"
            st.rerun()
    with c2:
        feature_card("📄", "PDF Notes Maker", "Turn your PDF study material into clear, structured notes you can revise.")
        if st.button("Make Notes  →", key="go_notes", use_container_width=True):
            st.session_state.page_choice = "PDF Notes"
            st.rerun()
    with c3:
        feature_card("💬", "Study Chat", "Ask questions, explore difficult concepts and get step-by-step explanations.")
        if st.button("Open Study Chat  →", key="go_chat", use_container_width=True):
            st.session_state.page_choice = "Study Chat"
            st.rerun()

    left, right = st.columns([1.45, 1])
    with left:
        st.markdown('<div class="info-panel"><h3>✦ A Better Way to Study</h3><p style="color:#a9bfdc;line-height:1.8;font-size:13px;">Break a large topic into smaller parts. Practise with questions, make concise notes and ask for help whenever a concept feels confusing.</p><div class="tip">Study tip: Try explaining a concept in your own words after reading it. It can help you identify what you understand and what needs more practice.</div></div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="info-panel"><h3>⚡ Quick Study Plan</h3><p style="color:#b9cce6;font-size:13px;line-height:2;">01 &nbsp; Choose one topic to focus on<br>02 &nbsp; Review your notes<br>03 &nbsp; Test yourself with a quiz<br>04 &nbsp; Clear doubts in Study Chat</p></div>', unsafe_allow_html=True)

elif current_page == "AI Quiz":
    st.markdown('<div class="eyebrow">PRACTISE AND IMPROVE</div>', unsafe_allow_html=True)
    st.title("🧠 AI Quiz Generator")
    st.write("Create a customised practice quiz from any subject or topic.")

    with st.form("quiz_form"):
        topic = st.text_input("Topic or subject", placeholder="e.g. C programming, matrices, chemistry")
        col1, col2 = st.columns(2)
        with col1:
            number = st.selectbox("Number of questions", [5, 10, 15, 20, 25, 30], index=1)
        with col2:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"])
        question_type = st.selectbox(
            "Question format",
            ["Multiple choice with answers", "Short-answer questions with answers", "Mixed questions with answers"]
        )
        submitted = st.form_submit_button("Generate My Quiz  →", use_container_width=True)

    if submitted:
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            with st.spinner("Preparing your quiz..."):
                try:
                    prompt = f"""
Create {number} educational practice questions on: {topic}.
Difficulty: {difficulty}.
Format: {question_type}.
Use numbered questions and clear formatting.
For multiple-choice questions, give four options labelled A, B, C, D.
Provide the correct answer and a brief explanation for each question.
Keep the content accurate, student-friendly, and relevant to the topic.
Do not skip any question.
"""
                    result = ask_ai(prompt)
                    st.session_state.quiz_result = result
                    st.session_state.quiz_count += 1
                    st.session_state.last_topic = topic
                    st.session_state.last_quiz = result
                except Exception as e:
                    st.error(f"Could not generate the quiz: {e}")

    if st.session_state.quiz_result:
        st.markdown("---")
        st.subheader("Your Generated Quiz")
        st.markdown(st.session_state.quiz_result)
        st.download_button(
            "⬇ Download Quiz as TXT",
            data=st.session_state.quiz_result,
            file_name="study_buddy_quiz.txt",
            mime="text/plain",
            use_container_width=True
        )

elif current_page == "PDF Notes":
    st.markdown('<div class="eyebrow">READ LESS, UNDERSTAND MORE</div>', unsafe_allow_html=True)
    st.title("📄 PDF Notes Maker")
    st.write("Upload a text-based PDF and turn its content into organised study notes.")

    uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"])

    col1, col2 = st.columns(2)
    with col1:
        notes_style = st.selectbox(
            "Notes style",
            ["Detailed notes with headings", "Short revision notes", "Exam preparation notes", "Key points and definitions"]
        )
    with col2:
        notes_language = st.selectbox("Output language", ["Simple English", "Hindi", "Hinglish"])

    if st.button("Generate Study Notes  →", use_container_width=True):
        if uploaded_file is None:
            st.warning("Please upload a PDF file first.")
        else:
            try:
                with st.spinner("Reading your PDF and preparing notes..."):
                    reader = PdfReader(io.BytesIO(uploaded_file.getvalue()))
                    extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages)
                    extracted_text = extracted_text.strip()

                    if not extracted_text:
                        st.error("No readable text was found. This PDF may contain scanned images.")
                    else:
                        extracted_text = extracted_text[:24000]
                        prompt = f"""
Create {notes_style.lower()} in {notes_language} from the supplied study material.
Use a clear title, headings, bullet points, definitions, important facts and examples where useful.
Keep the notes faithful to the source. Do not invent details that are not supported by it.
Make the language easy for a student to revise.

STUDY MATERIAL:
{extracted_text}
"""
                        result = ask_ai(prompt)
                        st.session_state.notes_result = result
                        st.session_state.notes_count += 1
                        st.session_state.last_notes = result
            except Exception as e:
                st.error(f"Could not create notes: {e}")

    if st.session_state.notes_result:
        st.markdown("---")
        st.subheader("Your Study Notes")
        st.markdown(st.session_state.notes_result)
        st.download_button(
            "⬇ Download Notes as TXT",
            data=st.session_state.notes_result,
            file_name="study_buddy_notes.txt",
            mime="text/plain",
            use_container_width=True
        )

elif current_page == "Study Chat":
    st.markdown('<div class="eyebrow">YOUR PERSONAL STUDY COMPANION</div>', unsafe_allow_html=True)
    st.title("💬 Study Chat")
    st.write("Ask a question, get an explanation or work through a difficult concept.")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Ask your study question...")
    if user_prompt:
        st.session_state.chat_history.append({"role": "user", "content": user_prompt})
        st.session_state.chat_count += 1

        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking through your question..."):
                try:
                    client = get_client()
                    if client is None:
                        raise ValueError("Groq API key is missing. Add GROQ_API_KEY in Streamlit Secrets.")

                    messages = [{
                        "role": "system",
                        "content": "You are Study Buddy AI, a patient and helpful study assistant. Explain concepts in simple student-friendly language. Use steps, examples and headings when useful. If asked for code, provide complete beginner-friendly code."
                    }]
                    messages.extend(st.session_state.chat_history[-12:])

                    response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=messages,
                        temperature=0.6
                    )
                    answer = response.choices[0].message.content
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})
                except Exception as e:
                    error_text = f"Sorry, I couldn't answer that just now: {e}"
                    st.error(error_text)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_text})

    if st.session_state.chat_history:
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

elif current_page == "Performance":
    st.markdown('<div class="eyebrow">YOUR LEARNING ACTIVITY</div>', unsafe_allow_html=True)
    st.title("📈 Performance")
    st.write("A summary of the work you've done in the current session.")

    a, b, c = st.columns(3)
    with a:
        metric_card("🧠", "Quizzes Generated", st.session_state.quiz_count, "This session")
    with b:
        metric_card("📄", "Notes Created", st.session_state.notes_count, "This session")
    with c:
        metric_card("💬", "Chat Messages", st.session_state.chat_count, "Questions submitted")

    total = st.session_state.quiz_count + st.session_state.notes_count + st.session_state.chat_count
    st.markdown('<div class="section-heading"><h3>Activity Breakdown</h3><span>Session totals</span></div>', unsafe_allow_html=True)

    activity = {
        "AI Quiz": st.session_state.quiz_count,
        "PDF Notes": st.session_state.notes_count,
        "Study Chat": st.session_state.chat_count
    }

    if total == 0:
        st.info("Your activity will appear here after you use the study tools.")
    else:
        st.bar_chart(activity)
        for label, count in activity.items():
            share = count / total
            st.write(f"**{label}** — {count} activities")
            st.progress(share)

    st.markdown('<div class="tip">Note: These statistics are stored in the current Streamlit session. They are not a permanent record and may reset when the app session restarts.</div>', unsafe_allow_html=True)

elif current_page == "Settings":
    st.markdown('<div class="eyebrow">MAKE IT WORK FOR YOU</div>', unsafe_allow_html=True)
    st.title("⚙️ Settings")
    st.write("Check your app configuration and manage your current session.")

    api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
    status_col, detail_col = st.columns([1, 2])

    with status_col:
        st.markdown('<div class="info-panel"><div style="font-size:28px;">🔐</div><h3>API Connection</h3>', unsafe_allow_html=True)
        if api_key:
            st.success("API key configured")
        else:
            st.warning("API key not found")
        st.markdown("</div>", unsafe_allow_html=True)

    with detail_col:
        st.markdown('<div class="info-panel"><h3>Groq AI Configuration</h3><p style="color:#a9bfdc;line-height:1.8;font-size:13px;">The app uses Groq to generate quiz questions, summarise PDF notes and answer study questions. Keep your API key private and store it in Streamlit Secrets.</p></div>', unsafe_allow_html=True)

    st.subheader("App Information")
    st.write("**Application:** Study Buddy AI")
    st.write("**Purpose:** Intelligent Learning Assistant")
    st.write("**AI model:** `openai/gpt-oss-20b`")
    st.write("**Tools:** AI Quiz, PDF Notes, Study Chat")

    st.markdown("---")
    st.subheader("Session Management")
    st.write("Reset your activity counts, generated content and chat history for this session.")
    confirm_reset = st.checkbox("I want to reset my current session data.")

    if st.button("Reset Session Data", use_container_width=True):
        if confirm_reset:
            for key in [
                "quiz_result", "notes_result", "chat_history",
                "quiz_count", "notes_count", "chat_count",
                "last_topic", "last_quiz", "last_notes"
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("Session data reset.")
            st.rerun()
        else:
            st.warning("Please tick the confirmation box before resetting.")

st.markdown("""
<div class="app-footer">
    <span>Study Buddy AI · Intelligent Learning Assistant</span>
    <span>Learn · Practise · Grow</span>
</div>
""", unsafe_allow_html=True)
