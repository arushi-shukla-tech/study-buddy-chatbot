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
    page_title="Study Buddy AI | Learning Workspace",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

MODEL = "openai/gpt-oss-20b"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {
    --green:#087F5B; --deep:#103B30; --dark:#092B24;
    --mint:#DDF3E7; --bg:#F5F7F4; --white:#FFFFFF;
    --ink:#172E26; --muted:#75847B; --line:#E1E8E1;
}
html,body,[class*="css"] {font-family:'DM Sans',sans-serif;}
.stApp {background:var(--bg);color:var(--ink);}
#MainMenu,footer {visibility:hidden;}
header[data-testid="stHeader"] {background:transparent;}
.block-container {max-width:1450px;padding:1.5rem 2.2rem 3rem;}
h1,h2,h3 {font-family:'Manrope',sans-serif!important;color:var(--ink);letter-spacing:-1px;}
p {line-height:1.75;}
hr {border-color:var(--line);}
section[data-testid="stSidebar"] {background:linear-gradient(180deg,#103B30 0%,#092B24 100%);border-right:1px solid #23483C;}
section[data-testid="stSidebar"] * {color:#E9F4ED;}
section[data-testid="stSidebar"] [data-testid="stRadio"] label {padding:7px 5px;font-size:14px;}
section[data-testid="stSidebar"] [data-testid="stRadio"] label p {font-weight:500;}
section[data-testid="stSidebar"] hr {border-color:#315348;}
.sb-brand {padding:14px 4px 23px;}
.sb-logo {display:flex;align-items:center;justify-content:center;width:52px;height:52px;border-radius:17px;background:linear-gradient(135deg,#19B889,#087F5B);color:white;font:800 25px 'Manrope',sans-serif;box-shadow:0 8px 25px #00000025;margin-bottom:16px;}
.sb-brand-name {font:800 22px 'Manrope',sans-serif;letter-spacing:-.8px;color:#fff;}
.sb-brand-caption {font-size:9px;letter-spacing:2px;color:#A9C8B7;margin-top:6px;}
.sb-side-note {background:#FFFFFF0D;border:1px solid #FFFFFF19;border-radius:15px;padding:16px;margin-top:20px;font-size:12px;line-height:1.8;color:#D4E6DC;}
div.stButton>button,div.stDownloadButton>button {min-height:44px;border-radius:11px;border:1px solid var(--line);font-weight:700;transition:.2s ease;}
div.stButton>button {background:white;color:var(--ink);}
div.stButton>button:hover,div.stDownloadButton>button:hover {border-color:var(--green);color:var(--green);}
div.stButton>button[kind="primary"] {background:var(--green);border-color:var(--green);color:white;}
div.stButton>button[kind="primary"]:hover {background:var(--deep);color:white;}
.stTextInput input,.stTextArea textarea,.stNumberInput input {border-radius:10px!important;}
[data-testid="stFileUploader"] {background:white;border:1px dashed #9BC9AE;border-radius:14px;padding:12px;}
[data-testid="stMetric"] {background:white;border:1px solid var(--line);border-radius:15px;padding:17px;}
[data-testid="stMetricValue"] {color:var(--green);font-family:'Manrope',sans-serif;font-weight:800;}
[data-testid="stChatMessage"] {background:white;border:1px solid var(--line);border-radius:14px;}
.sb-topbar {display:flex;align-items:center;justify-content:space-between;gap:12px;padding:2px 0 17px;margin-bottom:22px;border-bottom:1px solid var(--line);}
.sb-top-title {font:800 18px 'Manrope',sans-serif;letter-spacing:-.5px;}
.sb-top-caption {color:var(--muted);font-size:11px;margin-top:3px;}
.sb-pill {display:inline-block;color:var(--green);background:#E6F4E9;border:1px solid #CDE7D3;border-radius:30px;padding:8px 12px;font-size:10px;font-weight:700;letter-spacing:.5px;white-space:nowrap;}
.sb-hero {position:relative;overflow:hidden;background:linear-gradient(125deg,#103B30 0%,#087F5B 75%,#15966C 100%);border-radius:23px;padding:36px;color:white;min-height:300px;box-shadow:0 14px 35px #103B3017;}
.sb-hero:after {content:"";position:absolute;width:290px;height:290px;border-radius:50%;border:1px solid #FFFFFF2D;right:-90px;top:-155px;box-shadow:0 0 0 35px #FFFFFF08,0 0 0 75px #FFFFFF06;}
.sb-kicker {position:relative;z-index:1;font-size:10px;font-weight:700;letter-spacing:2px;color:#C5F0D4;}
.sb-hero h1 {position:relative;z-index:1;color:white!important;font-size:clamp(34px,4.2vw,57px);line-height:1.12;letter-spacing:-2.6px;margin:23px 0 15px;}
.sb-hero h1 span {color:#C6F0A9;}
.sb-hero-copy {position:relative;z-index:1;max-width:570px;color:#E0F1E8;font-size:13px;line-height:1.9;}
.sb-section {margin:31px 0 15px;}
.sb-eyebrow {font-size:10px;font-weight:800;letter-spacing:1.8px;color:var(--green);}
.sb-section-title {font:800 25px 'Manrope',sans-serif;letter-spacing:-1.1px;margin-top:5px;}
.sb-muted {color:var(--muted);font-size:12px;line-height:1.8;margin-top:5px;}
.sb-stat {background:white;border:1px solid var(--line);border-radius:16px;padding:19px;min-height:139px;}
.sb-stat-icon {color:var(--green);background:var(--mint);width:36px;height:36px;display:flex;align-items:center;justify-content:center;border-radius:11px;font-size:18px;}
.sb-stat-number {font:800 32px 'Manrope',sans-serif;letter-spacing:-1.5px;color:var(--ink);margin-top:13px;}
.sb-stat-label {color:var(--muted);font-size:11px;margin-top:3px;}
.sb-feature {background:white;border:1px solid var(--line);border-radius:17px;padding:21px;min-height:170px;margin-bottom:8px;}
.sb-feature-icon {width:42px;height:42px;border-radius:13px;background:#E5F5E9;display:flex;align-items:center;justify-content:center;font-size:21px;margin-bottom:15px;}
.sb-feature-title {font:800 18px 'Manrope',sans-serif;letter-spacing:-.6px;}
.sb-feature-copy {color:var(--muted);font-size:12px;line-height:1.8;margin-top:7px;}
.sb-panel {background:white;border:1px solid var(--line);border-radius:16px;padding:21px;margin-bottom:15px;}
.sb-panel-label {font-size:10px;font-weight:800;color:var(--green);letter-spacing:1.5px;}
.sb-panel-title {font:800 21px 'Manrope',sans-serif;letter-spacing:-.7px;margin:8px 0;}
.sb-quote {background:#E5F3E8;border-radius:17px;padding:23px;color:var(--deep);margin-bottom:15px;}
.sb-quote-title {font:800 22px/1.4 'Manrope',sans-serif;letter-spacing:-.7px;margin:12px 0;}
.sb-footer {display:flex;justify-content:space-between;gap:12px;border-top:1px solid var(--line);margin-top:30px;padding-top:17px;color:#849188;font-size:9px;letter-spacing:1px;}
@media(max-width:700px) {
 .block-container {padding:.8rem .9rem 2rem;}
 .sb-hero {padding:25px 21px;min-height:265px;border-radius:19px;}
 .sb-hero h1 {font-size:36px;letter-spacing:-1.8px;}
 .sb-hero-copy {font-size:12px;}
 .sb-top-title {font-size:16px;}
 .sb-pill {font-size:8px;padding:7px 8px;}
 .sb-section-title {font-size:22px;}
 .sb-stat {padding:12px;min-height:120px;}
 .sb-stat-number {font-size:27px;}
 .sb-stat-label {font-size:10px;}
 .sb-feature {padding:16px;min-height:160px;}
 .sb-feature-title {font-size:16px;}
 .sb-footer {flex-direction:column;}
}
</style>
""", unsafe_allow_html=True)

defaults = {
    "page":"Dashboard","chat":[],"quiz_history":[],"notes_history":[],
    "last_quiz":"","last_notes":"","quiz_topic":"","notes_title":"",
    "pdf_text":"","activity":"Your learning journey starts here"
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

PAGES = ["Dashboard","AI Quiz","PDF Notes","Study Chat","Performance","Settings"]

def get_client():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        key = ""
    return Groq(api_key=key) if key else None

def ask_ai(prompt="", max_tokens=3000, messages=None):
    client = get_client()
    if client is None:
        st.error("GROQ_API_KEY is missing. Open Streamlit Cloud → App settings → Secrets and add it privately.")
        return None

    if messages is None:
        messages = [{"role":"user","content":prompt}]

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.35,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception:
        st.error("The AI request failed. Check your Groq API key, model access and connection.")
        return None

def page_header(number, title, description):
    st.markdown(f"""
    <div style="padding:5px 0 21px;border-bottom:1px solid #E1E8E1;margin-bottom:23px">
      <div class="sb-eyebrow">STUDY BUDDY AI / {escape(number)}</div>
      <div class="sb-section-title" style="font-size:clamp(27px,4vw,39px);margin-top:8px">{escape(title)}</div>
      <div class="sb-muted">{escape(description)}</div>
    </div>""", unsafe_allow_html=True)

def section(label, title, description=""):
    desc = f'<div class="sb-muted">{escape(description)}</div>' if description else ""
    st.markdown(f"""
    <div class="sb-section">
      <div class="sb-eyebrow">{escape(label)}</div>
      <div class="sb-section-title">{escape(title)}</div>
      {desc}
    </div>""", unsafe_allow_html=True)

def panel(label, title, description):
    st.markdown(f"""
    <div class="sb-panel">
      <div class="sb-panel-label">{escape(label)}</div>
      <div class="sb-panel-title">{escape(title)}</div>
      <div class="sb-muted">{escape(description)}</div>
    </div>""", unsafe_allow_html=True)

def make_pdf(content, title="Study Buddy AI Notes"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "StudyBuddyTitle",
        parent=styles["Title"],
        textColor=colors.HexColor("#087F5B"),
        fontSize=22,
        leading=28,
        spaceAfter=18
    )
    body_style = ParagraphStyle(
        "StudyBuddyBody",
        parent=styles["BodyText"],
        fontSize=10,
        leading=16,
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
            story.append(Paragraph(escape(line.lstrip("#").strip()), styles["Heading2"]))
        elif line.startswith(("- ", "* ", "• ")):
            story.append(Paragraph("&#8226; " + escape(line[2:].strip()), body_style))
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
      <div class="sb-brand-caption">YOUR LEARNING SPACE</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.caption("WORKSPACE MENU")
    selected_page = st.radio(
        "Navigate",
        PAGES,
        index=PAGES.index(st.session_state.page),
        label_visibility="collapsed",
        key="sidebar_navigation"
    )
    st.session_state.page = selected_page
    st.markdown("---")

    st.markdown("""
    <div class="sb-side-note">
      <strong>✦ YOUR AI STUDY PARTNER</strong><br><br>
      Create practice quizzes, organise study notes and understand difficult concepts one step at a time.
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("POWERED BY GROQ AI")
    st.caption("LEARN · PRACTISE · GROW")

st.markdown("""
<div class="sb-topbar">
  <div>
    <div class="sb-top-title">Study Buddy AI</div>
    <div class="sb-top-caption">Your personal learning workspace</div>
  </div>
  <div class="sb-pill">✦ AI WORKSPACE</div>
</div>""", unsafe_allow_html=True)

def dashboard():
    st.markdown("""
    <div class="sb-hero">
      <div class="sb-kicker">YOUR PERSONAL AI STUDY SPACE</div>
      <h1>Study smarter.<br><span>Achieve more.</span></h1>
      <div class="sb-hero-copy">
        Your all-in-one workspace for practice quizzes, clear study notes and personalised doubt solving. Make every study session count.
      </div>
    </div>""", unsafe_allow_html=True)

    quiz_count = len(st.session_state.quiz_history)
    notes_count = len(st.session_state.notes_history)
    chat_count = sum(1 for m in st.session_state.chat if m["role"] == "user")

    section("YOUR WORKSPACE / 01", "Study overview", "A snapshot of your activity in this session.")

    cols = st.columns(3)
    stats = [
        ("✳", quiz_count, "QUIZ SETS", "Practice sets created"),
        ("▤", notes_count, "NOTES CREATED", "Revision resources"),
        ("◉", chat_count, "QUESTIONS ASKED", "Tutor conversations")
    ]

    for col, item in zip(cols, stats):
        icon, value, label, caption = item
        with col:
            st.markdown(f"""
            <div class="sb-stat">
              <div class="sb-stat-icon">{icon}</div>
              <div class="sb-stat-number">{value}</div>
              <div class="sb-stat-label">{label}</div>
              <div class="sb-muted">{caption}</div>
            </div>""", unsafe_allow_html=True)

    section("YOUR TOOLKIT / 02", "Everything you need to learn", "Choose a workspace and get started.")

    a, b = st.columns(2)

    with a:
        st.markdown("""
        <div class="sb-feature">
          <div class="sb-feature-icon">✳</div>
          <div class="sb-feature-title">AI Quiz Lab</div>
          <div class="sb-feature-copy">Generate topic-based practice questions with answers and explanations to test your understanding.</div>
        </div>""", unsafe_allow_html=True)

        if st.button("Explore AI Quiz →", key="dash_quiz", type="primary", use_container_width=True):
            st.session_state.page = "AI Quiz"
            st.rerun()

    with b:
        st.markdown("""
        <div class="sb-feature">
          <div class="sb-feature-icon">▤</div>
          <div class="sb-feature-title">Notes Studio</div>
          <div class="sb-feature-copy">Transform readable PDFs into organised revision notes and export your study material.</div>
        </div>""", unsafe_allow_html=True)

        if st.button("Create study notes →", key="dash_notes", use_container_width=True):
            st.session_state.page = "PDF Notes"
            st.rerun()

    a, b = st.columns(2)

    with a:
        st.markdown("""
        <div class="sb-feature">
          <div class="sb-feature-icon">◉</div>
          <div class="sb-feature-title">Personal AI Tutor</div>
          <div class="sb-feature-copy">Ask doubts, explore examples and get step-by-step explanations in clear language.</div>
        </div>""", unsafe_allow_html=True)

        if st.button("Ask a question →", key="dash_chat", use_container_width=True):
            st.session_state.page = "Study Chat"
            st.rerun()

    with b:
        st.markdown("""
        <div class="sb-feature">
          <div class="sb-feature-icon">↗</div>
          <div class="sb-feature-title">Progress Centre</div>
          <div class="sb-feature-copy">Review your quiz sets, notes and recent study activity from this session.</div>
        </div>""", unsafe_allow_html=True)

        if st.button("View my progress →", key="dash_progress", use_container_width=True):
            st.session_state.page = "Performance"
            st.rerun()

    section("RECENT ACTIVITY / 03", "Your learning trail")
    panel("LATEST UPDATE", "Keep moving forward", st.session_state.activity)


def ai_quiz():
    page_header("01 / PRACTISE", "AI Quiz Lab", "Build a personalised practice set for your next study session.")

    a, b = st.columns([1.25, 0.75])

    with a:
        panel("QUIZ BUILDER", "Configure your practice", "Choose your topic, difficulty and preferred question style.")

        topic = st.text_input(
            "Subject or topic",
            placeholder="e.g. BJT, recursion, electrochemistry",
            key="quiz_topic_input"
        )
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"], key="quiz_difficulty")
        qtype = st.selectbox("Question type", ["MCQ", "Short Answer", "Mixed"], key="quiz_type")
        language = st.selectbox("Language", ["Simple English", "Hindi", "Hinglish"], key="quiz_language")
        count = st.select_slider("Number of questions", options=[5, 10, 15, 20, 30, 40, 50], value=10, key="quiz_count")
        generate = st.button("✳ Generate my quiz", type="primary", use_container_width=True)

    with b:
        st.markdown("""
        <div class="sb-quote">
          <div class="sb-eyebrow">A BETTER WAY TO REVISE</div>
          <div class="sb-quote-title">Learn it.<br>Test it.<br>Remember it.</div>
          <div class="sb-muted">PERSONAL PRACTICE · CLEAR EXPLANATIONS</div>
        </div>""", unsafe_allow_html=True)

        panel("STUDY TIP", "Recall before review", "Try answering each question yourself before checking the solution.")

    if generate:
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            results = []
            remaining = count
            start = 1
            failed = False

            with st.spinner("Building your personalised quiz..."):
                while remaining > 0:
                    batch = min(10, remaining)

                    prompt = f"""You are a careful college-level tutor. Create exactly {batch} questions about {topic}.
Difficulty: {difficulty}. Format: {qtype}. Language: {language}. Start numbering at {start}.
For MCQs include options A-D, correct answer and brief explanation. For short-answer questions include a model answer.
For mixed format include both types. Use readable headings and accurate facts. No long introduction."""

                    answer = ask_ai(prompt, max_tokens=4000)

                    if not answer:
                        failed = True
                        break

                    results.append(answer)
                    remaining -= batch
                    start += batch

            if results:
                combined = "\n\n".join(results)
                st.session_state.last_quiz = combined
                st.session_state.quiz_topic = topic

                st.session_state.quiz_history.append({
                    "topic": topic,
                    "count": count,
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "content": combined
                })

                st.session_state.activity = f"Generated quiz: {topic}"

                if failed:
                    st.warning("The quiz was only partially generated.")
                else:
                    st.success("Your quiz is ready!")

    if st.session_state.last_quiz:
        section("YOUR PRACTICE SET", st.session_state.quiz_topic)
        st.markdown(st.session_state.last_quiz)

        st.download_button(
            "Download quiz as TXT",
            data=st.session_state.last_quiz,
            file_name="study_buddy_quiz.txt",
            mime="text/plain",
            use_container_width=True
        )


def pdf_notes():
    page_header("02 / ORGANISE", "Notes Studio", "Turn readable PDF study material into structured notes for revision.")

    panel("DOCUMENT WORKSPACE", "Start with your study material", "Upload a PDF, choose a format and create notes you can download.")

    uploaded = st.file_uploader("Upload your study PDF", type=["pdf"], key="notes_pdf_upload")

    if uploaded:
        try:
            reader = PdfReader(uploaded)
            extracted = "\n".join(page.extract_text() or "" for page in reader.pages).strip()

            if extracted:
                st.session_state.pdf_text = extracted
                st.session_state.notes_title = uploaded.name
                st.success(f"PDF ready · {len(reader.pages)} pages detected")
            else:
                st.warning("No selectable text was found. Scanned PDFs may require OCR.")
        except Exception:
            st.error("Could not read this PDF. Please try another file.")

    a, b = st.columns(2)

    with a:
        style = st.selectbox(
            "Notes format",
            [
                "Detailed notes with headings",
                "Exam revision notes",
                "Short summary",
                "Question and answer format",
                "Bullet-point notes"
            ],
            key="notes_style"
        )

    with b:
        language = st.selectbox(
            "Output language",
            ["Simple English", "Hindi", "Hinglish"],
            key="notes_language"
        )

    if st.button("▤ Generate study notes", type="primary", use_container_width=True):
        if not st.session_state.pdf_text:
            st.warning("Upload a readable PDF first.")
        else:
            prompt = f"""You are an educational note-making assistant. Create notes using only the supplied source text.
Format: {style}. Language: {language}. Use clear headings, subheadings and bullet points.
Preserve important definitions, formulas, examples and facts. Explain difficult ideas in student-friendly language.
Do not invent facts or claim to cover material not present in the source.
SOURCE TEXT:
{st.session_state.pdf_text[:26000]}"""

            with st.spinner("Creating organised study notes..."):
                notes = ask_ai(prompt, max_tokens=6000)

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

        a, b = st.columns(2)

        with a:
            st.download_button(
                "Download TXT",
                data=st.session_state.last_notes,
                file_name="study_buddy_notes.txt",
                mime="text/plain",
                use_container_width=True
            )

        with b:
            try:
                pdf_data = make_pdf(st.session_state.last_notes)

                st.download_button(
                    "Download PDF",
                    data=pdf_data,
                    file_name="study_buddy_notes.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception:
                st.error("PDF export failed. You can still download the TXT.")


def study_chat():
    page_header("03 / UNDERSTAND", "Personal AI Tutor", "Ask questions and get clear, step-by-step study explanations.")

    panel("CONVERSATION SPACE", "What would you like to understand?", "Ask one question at a time for focused help with your studies.")

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
            "content": "You are Study Buddy AI, a patient and accurate tutor. Explain in simple, clear language. Use examples and show calculation steps when useful. Do not invent facts."
        }]

        messages.extend(st.session_state.chat[-12:])

        with st.chat_message("assistant"):
            with st.spinner("Preparing your explanation..."):
                answer = ask_ai(messages=messages, max_tokens=3000)

            if answer:
                st.markdown(answer)
                st.session_state.chat.append({"role": "assistant", "content": answer})
                st.session_state.activity = "Asked a question in Study Chat"

    if st.session_state.chat and st.button("Clear conversation", use_container_width=True):
        st.session_state.chat = []
        st.rerun()


def performance():
    page_header("04 / REFLECT", "Progress Centre", "Review your quiz sets, notes and study activity in this session.")

    a, b, c = st.columns(3)
    a.metric("Quiz sets", len(st.session_state.quiz_history))
    b.metric("Notes created", len(st.session_state.notes_history))
    c.metric("Questions asked", sum(1 for m in st.session_state.chat if m["role"] == "user"))

    section("ACTIVITY / 01", "Your latest work")
    panel("RECENT UPDATE", "Learning activity", st.session_state.activity)

    section("PRACTICE / 02", "Quiz history")

    if st.session_state.quiz_history:
        for i, item in enumerate(reversed(st.session_state.quiz_history[-10:])):
            with st.expander(f"{item['topic']} · {item['count']} questions · {item['date']}"):
                st.markdown(item["content"])

                st.download_button(
                    "Download quiz",
                    data=item["content"],
                    file_name="study_buddy_quiz.txt",
                    mime="text/plain",
                    key=f"history_quiz_{i}"
                )
    else:
        st.info("Your generated quizzes will appear here.")

    section("RESOURCES / 03", "Notes history")

    if st.session_state.notes_history:
        for i, item in enumerate(reversed(st.session_state.notes_history[-10:])):
            with st.expander(f"{item['title']} · {item['date']}"):
                st.markdown(item["content"])

                st.download_button(
                    "Download notes",
                    data=item["content"],
                    file_name="study_buddy_notes.txt",
                    mime="text/plain",
                    key=f"history_notes_{i}"
                )
    else:
        st.info("Your created notes will appear here.")


def settings():
    page_header("05 / SETTINGS", "Workspace settings", "Review your app configuration and manage current session data.")

    panel("PRODUCT", "Study Buddy AI", "A learning workspace for AI quizzes, PDF notes and study conversations.")
    panel("AI ENGINE", MODEL, "Uses Groq. Configure GROQ_API_KEY privately in Streamlit Cloud Secrets.")
    panel("SESSION HISTORY", "Temporary session storage", "Your current quiz, notes and chat history are held in the active session and are not a permanent database.")

    section("SESSION MANAGEMENT", "Clear current history")

    confirm = st.checkbox("I understand that clearing data removes my current quiz, notes and chat history.")

    if st.button("Clear session history", type="primary", use_container_width=True):
        if not confirm:
            st.warning("Confirm the checkbox before clearing your data.")
        else:
            reset_values = {
                "chat": [],
                "quiz_history": [],
                "notes_history": [],
                "last_quiz": "",
                "last_notes": "",
                "quiz_topic": "",
                "notes_title": "",
                "pdf_text": "",
                "activity": "Your learning journey starts here"
            }

            for key, value in reset_values.items():
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
  <span>STUDY BUDDY AI · PERSONAL LEARNING WORKSPACE</span>
  <span>LEARN WITH PURPOSE · GROW WITH CONFIDENCE</span>
</div>""", unsafe_allow_html=True)