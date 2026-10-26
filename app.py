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
    page_title="Study Buddy AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

MODEL = "openai/gpt-oss-20b"
GREEN = "#087F5B"

PAGES = {
    "Dashboard": "⌂",
    "AI Quiz": "✳",
    "PDF Notes": "▤",
    "Study Chat": "◉",
    "Performance": "↗",
    "Settings": "⚙"
}

for key, default in {
    "page": "Dashboard",
    "menu_open": False,
    "chat_messages": [],
    "quiz_history": [],
    "notes_history": [],
    "generated_quizzes": 0,
    "notes_created": 0,
    "last_quiz": "",
    "last_notes": "",
    "pdf_text": "",
    "quiz_topic": "",
    "last_activity": "Your learning journey starts here",
    "quiz_partial": False,
    "notes_title": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
 --bg:#F6F8F4;
 --paper:#FFFFFF;
 --ink:#17372A;
 --green:#087F5B;
 --deep:#064E3B;
 --mint:#DDF3E5;
 --line:#DDE7DE;
 --muted:#718278;
 --lime:#C7EDB5;
}

html,body,[class*="css"] {
 font-family:'DM Sans',sans-serif;
}

.stApp {
 background:var(--bg);
 color:var(--ink);
}

#MainMenu,footer {
 visibility:hidden;
}

header[data-testid="stHeader"] {
 background:transparent;
}

.block-container {
 max-width:1450px;
 padding:1rem 3rem 4rem;
}

h1,h2,h3,h4 {
 font-family:'Manrope',sans-serif!important;
 color:var(--ink);
 letter-spacing:-1px;
}

p {
 line-height:1.7;
}

hr {
 border-color:var(--line);
}

div.stButton>button {
 border:1px solid var(--line);
 border-radius:12px;
 min-height:43px;
 font-weight:600;
 color:var(--ink);
 background:white;
 transition:all .2s ease;
}

div.stButton>button:hover {
 border-color:var(--green);
 color:var(--green);
 background:#F0F8F1;
}

div.stButton>button[kind="primary"] {
 background:var(--green);
 border-color:var(--green);
 color:white;
}

div.stButton>button[kind="primary"]:hover {
 background:var(--deep);
 color:white;
}

.stTextInput input,.stTextArea textarea,
.stSelectbox div[data-baseweb="select"],
.stNumberInput input {
 border-radius:11px!important;
}

[data-testid="stFileUploader"] {
 border:1px dashed #9CCBA9;
 border-radius:16px;
 background:white;
 padding:12px;
}

[data-testid="stChatMessage"] {
 border:1px solid var(--line);
 border-radius:15px;
 background:white;
}

[data-testid="stMetric"] {
 background:white;
 border:1px solid var(--line);
 border-radius:15px;
 padding:17px;
}

[data-testid="stMetricValue"] {
 color:var(--green);
 font-family:'Manrope',sans-serif;
}

.sb-top {
 display:flex;
 justify-content:space-between;
 align-items:center;
 gap:12px;
 padding:5px 0 18px;
 border-bottom:1px solid var(--line);
 margin-bottom:22px;
}

.sb-brand {
 display:flex;
 align-items:center;
 gap:11px;
}

.sb-mark {
 width:45px;
 height:45px;
 display:flex;
 align-items:center;
 justify-content:center;
 color:white;
 background:var(--green);
 border-radius:15px 15px 15px 4px;
 font-family:'Manrope',sans-serif;
 font-size:21px;
 font-weight:800;
 box-shadow:0 6px 16px #087F5B25;
}

.sb-name {
 font-family:'Manrope',sans-serif;
 font-size:17px;
 line-height:1.2;
 font-weight:800;
 letter-spacing:-.7px;
 color:var(--ink);
}

.sb-tag {
 margin-top:5px;
 font-family:'DM Mono',monospace;
 font-size:9px;
 letter-spacing:1.5px;
 color:var(--muted);
}

.sb-online {
 font-family:'DM Mono',monospace;
 font-size:9px;
 letter-spacing:1px;
 color:var(--green);
 border:1px solid #C9E3CF;
 background:#EFF8F0;
 padding:9px 12px;
 border-radius:30px;
 white-space:nowrap;
}

.sb-led {
 display:inline-block;
 height:7px;
 width:7px;
 background:#29A56D;
 border-radius:50%;
 margin-right:6px;
}

.sb-nav {
 background:white;
 border:1px solid var(--line);
 border-radius:17px;
 padding:18px;
 margin:0 0 23px;
}

.sb-nav-label {
 font-family:'DM Mono',monospace;
 color:var(--muted);
 font-size:10px;
 letter-spacing:1.5px;
 margin-bottom:13px;
}

.sb-nav-hint {
 color:var(--muted);
 font-size:12px;
 margin-top:12px;
}

.sb-hero {
 position:relative;
 overflow:hidden;
 min-height:340px;
 border-radius:25px;
 padding:35px;
 color:white;
 background:linear-gradient(118deg,#103E35 0%,#087F5B 72%,#15966B 100%);
}

.sb-hero:before {
 content:"";
 position:absolute;
 width:350px;
 height:350px;
 right:-100px;
 top:-190px;
 border:1px solid #FFFFFF35;
 border-radius:50%;
 box-shadow:0 0 0 35px #FFFFFF08,0 0 0 75px #FFFFFF07;
}

.sb-hero:after {
 content:"";
 position:absolute;
 width:220px;
 height:220px;
 right:0;
 bottom:-160px;
 border:1px solid #FFFFFF35;
 border-radius:50%;
}

.sb-hero-content {
 position:relative;
 z-index:1;
}

.sb-kicker {
 font-family:'DM Mono',monospace;
 font-size:10px;
 letter-spacing:2px;
 color:#B7E9CA;
}

.sb-hero-title {
 font-family:'Manrope',sans-serif;
 font-size:clamp(38px,5vw,68px);
 line-height:1.04;
 letter-spacing:-4px;
 font-weight:800;
 margin:24px 0 16px;
 color:white;
}

.sb-hero-title span {
 color:#C7EDB5;
}

.sb-hero-copy {
 font-size:14px;
 line-height:1.9;
 color:#E1F1E8;
 max-width:540px;
}

.sb-hero-stamp {
 position:absolute;
 right:7%;
 bottom:25%;
 z-index:1;
 width:135px;
 height:135px;
 border:1px solid #FFFFFF70;
 border-radius:50%;
 display:flex;
 align-items:center;
 justify-content:center;
 text-align:center;
 color:#D7F4D4;
 font-family:'DM Mono',monospace;
 font-size:11px;
 letter-spacing:2px;
 transform:rotate(10deg);
}

.sb-hero-stamp:after {
 content:"";
 position:absolute;
 inset:11px;
 border:1px dashed #FFFFFF60;
 border-radius:50%;
}

.sb-eyebrow {
 color:var(--green);
 font-family:'DM Mono',monospace;
 font-size:10px;
 letter-spacing:1.7px;
}

.sb-heading {
 font-family:'Manrope',sans-serif;
 font-size:clamp(29px,3.5vw,43px);
 line-height:1.1;
 font-weight:800;
 letter-spacing:-2px;
 margin:9px 0 12px;
}

.sb-sub {
 color:var(--muted);
 font-size:13px;
 line-height:1.85;
 max-width:650px;
}

.sb-section {
 margin:31px 0 15px;
}

.sb-section-title {
 font-family:'Manrope',sans-serif;
 font-size:24px;
 font-weight:800;
 letter-spacing:-1px;
}

.sb-section-caption {
 font-family:'DM Mono',monospace;
 color:var(--muted);
 font-size:9px;
 letter-spacing:1.5px;
 margin-bottom:7px;
}

.sb-feature {
 height:100%;
 min-height:210px;
 border:1px solid var(--line);
 border-radius:19px;
 padding:22px;
 background:white;
 transition:transform .2s,border-color .2s;
}

.sb-feature:hover {
 transform:translateY(-3px);
 border-color:#9BCDA9;
}

.sb-feature-head {
 display:flex;
 align-items:center;
 justify-content:space-between;
 margin-bottom:25px;
}

.sb-feature-icon {
 width:43px;
 height:43px;
 display:flex;
 align-items:center;
 justify-content:center;
 border-radius:13px;
 background:#E5F4E8;
 color:var(--green);
 font-size:22px;
}

.sb-feature-number {
 font-family:'DM Mono',monospace;
 color:#9AA89E;
 font-size:10px;
}

.sb-feature-title {
 font-family:'Manrope',sans-serif;
 font-size:20px;
 font-weight:800;
 letter-spacing:-.8px;
}

.sb-feature-copy {
 font-size:12px;
 color:var(--muted);
 line-height:1.8;
 margin-top:7px;
}

.sb-feature-arrow {
 font-family:'DM Mono',monospace;
 font-size:10px;
 color:var(--green);
 margin-top:17px;
}

.sb-stat {
 background:white;
 border:1px solid var(--line);
 border-radius:16px;
 padding:18px;
 height:100%;
}

.sb-stat-top {
 display:flex;
 justify-content:space-between;
 gap:8px;
 align-items:center;
}

.sb-stat-name {
 font-family:'DM Mono',monospace;
 font-size:9px;
 letter-spacing:1px;
 color:var(--muted);
}

.sb-stat-icon {
 color:var(--green);
 font-size:19px;
}

.sb-stat-number {
 font-family:'Manrope',sans-serif;
 font-size:38px;
 letter-spacing:-2px;
 font-weight:800;
 margin-top:16px;
 color:var(--ink);
}

.sb-stat-foot {
 font-size:11px;
 color:var(--muted);
 margin-top:4px;
}

.sb-side-card {
 border-radius:20px;
 background:#E4F3E6;
 padding:24px;
 color:var(--deep);
 height:100%;
}

.sb-side-card .quote {
 font-family:'Manrope',sans-serif;
 font-size:22px;
 line-height:1.4;
 letter-spacing:-.7px;
 font-weight:800;
 margin:16px 0;
}

.sb-small {
 font-family:'DM Mono',monospace;
 font-size:9px;
 letter-spacing:1.3px;
 color:#4D8261;
}

.sb-activity {
 background:white;
 border:1px solid var(--line);
 border-radius:18px;
 padding:20px;
}

.sb-activity-row {
 display:flex;
 align-items:center;
 gap:13px;
 padding:13px 0;
 border-bottom:1px solid #EEF1ED;
}

.sb-activity-row:last-child {
 border-bottom:none;
}

.sb-activity-icon {
 height:38px;
 width:38px;
 flex-shrink:0;
 display:flex;
 align-items:center;
 justify-content:center;
 border-radius:12px;
 background:#E6F5E9;
 color:var(--green);
 font-size:18px;
}

.sb-activity-title {
 font-size:13px;
 font-weight:700;
 color:var(--ink);
}

.sb-activity-copy {
 font-size:11px;
 color:var(--muted);
 margin-top:4px;
}

.sb-page-top {
 padding:12px 0 22px;
 margin-bottom:24px;
 border-bottom:1px solid var(--line);
}

.sb-page-title {
 font-family:'Manrope',sans-serif;
 font-size:clamp(35px,4vw,54px);
 font-weight:800;
 line-height:1.1;
 letter-spacing:-3px;
 margin:12px 0;
}

.sb-panel {
 background:white;
 border:1px solid var(--line);
 border-radius:18px;
 padding:22px;
}

.sb-panel-label {
 font-family:'DM Mono',monospace;
 font-size:10px;
 color:var(--green);
 letter-spacing:1.5px;
}

.sb-panel-title {
 font-family:'Manrope',sans-serif;
 font-size:21px;
 font-weight:800;
 letter-spacing:-.8px;
 margin:8px 0 10px;
}

.sb-footer {
 border-top:1px solid var(--line);
 margin-top:35px;
 padding-top:16px;
 display:flex;
 justify-content:space-between;
 gap:10px;
 color:#839188;
 font-family:'DM Mono',monospace;
 font-size:9px;
 letter-spacing:1px;
}

@media(max-width:800px) {
 .block-container {
  padding:0.7rem 1rem 3rem;
 }
 .sb-hero {
  padding:25px 22px;
  min-height:360px;
 }
 .sb-hero-title {
  letter-spacing:-2.5px;
  font-size:43px;
 }
 .sb-hero-stamp {
  width:90px;
  height:90px;
  font-size:8px;
  right:8%;
  bottom:9%;
 }
 .sb-hero-copy {
  max-width:100%;
  font-size:13px;
 }
 .sb-top {
  align-items:flex-start;
 }
 .sb-online {
  font-size:8px;
  padding:8px;
 }
 .sb-name {
  font-size:15px;
 }
 .sb-tag {
  font-size:8px;
  letter-spacing:.8px;
 }
 .sb-feature {
  padding:17px;
  min-height:195px;
 }
 .sb-feature-title {
  font-size:18px;
 }
 .sb-footer {
  flex-direction:column;
 }
}
</style>
""", unsafe_allow_html=True)


def get_client():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        key = ""

    if not key:
        return None

    return Groq(api_key=key)


def ask_ai(prompt, max_tokens=3000, temperature=0.4):
    client = get_client()

    if client is None:
        st.error(
            "GROQ_API_KEY missing hai. Streamlit Cloud ke "
            "App Settings → Secrets mein key configure karo."
        )
        return None

    try:
        result = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return result.choices[0].message.content.strip()

    except Exception as error:
        st.error(f"AI request failed: {error}")
        return None


def page_header(number, title, description):
    st.markdown(f"""
    <div class="sb-page-top">
      <div class="sb-eyebrow">STUDY BUDDY AI &nbsp; / &nbsp; {escape(number)}</div>
      <div class="sb-page-title">{escape(title)}</div>
      <div class="sb-sub">{escape(description)}</div>
    </div>
    """, unsafe_allow_html=True)


def section(label, title):
    st.markdown(f"""
    <div class="sb-section">
      <div class="sb-section-caption">{escape(label)}</div>
      <div class="sb-section-title">{escape(title)}</div>
    </div>
    """, unsafe_allow_html=True)


def stat_card(icon, label, value, caption):
    st.markdown(f"""
    <div class="sb-stat">
      <div class="sb-stat-top">
        <div class="sb-stat-name">{escape(label)}</div>
        <div class="sb-stat-icon">{icon}</div>
      </div>
      <div class="sb-stat-number">{escape(str(value))}</div>
      <div class="sb-stat-foot">{escape(caption)}</div>
    </div>
    """, unsafe_allow_html=True)


def feature_card(number, icon, title, description, page):
    st.markdown(f"""
    <div class="sb-feature">
      <div class="sb-feature-head">
        <div class="sb-feature-icon">{icon}</div>
        <div class="sb-feature-number">SPACE / {number}</div>
      </div>
      <div class="sb-feature-title">{escape(title)}</div>
      <div class="sb-feature-copy">{escape(description)}</div>
      <div class="sb-feature-arrow">ENTER WORKSPACE ↗</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(
        f"Open {title} ↗",
        key=f"open_{number}",
        use_container_width=True
    ):
        st.session_state.page = page
        st.session_state.menu_open = False
        st.rerun()


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
        "StudyTitle",
        parent=styles["Title"],
        textColor=colors.HexColor("#087F5B"),
        fontSize=22,
        leading=28,
        spaceAfter=18
    )

    body_style = ParagraphStyle(
        "StudyBody",
        parent=styles["BodyText"],
        fontSize=10,
        leading=16,
        textColor=colors.HexColor("#24392E"),
        spaceAfter=8
    )

    story = [
        Paragraph(escape(title), title_style),
        Paragraph(
            "Created with Study Buddy AI",
            styles["Normal"]
        ),
        Spacer(1, 18)
    ]

    for line in content.splitlines():
        line = line.strip()

        if not line:
            story.append(Spacer(1, 5))
        elif line.startswith("#"):
            story.append(
                Paragraph(
                    escape(line.lstrip("#").strip()),
                    styles["Heading2"]
                )
            )
        elif line.startswith(("- ", "* ", "• ")):
            story.append(
                Paragraph(
                    "&#8226; " + escape(line[2:].strip()),
                    body_style
                )
            )
        else:
            story.append(Paragraph(escape(line), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def render_topbar():
    menu_col, brand_col, status_col = st.columns([0.6, 3.7, 1.6])

    with menu_col:
        if st.button(
            "☰",
            key="hamburger",
            help="Open navigation",
            use_container_width=True
        ):
            st.session_state.menu_open = not st.session_state.menu_open
            st.rerun()

    with brand_col:
        st.markdown("""
        <div class="sb-brand">
          <div class="sb-mark">S.</div>
          <div>
            <div class="sb-name">Study Buddy AI</div>
            <div class="sb-tag">YOUR PERSONAL LEARNING SPACE</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with status_col:
        st.markdown("""
        <div style="text-align:right;padding-top:8px">
          <div class="sb-online"><span class="sb-led"></span>AI WORKSPACE</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        '<div style="height:1px;background:#DDE7DE;margin:18px 0 22px"></div>',
        unsafe_allow_html=True
    )


def render_navigation():
    if not st.session_state.menu_open:
        return

    st.markdown("""
    <div class="sb-nav">
      <div class="sb-nav-label">☰ &nbsp; NAVIGATION / WORKSPACES</div>
    </div>
    """, unsafe_allow_html=True)

    columns = st.columns(3)

    for index, (name, icon) in enumerate(PAGES.items()):
        with columns[index % 3]:
            current = st.session_state.page == name

            if st.button(
                f"{icon}  {name}" + ("  ✓" if current else ""),
                key=f"nav_{name}",
                type="primary" if current else "secondary",
                use_container_width=True
            ):
                st.session_state.page = name
                st.session_state.menu_open = False
                st.rerun()

    st.markdown(
        '<div style="height:10px"></div>',
        unsafe_allow_html=True
    )


def dashboard():
    st.markdown("""
    <div class="sb-hero">
      <div class="sb-hero-content">
        <div class="sb-kicker">✦ &nbsp; YOUR PERSONAL AI STUDY SPACE</div>
        <div class="sb-hero-title">
          Make every study<br>
          session <span>count.</span>
        </div>
        <div class="sb-hero-copy">
          Your personal AI workspace for quizzes, clear notes and doubt
          solving. Turn study time into real progress.
        </div>
      </div>
      <div class="sb-hero-stamp">LEARN<br>GROW<br>REPEAT</div>
    </div>
    """, unsafe_allow_html=True)

    section("YOUR ACTIVITY / 01", "Your study overview")

    c1, c2, c3 = st.columns(3)

    with c1:
        stat_card(
            "✳", "QUIZZES GENERATED",
            st.session_state.generated_quizzes,
            "Practice sets created"
        )

    with c2:
        stat_card(
            "▤", "NOTES CREATED",
            st.session_state.notes_created,
            "Study resources prepared"
        )

    with c3:
        chat_count = sum(
            1 for item in st.session_state.chat_messages
            if item["role"] == "user"
        )

        stat_card(
            "◉", "QUESTIONS ASKED",
            chat_count,
            "Questions sent to your AI tutor"
        )

    section("THE TOOLKIT / 02", "Choose your next move")

    c1, c2 = st.columns(2)

    with c1:
        feature_card(
            "01", "✳", "AI Quiz Lab",
            "Build topic-based practice questions and revise with answers.",
            "AI Quiz"
        )

    with c2:
        feature_card(
            "02", "▤", "Notes Studio",
            "Turn your PDF material into organised study notes.",
            "PDF Notes"
        )

    c3, c4 = st.columns(2)

    with c3:
        feature_card(
            "03", "◉", "Study Chat",
            "Ask doubts and learn concepts through clear explanations.",
            "Study Chat"
        )

    with c4:
        feature_card(
            "04", "↗", "Growth Tracker",
            "Review your quiz, notes and study activity.",
            "Performance"
        )

    section("RECENT ACTIVITY / 03", "Your learning trail")

    st.markdown(f"""
    <div class="sb-activity">
      <div class="sb-activity-row">
        <div class="sb-activity-icon">◈</div>
        <div>
          <div class="sb-activity-title">Latest activity</div>
          <div class="sb-activity-copy">{escape(st.session_state.last_activity)}</div>
        </div>
      </div>
      <div class="sb-activity-row">
        <div class="sb-activity-icon">✳</div>
        <div>
          <div class="sb-activity-title">Quiz sessions</div>
          <div class="sb-activity-copy">{len(st.session_state.quiz_history)} quiz sets recorded in this session</div>
        </div>
      </div>
      <div class="sb-activity-row">
        <div class="sb-activity-icon">▤</div>
        <div>
          <div class="sb-activity-title">Study resources</div>
          <div class="sb-activity-copy">{len(st.session_state.notes_history)} sets of notes created in this session</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="sb-footer">
      <span>STUDY BUDDY AI · PERSONAL LEARNING WORKSPACE</span>
      <span>LEARN WITH PURPOSE ↗</span>
    </div>
    """, unsafe_allow_html=True)


def ai_quiz():
    page_header(
        "01 / PRACTICE",
        "AI Quiz Lab.",
        "Create practice questions around your subject, your level and your goals."
    )

    left, right = st.columns([1.15, 0.85])

    with left:
        st.markdown("""
        <div class="sb-panel">
          <div class="sb-panel-label">QUIZ CONFIGURATION</div>
          <div class="sb-panel-title">Build your practice set</div>
        </div>
        """, unsafe_allow_html=True)

        topic = st.text_input(
            "Topic or subject",
            placeholder="e.g. BJT, recursion, electrochemistry"
        )

        difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard", "Mixed"]
        )

        qtype = st.selectbox(
            "Question format",
            ["MCQ", "Short Answer", "Mixed"]
        )

        language = st.selectbox(
            "Language",
            ["Simple English", "Hindi", "Hinglish"]
        )

        count = st.select_slider(
            "Number of questions",
            options=[5, 10, 15, 20, 30, 40, 50],
            value=10
        )

        generate = st.button(
            "✳  Generate quiz",
            type="primary",
            use_container_width=True
        )

    with right:
        st.markdown("""
        <div class="sb-side-card">
          <div class="sb-small">PRACTICE / PRINCIPLE 01</div>
          <div class="quote">Test what you know. Discover what you can learn.</div>
          <div class="sb-small">TOPIC-BASED · ADAPTABLE · REVISION-READY</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="sb-panel">
          <div class="sb-panel-label">STUDY TIP</div>
          <div class="sb-panel-title">Try before you reveal</div>
          <div class="sb-sub">Attempt each question first, then read its answer and explanation.</div>
        </div>
        """, unsafe_allow_html=True)

    if generate:
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            outputs = []
            remaining = count
            start = 1
            failed = False

            with st.spinner("Creating your practice set..."):
                while remaining > 0:
                    batch = min(10, remaining)

                    prompt = f"""
You are an accurate college-level tutor.
Create exactly {batch} questions about: {topic}
Difficulty: {difficulty}
Format: {qtype}
Language: {language}
Start numbering at {start}.

For each MCQ, provide options A, B, C and D, the correct answer
and a short explanation.
For short-answer questions, provide a clear model answer.
For mixed format, include both formats.
Keep formatting readable and do not add an introduction.
Do not invent facts.
"""

                    answer = ask_ai(prompt, max_tokens=4500)

                    if not answer:
                        failed = True
                        break

                    outputs.append(answer)
                    remaining -= batch
                    start += batch

            if outputs:
                result = "\n\n".join(outputs)
                st.session_state.last_quiz = result
                st.session_state.quiz_topic = topic
                st.session_state.generated_quizzes += 1
                st.session_state.quiz_partial = failed

                st.session_state.quiz_history.append({
                    "topic": topic,
                    "count": count,
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "content": result
                })

                st.session_state.last_activity = f"Generated quiz: {topic}"

                if failed:
                    st.warning("Quiz partially generated. Available questions are shown below.")
                else:
                    st.success("Your quiz is ready!")

    if st.session_state.last_quiz:
        section("GENERATED MATERIAL", st.session_state.quiz_topic)

        st.markdown(st.session_state.last_quiz)

        st.download_button(
            "Download quiz as TXT",
            data=st.session_state.last_quiz,
            file_name="study_buddy_quiz.txt",
            mime="text/plain",
            use_container_width=True
        )


def pdf_notes():
    page_header(
        "02 / ORGANISE",
        "Notes Studio.",
        "Convert readable PDF material into notes that are easier to understand and revise."
    )

    st.markdown("""
    <div class="sb-panel">
      <div class="sb-panel-label">DOCUMENT WORKSPACE</div>
      <div class="sb-panel-title">Bring your study material</div>
      <div class="sb-sub">Upload your PDF and choose how you want your notes to be organised.</div>
    </div>
    """, unsafe_allow_html=True)

    file = st.file_uploader("Upload study PDF", type=["pdf"])

    style = st.selectbox(
        "Notes format",
        [
            "Detailed notes with headings",
            "Exam revision notes",
            "Short summary",
            "Question and answer format",
            "Bullet-point notes"
        ]
    )

    language = st.selectbox(
        "Output language",
        ["Simple English", "Hindi", "Hinglish"]
    )

    if file:
        try:
            reader = PdfReader(file)
            extracted = "\n".join(
                page.extract_text() or "" for page in reader.pages
            ).strip()

            if extracted:
                st.session_state.pdf_text = extracted
                st.success(f"PDF ready · {len(reader.pages)} pages")
            else:
                st.warning(
                    "Selectable text nahi mila. Scanned PDFs ke liye OCR ki zaroorat ho sakti hai."
                )
        except Exception as error:
            st.error(f"PDF read nahi ho saki: {error}")

    if st.button(
        "▤  Create notes",
        type="primary",
        use_container_width=True
    ):
        if not st.session_state.pdf_text:
            st.warning("Please upload a readable PDF first.")
        else:
            prompt = f"""
You are an educational note-making assistant.
Create notes from the following source material.

Style: {style}
Language: {language}

Use headings, subheadings and bullet points.
Preserve key definitions, formulas, examples and facts.
Explain important concepts in student-friendly language.
Do not invent details or claim to have covered unseen content.

SOURCE:
{st.session_state.pdf_text[:26000]}
"""

            with st.spinner("Organising your notes..."):
                notes = ask_ai(prompt, max_tokens=6000)

            if notes:
                st.session_state.last_notes = notes
                st.session_state.notes_created += 1
                st.session_state.notes_title = file.name if file else "Study Notes"

                st.session_state.notes_history.append({
                    "title": st.session_state.notes_title,
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "content": notes
                })

                st.session_state.last_activity = "Created PDF study notes"
                st.success("Your notes are ready!")

    if st.session_state.last_notes:
        section("YOUR DOCUMENT", "Ready for revision")
        st.markdown(st.session_state.last_notes)

        c1, c2 = st.columns(2)

        with c1:
            st.download_button(
                "Download TXT",
                data=st.session_state.last_notes,
                file_name="study_buddy_notes.txt",
                mime="text/plain",
                use_container_width=True
            )

        with c2:
            try:
                pdf_data = make_pdf(st.session_state.last_notes)

                st.download_button(
                    "Download PDF",
                    data=pdf_data,
                    file_name="study_buddy_notes.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as error:
                st.error(f"PDF export failed: {error}")


def study_chat():
    page_header(
        "03 / UNDERSTAND",
        "Study Chat.",
        "Ask questions, explore examples and work through difficult concepts with your AI tutor."
    )

    left, right = st.columns([1.7, 0.8])

    with left:
        st.markdown("""
        <div class="sb-panel">
          <div class="sb-panel-label">CONVERSATION SPACE</div>
          <div class="sb-panel-title">Curiosity starts here.</div>
          <div class="sb-sub">Ask one question at a time for focused, clear explanations.</div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="sb-side-card">
          <div class="sb-small">REMEMBER</div>
          <div class="quote">Understanding matters more than memorising.</div>
          <div class="sb-small">ASK · EXPLORE · UNDERSTAND</div>
        </div>
        """, unsafe_allow_html=True)

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask your study question...")

    if prompt:
        st.session_state.chat_messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        client = get_client()

        if client is None:
            st.error("GROQ_API_KEY is missing from Streamlit Secrets.")
        else:
            messages = [{
                "role": "system",
                "content": (
                    "You are Study Buddy AI, a patient and accurate study tutor. "
                    "Explain clearly in the user's language. Show calculation steps "
                    "where needed and do not invent facts."
                )
            }]
            messages.extend(st.session_state.chat_messages[-12:])

            try:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = client.chat.completions.create(
                            model=MODEL,
                            messages=messages,
                            temperature=0.4,
                            max_tokens=3000
                        )
                        answer = response.choices[0].message.content.strip()

                    st.markdown(answer)

                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": answer
                })
                st.session_state.last_activity = "Asked a question in Study Chat"

            except Exception as error:
                st.error(f"Chat request failed: {error}")

    if st.session_state.chat_messages:
        if st.button("Clear chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()


def performance():
    page_header(
        "04 / REFLECT",
        "Your progress.",
        "Review your activity and the study resources you have created in this session."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Quiz sessions", st.session_state.generated_quizzes)

    with c2:
        st.metric("Notes created", st.session_state.notes_created)

    with c3:
        st.metric(
            "Questions asked",
            sum(1 for item in st.session_state.chat_messages if item["role"] == "user")
        )

    section("ACTIVITY / 01", "Your latest work")

    st.markdown(f"""
    <div class="sb-panel">
      <div class="sb-panel-label">MOST RECENT</div>
      <div class="sb-panel-title">{escape(st.session_state.last_activity)}</div>
      <div class="sb-sub">Activity is stored in the current app session and may reset when the session restarts.</div>
    </div>
    """, unsafe_allow_html=True)

    section("PRACTICE / 02", "Quiz history")

    if st.session_state.quiz_history:
        for i, item in enumerate(reversed(st.session_state.quiz_history[-10:])):
            with st.expander(
                f"{item['topic']} · {item['count']} questions · {item['date']}"
            ):
                st.markdown(item["content"])

                st.download_button(
                    "Download quiz",
                    data=item["content"],
                    file_name="study_buddy_quiz.txt",
                    mime="text/plain",
                    key=f"qh_{i}"
                )
    else:
        st.info("Your quiz history will appear here.")

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
                    key=f"nh_{i}"
                )
    else:
        st.info("Your notes history will appear here.")

    st.markdown("""
    <div class="sb-footer">
      <span>STUDY BUDDY AI</span>
      <span>SMALL STEPS · REAL PROGRESS</span>
    </div>
    """, unsafe_allow_html=True)


def settings():
    page_header(
        "05 / SETTINGS",
        "Your workspace.",
        "Review app information and manage your current session data."
    )

    st.markdown("""
    <div class="sb-panel">
      <div class="sb-panel-label">PRODUCT IDENTITY</div>
      <div class="sb-panel-title">Study Buddy AI</div>
      <div class="sb-sub">
        A personal AI learning workspace for quizzes, PDF notes and study conversations.
      </div>
      <div style="margin-top:17px" class="sb-eyebrow">MODEL / GROQ</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:15px"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="sb-panel">
      <div class="sb-panel-label">SESSION DATA</div>
      <div class="sb-panel-title">About your history</div>
      <div class="sb-sub">
        Quiz history, notes and chat messages are kept in the active session.
        They are not a permanent database and may reset when the session restarts.
      </div>
    </div>
    """, unsafe_allow_html=True)

    section("DANGER ZONE", "Clear session history")

    confirm = st.checkbox(
        "I understand this will clear my current quiz, notes and chat history."
    )

    if st.button(
        "Clear session data",
        type="primary",
        use_container_width=True
    ):
        if not confirm:
            st.warning("Please confirm before clearing session data.")
        else:
            for key, value in {
                "chat_messages": [],
                "quiz_history": [],
                "notes_history": [],
                "generated_quizzes": 0,
                "notes_created": 0,
                "last_quiz": "",
                "last_notes": "",
                "pdf_text": "",
                "quiz_topic": "",
                "last_activity": "Your learning journey starts here",
                "quiz_partial": False,
                "notes_title": "",
            }.items():
                st.session_state[key] = value

            st.success("Current session data cleared.")
            st.rerun()

    st.markdown("""
    <div class="sb-footer">
      <span>STUDY BUDDY AI</span>
      <span>YOUR SPACE TO LEARN</span>
    </div>
    """, unsafe_allow_html=True)


render_topbar()
render_navigation()

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