import streamlit as st
from groq import Groq
from pypdf import PdfReader
from io import BytesIO
from datetime import datetime
import random
import re

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root { color-scheme: dark; }
.stApp {
    background:
      radial-gradient(ellipse at 12% 0%, rgba(92,78,180,.16), transparent 34%),
      radial-gradient(ellipse at 90% 8%, rgba(42,164,180,.09), transparent 28%),
    color: #eef2ff;
    font-family: 'DM Sans', sans-serif;
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding: 1.5rem 2.4rem 3rem; max-width: 1500px; }
[data-testid="stSidebar"] {
    background: #0d1426;
    border-right: 1px solid #202b43;
}
[data-testid="stSidebar"] .block-container { padding: 1.5rem 1rem; }
h1,h2,h3 { font-family: 'Manrope', sans-serif !important; letter-spacing: -.5px; }
p, label, .stMarkdown { color: #dce4f8; }
.brand { display:flex; align-items:center; gap:12px; padding:4px 0 24px; }
.brand-icon {
    display:flex; align-items:center; justify-content:center;
    width:46px; height:46px; border-radius:15px;
    background:linear-gradient(135deg,#9b8aff,#6356e8 55%,#36c9d0);
    color:white; font-size:24px; font-weight:800;
    box-shadow:0 8px 26px rgba(111,94,249,.25);
}
.brand-name { color:#f5f7ff; font-family:'Manrope',sans-serif; font-size:21px; font-weight:800; line-height:1.1; }
.brand-name span { color:#a99aff; }
.brand-sub { color:#8291b2; font-size:9px; letter-spacing:2px; margin-top:6px; }
.side-caption { color:#7382a4; font-size:10px; font-weight:700; letter-spacing:1.8px; padding:8px 0 10px; }
.eyebrow { color:#a99aff; text-transform:uppercase; font-size:10px; font-weight:700; letter-spacing:2px; }
.hero {
    border:1px solid #30345d; border-radius:24px; padding:30px;
    background:linear-gradient(120deg,rgba(76,65,149,.35),rgba(23,39,66,.82) 58%,rgba(20,72,83,.36));
    margin: 8px 0 22px;
}
.hero h1 { font-size:clamp(28px,4vw,43px); line-height:1.12; margin:10px 0 12px; color:#f6f7ff; }
.hero p { color:#b8c4df; max-width:650px; font-size:15px; line-height:1.7; }
.hero-pill { display:inline-block; border:1px solid #514a88; color:#d7d0ff; background:#29254d; border-radius:30px; padding:6px 11px; font-size:11px; }
.panel {
    background:linear-gradient(145deg,#141d32,#11192b);
    border:1px solid #26334e; border-radius:19px; padding:20px;
}
.panel-title { color:#f1f4ff; font-size:16px; font-weight:700; margin-bottom:5px; }
.panel-note { color:#8e9dbc; font-size:12px; line-height:1.6; }
.metric {
    background:linear-gradient(145deg,#151f36,#11192a);
    border:1px solid #26334d; border-radius:17px; padding:18px 19px;
}
.metric-label { color:#91a0bf; font-size:12px; }
.metric-value { color:#f4f6ff; font-family:'Manrope',sans-serif; font-size:29px; font-weight:800; margin:7px 0 2px; }
.metric-foot { color:#7c8eaf; font-size:11px; }
.section-heading { font-family:'Manrope',sans-serif; font-size:23px; font-weight:800; color:#f3f5ff; margin:8px 0 4px; }
.section-sub { color:#93a1be; font-size:13px; margin-bottom:18px; }
div.stButton > button {
    border-radius:11px; border:1px solid #344362; font-weight:600;
    min-height:43px; transition:all .15s ease;
}
div.stButton > button[kind="primary"] {
    background:linear-gradient(110deg,#7566f2,#6356d9);
    border:1px solid #8a7dff; color:white;
}
div.stButton > button[kind="secondary"] {
    background:#141d31; color:#dce5ff;
}
div.stButton > button:hover { border-color:#9b8cff; color:white; }
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background:#10182a !important; color:#f1f4ff !important; border-color:#33415f !important;
    border-radius:10px !important;
}
[data-testid="stFileUploader"] {
    background:#111a2d; border:1px dashed #465578; border-radius:14px; padding:8px;
}
hr { border-color:#27334d !important; }
footer { visibility:hidden; }
.small-muted { color:#8493b2; font-size:11px; }
.tag { display:inline-block; padding:5px 9px; border-radius:8px; background:#242449; color:#cfc8ff; font-size:10px; }
</style>
""", unsafe_allow_html=True)

defaults = {
    "page": "Dashboard",
    "quiz_data": None,
    "quiz_answers": {},
    "quiz_submitted": False,
    "chat_history": [],
    "pdf_text": "",
    "pdf_name": "",
    "notes": "",
    "topics_done": 0,
    "quiz_count": 0,
    "correct_count": 0,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

def go(page):
    st.session_state.page = page
    st.rerun()

def safe_text(value):
    return re.sub(r"[<>]", "", str(value))

def get_client():
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        api_key = ""
    if not api_key:
        st.warning("AI features ke liye Streamlit Secrets mein GROQ_API_KEY add karna hoga.")
        return None
    return Groq(api_key=api_key)

def ask_ai(prompt, system="You are a helpful study tutor. Explain concepts in clear, natural, student-friendly language. Be accurate, use examples when useful, and never claim that the answer is written by a human."):
    client = get_client()
    if client is None:
        return None
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=1800,
        )
        return response.choices[0].message.content
    except Exception as exc:
        st.error(f"AI request nahi chal payi: {exc}")
        return None

def panel_start(title, subtitle=""):
    st.markdown(f"<div class='panel-title'>{title}</div><div class='panel-note'>{subtitle}</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div class="brand">
      <div class="brand-icon">✦</div>
      <div>
        <div class="brand-name">Study Buddy <span>AI</span></div>
        <div class="brand-sub">YOUR PERSONAL LEARNING SPACE</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='side-caption'>YOUR WORKSPACE</div>", unsafe_allow_html=True)
    nav_items = [
        ("🏠", "Dashboard"),
        ("🧠", "AI Quiz"),
        ("📚", "PDF Notes"),
        ("💬", "AI Study Chat"),
        ("📊", "Performance"),
        ("⚙️", "Settings"),
    ]
    for symbol, name in nav_items:
        if st.button(
            f"{symbol}   {name}",
            key=f"nav_{name}",
            use_container_width=True,
            type="primary" if st.session_state.page == name else "secondary",
        ):
            go(name)
    st.markdown("---")
    st.markdown("<div class='panel-note'>Made for focused learning, one topic at a time.</div>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>STUDY BUDDY AI · STUDENT PROJECT</div>", unsafe_allow_html=True)

st.markdown("""
<div class="brand" style="border-bottom:1px solid #26334e;margin-bottom:18px;padding-bottom:18px">
  <div class="brand-icon">✦</div>
  <div>
    <div class="brand-name" style="font-size:25px">Study Buddy <span>AI</span></div>
    <div class="brand-sub">LEARN SMARTER. BUILD CONFIDENCE.</div>
  </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.page == "Dashboard":
    st.markdown("""
    <div class="hero">
      <span class="hero-pill">✦ YOUR STUDY SPACE</span>
      <h1>Small steps. Strong concepts.<br>Better learning.</h1>
      <p>A simple place to practise topics, turn your notes into revision material, and ask questions when you get stuck. Pick a tool and get started.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric'><div class='metric-label'>Quizzes attempted</div><div class='metric-value'>{st.session_state.quiz_count}</div><div class='metric-foot'>Your practice sessions</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric'><div class='metric-label'>Correct answers</div><div class='metric-value'>{st.session_state.correct_count}</div><div class='metric-foot'>Across submitted quizzes</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric'><div class='metric-label'>Study chats</div><div class='metric-value'>{len(st.session_state.chat_history)}</div><div class='metric-foot'>Questions and replies</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric'><div class='metric-label'>PDF loaded</div><div class='metric-value'>{'Yes' if st.session_state.pdf_text else 'No'}</div><div class='metric-foot'>{safe_text(st.session_state.pdf_name) if st.session_state.pdf_name else 'Upload notes to begin'}</div></div>", unsafe_allow_html=True)

    st.markdown("<div class='section-heading'>Choose your next step</div><div class='section-sub'>Tools to help you understand, practise and revise.</div>", unsafe_allow_html=True)
    a, b, c = st.columns(3)
    with a:
        st.markdown("<div class='panel'><div style='font-size:25px'>🧠</div><div class='panel-title'>AI Quiz</div><div class='panel-note'>Create practice questions for any topic and check your understanding.</div></div>", unsafe_allow_html=True)
        if st.button("Start a quiz →", key="dash_quiz", use_container_width=True): go("AI Quiz")
    with b:
        st.markdown("<div class='panel'><div style='font-size:25px'>📚</div><div class='panel-title'>PDF Notes</div><div class='panel-note'>Upload class notes and ask for summaries, key points or revision questions.</div></div>", unsafe_allow_html=True)
        if st.button("Open my notes →", key="dash_pdf", use_container_width=True): go("PDF Notes")
    with c:
        st.markdown("<div class='panel'><div style='font-size:25px'>💬</div><div class='panel-title'>Study Chat</div><div class='panel-note'>Ask a question and get a clear explanation with examples.</div></div>", unsafe_allow_html=True)
        if st.button("Ask a question →", key="dash_chat", use_container_width=True): go("AI Study Chat")

    st.markdown("<div class='section-heading'>A useful study routine</div>", unsafe_allow_html=True)
    r1, r2, r3 = st.columns(3)
    with r1:
        st.markdown("<div class='panel'><span class='tag'>01 · UNDERSTAND</span><div class='panel-title' style='margin-top:12px'>Learn one concept</div><div class='panel-note'>Ask for a simple explanation before moving to the next topic.</div></div>", unsafe_allow_html=True)
    with r2:
        st.markdown("<div class='panel'><span class='tag'>02 · PRACTISE</span><div class='panel-title' style='margin-top:12px'>Test your knowledge</div><div class='panel-note'>Use short quizzes to find what needs more revision.</div></div>", unsafe_allow_html=True)
    with r3:
        st.markdown("<div class='panel'><span class='tag'>03 · REVISE</span><div class='panel-title' style='margin-top:12px'>Return to key points</div><div class='panel-note'>Use your notes to revisit important definitions and examples.</div></div>", unsafe_allow_html=True)

elif st.session_state.page == "AI Quiz":
    st.markdown("<div class='eyebrow'>PRACTICE ROOM</div><div class='section-heading'>AI Quiz</div><div class='section-sub'>Generate a practice quiz around the topic you are learning.</div>", unsafe_allow_html=True)
    with st.container(border=True):
        topic = st.text_input("Topic", placeholder="e.g. C loops, matrices, semiconductor basics")
        col1, col2 = st.columns(2)
        with col1:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
        with col2:
            number = st.selectbox("Number of questions", [5, 10, 15])
        if st.button("Generate quiz", type="primary", use_container_width=True):
            if not topic.strip():
                st.warning("Pehle topic likho.")
            else:
                with st.spinner("Quiz taiyar ho raha hai..."):
                    prompt = f"""Create exactly {number} multiple-choice questions about {topic}. Difficulty: {difficulty}.
Return ONLY valid JSON as an array. Each object must have keys: question, options (array of exactly 4 strings), answer (exact option string), explanation (short).
Do not use markdown fences. Make questions accurate and varied."""
                    raw = ask_ai(prompt, "You create accurate educational multiple-choice quizzes. Return valid JSON only.")
                    if raw:
                        import json
                        try:
                            cleaned = raw.strip().replace("```json", "").replace("```", "").strip()
                            start, end = cleaned.find("["), cleaned.rfind("]")
                            quiz = json.loads(cleaned[start:end+1])
                            if not quiz:
                                raise ValueError("Empty quiz")
                            st.session_state.quiz_data = quiz
                            st.session_state.quiz_answers = {}
                            st.session_state.quiz_submitted = False
                        except Exception:
                            st.error("Quiz format sahi nahi aaya. Ek baar phir Generate quiz dabao.")
    if st.session_state.quiz_data:
        st.markdown("---")
        st.markdown("### Your questions")
        with st.form("quiz_form"):
            for i, q in enumerate(st.session_state.quiz_data):
                st.markdown(f"**Q{i+1}. {q.get('question','')}**")
                st.radio("Choose one", q.get("options", []), key=f"quiz_answer_{i}", index=None, label_visibility="collapsed")
            submitted = st.form_submit_button("Submit answers", type="primary", use_container_width=True)
        if submitted:
            score = 0
            for i, q in enumerate(st.session_state.quiz_data):
                answer = st.session_state.get(f"quiz_answer_{i}")
                st.session_state.quiz_answers[i] = answer
                if answer == q.get("answer"):
                    score += 1
            st.session_state.quiz_submitted = True
            st.session_state.quiz_count += 1
            st.session_state.correct_count += score
            st.session_state.last_score = score
        if st.session_state.quiz_submitted:
            score = getattr(st.session_state, "last_score", 0)
            st.success(f"Your score: {score} / {len(st.session_state.quiz_data)}")
            for i, q in enumerate(st.session_state.quiz_data):
                user_ans = st.session_state.quiz_answers.get(i)
                correct = q.get("answer")
                st.markdown(f"**Q{i+1}. {q.get('question','')}**")
                st.write(f"Your answer: {user_ans or 'Not answered'}")
                st.write(f"Correct answer: {correct}")
                st.caption(q.get("explanation", ""))

elif st.session_state.page == "PDF Notes":
    st.markdown("<div class='eyebrow'>YOUR MATERIAL</div><div class='section-heading'>PDF Notes</div><div class='section-sub'>Upload a PDF and turn its text into a practical revision companion.</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Choose a PDF file", type=["pdf"])
    if uploaded is not None:
        if uploaded.name != st.session_state.pdf_name:
            try:
                reader = PdfReader(BytesIO(uploaded.getvalue()))
                text_content = "\n".join(page.extract_text() or "" for page in reader.pages)
                st.session_state.pdf_text = text_content[:60000]
                st.session_state.pdf_name = uploaded.name
                st.success(f"Loaded {uploaded.name} ({len(reader.pages)} pages)")
            except Exception as exc:
                st.error(f"PDF read nahi ho payi: {exc}")
    if st.session_state.pdf_text:
        st.markdown(f"<div class='panel'><div class='panel-title'>📄 {safe_text(st.session_state.pdf_name)}</div><div class='panel-note'>Text extracted: {len(st.session_state.pdf_text)} characters</div></div>", unsafe_allow_html=True)
        task = st.selectbox("What would you like to make?", ["Simple summary", "Important exam points", "Short revision notes", "Practice questions", "Explain in simple English"])
        if st.button("Prepare from PDF", type="primary", use_container_width=True):
            with st.spinner("Your study material is being prepared..."):
                prompts = {
                    "Simple summary": "Summarise this material using clear headings and simple English.",
                    "Important exam points": "List the most important exam points and definitions from this material.",
                    "Short revision notes": "Create concise revision notes with headings, bullets and key formulas where present.",
                    "Practice questions": "Create 10 useful practice questions with short answers based only on this material.",
                    "Explain in simple English": "Explain the material in simple student-friendly English with examples where useful.",
                }
                result = ask_ai(prompts[task] + "\n\nMATERIAL:\n" + st.session_state.pdf_text)
                if result:
                    st.session_state.notes = result
        if st.session_state.notes:
            st.markdown("---")
            st.markdown("### Your study material")
            st.markdown(st.session_state.notes)
            st.download_button("Download notes as TXT", st.session_state.notes, file_name="study_notes.txt", mime="text/plain", use_container_width=True)
    else:
        st.info("Upload a text-based PDF to get started. Scanned image-only PDFs may not extract text.")

elif st.session_state.page == "AI Study Chat":
    st.markdown("<div class='eyebrow'>ASK WITHOUT HESITATION</div><div class='section-heading'>AI Study Chat</div><div class='section-sub'>Ask about a concept, a program, a formula or an exam question.</div>", unsafe_allow_html=True)
    style = st.selectbox("Explanation style", ["Simple English", "Hinglish", "Step by step", "Exam-ready answer"])
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    prompt = st.chat_input("Type your study question...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        system = f"""You are Study Buddy AI, a study assistant for students. Answer in {style}.
Use natural, clear, student-friendly wording. Avoid unnecessary jargon. For programming, show complete beginner-friendly code and explain it.
For exam answers, use suitable headings. Do not claim to be a human or help misrepresent authorship; instead, make explanations easy for the student to understand and rewrite in their own words."""
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = ask_ai(prompt, system)
            if response:
                st.markdown(response)
                st.session_state.chat_history.append({"role": "assistant", "content": response})
    if st.button("Clear chat", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()

elif st.session_state.page == "Performance":
    st.markdown("<div class='eyebrow'>YOUR PROGRESS</div><div class='section-heading'>Performance</div><div class='section-sub'>A quick view of the practice you have completed in this session.</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='metric'><div class='metric-label'>Quizzes attempted</div><div class='metric-value'>{st.session_state.quiz_count}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric'><div class='metric-label'>Correct answers</div><div class='metric-value'>{st.session_state.correct_count}</div></div>", unsafe_allow_html=True)
    with c3:
        total_possible = sum(len(q) for q in [])  # session-only metrics; no fake historical data
        st.markdown(f"<div class='metric'><div class='metric-label'>Chat messages</div><div class='metric-value'>{len(st.session_state.chat_history)}</div></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Keep improving")
    st.write("Try one short quiz, review the explanations, and revisit any topic that felt difficult.")
    st.caption("Progress is currently kept in this app session. It may reset when the app restarts.")

elif st.session_state.page == "Settings":
    st.markdown("<div class='eyebrow'>APP PREFERENCES</div><div class='section-heading'>Settings</div><div class='section-sub'>Basic information about your Study Buddy AI setup.</div>", unsafe_allow_html=True)
    st.markdown("<div class='panel'><div class='panel-title'>About this project</div><div class='panel-note'>Study Buddy AI is a student-built learning assistant for practice quizzes, PDF revision notes and study questions.</div></div>", unsafe_allow_html=True)
    st.markdown("#### AI connection")
    st.write("The app uses a Groq API key stored in Streamlit Secrets. Keep the key private and never commit it to GitHub.")
    if st.button("Check AI connection", type="primary"):
        client = get_client()
        if client:
            try:
                models = client.models.list()
                st.success("API key connection looks good.")
            except Exception as exc:
                st.error(f"Connection check failed: {exc}")
    st.markdown("#### Reset this session")
    if st.button("Reset quiz and chat data"):
        for key in ["quiz_data", "quiz_answers", "quiz_submitted", "chat_history", "pdf_text", "pdf_name", "notes", "quiz_count", "correct_count"]:
            st.session_state[key] = defaults.get(key, None)
        st.rerun()

st.markdown("<div style='text-align:center;color:#667594;font-size:11px;padding:32px 0 4px'>STUDY BUDDY AI · MADE FOR LEARNING</div>", unsafe_allow_html=True)
