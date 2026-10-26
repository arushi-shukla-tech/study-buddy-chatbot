import streamlit as st
from groq import Groq
from pypdf import PdfReader
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from xml.sax.saxutils import escape
import re

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

MODEL = "openai/gpt-oss-20b"

for key, value in {
    "page": "Dashboard",
    "generated_quizzes": 0,
    "notes_created": 0,
    "chat_messages": [],
    "last_quiz": "",
    "last_notes": "",
    "last_activity": "Ready to study",
    "quiz_history": [],
    "notes_history": [],
    "pdf_text": "",
    "quiz_topic": "",
    "quiz_partial": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = value


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #f5f7fb;
    --card: #ffffff;
    --ink: #17233c;
    --muted: #75819a;
    --green: #087f5b;
    --green2: #12a879;
    --line: #e6ebf2;
}

.stApp {
    background:
        radial-gradient(ellipse at 5% 0%, rgba(18,168,121,.08), transparent 32%),
        radial-gradient(ellipse at 100% 10%, rgba(96,112,230,.07), transparent 28%),
        var(--bg);
    color: var(--ink);
    font-family: 'DM Sans', sans-serif;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3, h4 {
    font-family: 'Manrope', sans-serif !important;
    color: var(--ink);
    letter-spacing: -0.6px;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #102a35 0%, #102c38 55%, #123b38 100%);
    border-right: 1px solid rgba(255,255,255,.08);
}

[data-testid="stSidebar"] * {
    color: #eef8f4 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 10px 12px;
    border-radius: 11px;
    transition: .2s;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,.10);
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,.15);
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 4px 24px 4px;
}

.brand-icon {
    width: 47px;
    height: 47px;
    border-radius: 15px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 25px;
    background: linear-gradient(135deg, #16c79a, #087f5b);
    box-shadow: 0 8px 22px rgba(18,168,121,.22);
}

.brand-name {
    font-family: 'Manrope', sans-serif;
    font-size: 19px;
    font-weight: 800;
    line-height: 1.3;
    color: white;
}

.brand-caption {
    font-size: 11px;
    color: #a7c8bf;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 34px;
    border-radius: 26px;
    background: linear-gradient(120deg, #102d3a 0%, #125b50 58%, #128365 100%);
    color: white;
    box-shadow: 0 18px 45px rgba(16,65,68,.16);
    margin-bottom: 24px;
}

.hero:after {
    content: "";
    position: absolute;
    width: 270px;
    height: 270px;
    border: 1px solid rgba(255,255,255,.13);
    border-radius: 50%;
    right: -65px;
    top: -100px;
    box-shadow: 0 0 0 35px rgba(255,255,255,.035),
                0 0 0 70px rgba(255,255,255,.025);
}

.hero h1 {
    color: white !important;
    font-size: clamp(28px, 3.4vw, 43px);
    line-height: 1.2;
    font-weight: 800;
    margin: 13px 0;
}

.hero p {
    color: #d4eee5;
    font-size: 15px;
    line-height: 1.7;
    max-width: 620px;
}

.eyebrow {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #9af2d1;
    text-transform: uppercase;
}

.hero-pill {
    display: inline-block;
    padding: 7px 12px;
    border: 1px solid rgba(255,255,255,.2);
    background: rgba(255,255,255,.09);
    border-radius: 30px;
    color: #effff8;
    font-size: 12px;
    margin-bottom: 8px;
}

.section-title {
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    font-size: 22px;
    margin: 26px 0 6px 0;
    color: #17233c;
}

.section-subtitle {
    font-size: 13px;
    color: #75819a;
    margin-bottom: 18px;
}

.metric-card {
    background: white;
    border: 1px solid #e8edf4;
    border-radius: 19px;
    padding: 21px;
    min-height: 142px;
    box-shadow: 0 5px 20px rgba(30,48,80,.035);
    transition: transform .2s, box-shadow .2s;
}

.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(30,48,80,.08);
}

.metric-icon {
    font-size: 22px;
    margin-bottom: 13px;
}

.metric-value {
    font-family: 'Manrope', sans-serif;
    font-size: 31px;
    font-weight: 800;
    color: #17233c;
    line-height: 1.2;
}

.metric-label {
    color: #75819a;
    font-size: 12px;
    margin-top: 6px;
}

.feature-card {
    height: 100%;
    padding: 23px;
    border: 1px solid #e6ebf2;
    background: rgba(255,255,255,.95);
    border-radius: 20px;
    box-shadow: 0 5px 20px rgba(30,48,80,.035);
}

.feature-icon {
    font-size: 30px;
    margin-bottom: 14px;
}

.feature-card h3 {
    font-size: 17px;
    margin-bottom: 8px;
}

.feature-card p {
    color: #75819a;
    font-size: 13px;
    line-height: 1.7;
}

.panel {
    padding: 25px;
    border-radius: 21px;
    background: white;
    border: 1px solid #e6ebf2;
    box-shadow: 0 6px 24px rgba(30,48,80,.035);
    margin-bottom: 18px;
}

.panel-title {
    font-family: 'Manrope', sans-serif;
    font-size: 19px;
    font-weight: 800;
    color: #17233c;
    margin-bottom: 5px;
}

.panel-subtitle {
    color: #75819a;
    font-size: 13px;
    margin-bottom: 20px;
}

.status-chip {
    display: inline-block;
    padding: 6px 11px;
    border-radius: 30px;
    font-size: 11px;
    font-weight: 700;
    background: #e6f8f0;
    color: #087f5b;
}

.stButton > button {
    border-radius: 12px;
    min-height: 43px;
    font-weight: 700;
    border: 1px solid #e0e8e8;
    transition: .2s;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(110deg, #087f5b, #12a879);
    color: white;
    border: 0;
    box-shadow: 0 6px 16px rgba(8,127,91,.17);
}

.stButton > button:hover {
    transform: translateY(-1px);
    border-color: #12a879;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 11px !important;
}

.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #087f5b, #28c79a);
}

[data-testid="stFileUploader"] {
    background: #f8fbfa;
    border: 1px dashed #b8d8ce;
    border-radius: 15px;
    padding: 10px;
}

[data-testid="stChatMessage"] {
    background: white;
    border: 1px solid #e8edf4;
    border-radius: 17px;
    padding: 12px;
    margin-bottom: 12px;
}

/* FIX: Study Chat input text visibility */
.stChatInput textarea,
[data-testid="stChatInput"] textarea {
    color: #17233c !important;
    -webkit-text-fill-color: #17233c !important;
    background-color: #ffffff !important;
    caret-color: #087f5b !important;
    opacity: 1 !important;
}

.stChatInput textarea::placeholder,
[data-testid="stChatInput"] textarea::placeholder {
    color: #75819a !important;
    -webkit-text-fill-color: #75819a !important;
    opacity: 1 !important;
}

[data-testid="stChatInput"] {
    background-color: #ffffff !important;
    border-color: #b8d8ce !important;
}

[data-testid="stChatInput"] button {
    color: #087f5b !important;
}

div[data-testid="stMetric"] {
    background: white;
    padding: 15px;
    border: 1px solid #e6ebf2;
    border-radius: 15px;
}

hr {
    border-color: #e6ebf2;
}

.footer {
    text-align: center;
    color: #8792a7;
    font-size: 11px;
    padding: 25px 0 0 0;
}

@media (max-width: 700px) {
    .block-container { padding-top: 1rem; }
    .hero { padding: 24px 20px; border-radius: 20px; }
    .metric-card { padding: 16px; }
    .panel { padding: 18px; }
}
</style>
""", unsafe_allow_html=True)


def get_client():
    api_key = st.secrets.get("GROQ_API_KEY", "")
  
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
  
def extract_pdf_text(file):
    try:
        reader = PdfReader(file)
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        return "\n".join(pages).strip()
    
def make_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] strong,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] em {
    color: #17233c !important;
    -webkit-text-fill-color: #17233c !important;
    opacity: 1 !important;
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] pre,
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] code {
    color: #17233c !important;
    -webkit-text-fill-color: #17233c !important;
    opacity: 1 !important;
}

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="StudyTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=25,
        textColor=colors.HexColor("#087f5b"),
        alignment=TA_CENTER,
        spaceAfter=18
    ))

    styles.add(ParagraphStyle(
        name="StudyBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        spaceAfter=7
    ))

    styles.add(ParagraphStyle(
        name="StudyHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#087f5b"),
        spaceBefore=12,
        spaceAfter=7
    ))

    story = [Paragraph("STUDY BUDDY AI", styles["StudyTitle"])]

    for line in text.splitlines():
        line = line.strip()
        if not line:
            story.append(Spacer(1, 5))
            continue

        safe_line = escape(line)

        if line.startswith("#"):
            clean = line.lstrip("#").strip()
            story.append(
                Paragraph(escape(clean), styles["StudyHeading"])
            )
        elif line.startswith(("- ", "* ", "• ")):
            clean = line[2:].strip()
            story.append(
                Paragraph("&#8226; " + escape(clean), styles["StudyBody"])
            )
        else:
            story.append(Paragraph(safe_line, styles["StudyBody"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def show_heading(title, subtitle):
    st.markdown(f"""
    <div style="margin-bottom:22px">
      <div class="eyebrow" style="color:#087f5b">STUDY BUDDY AI / WORKSPACE</div>
      <h1 style="font-size:32px;margin:8px 0 6px 0">{escape(title)}</h1>
      <div style="color:#75819a;font-size:14px">{escape(subtitle)}</div>
    </div>
    """, unsafe_allow_html=True)


def go_to(page):
    st.session_state.page = page


def metric_card(icon, value, label):
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-icon">{icon}</div>
      <div class="metric-value">{value}</div>
      <div class="metric-label">{escape(label)}</div>
    </div>
    """, unsafe_allow_html=True)


def feature_card(icon, title, description):
    st.markdown(f"""
    <div class="feature-card">
      <div class="feature-icon">{icon}</div>
      <h3>{escape(title)}</h3>
      <p>{escape(description)}</p>
    </div>
    """, unsafe_allow_html=True)


with st.sidebar:
    st.markdown("""
    <div class="brand">
      <div class="brand-icon">🎓</div>
      <div>
        <div class="brand-name">Study Buddy AI</div>
        <div class="brand-caption">Your learning space</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div style="font-size:11px;letter-spacing:1.5px;'
        'color:#9cc5b8;margin:8px 0">MAIN MENU</div>',
        unsafe_allow_html=True
    )

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
    <div style="padding:14px;background:rgba(255,255,255,.07);border-radius:15px">
      <div style="font-size:12px;font-weight:700">✨ AI Study Assistant</div>
      <div style="font-size:11px;color:#b6d4cc;margin-top:6px;line-height:1.6">
        Create quizzes, understand notes and learn one concept at a time.
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.caption("Powered by Groq AI")


if st.session_state.page == "Dashboard":
    st.markdown("""
    <div class="hero">
      <div class="hero-pill">✦ YOUR PERSONAL AI STUDY SPACE</div>
      <div class="eyebrow">LEARN SMARTER · GROW FASTER</div>
      <h1>Make every study<br>session count.</h1>
      <p>Your personal AI workspace for quizzes, clear notes and doubt solving. Turn study time into real progress.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">Your study overview</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-subtitle">A quick look at what you have created in this session.</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("🧠", st.session_state.generated_quizzes, "Quizzes generated")
    with c2:
        metric_card("📚", st.session_state.notes_created, "Notes created")
    with c3:
        metric_card("💬", len(st.session_state.chat_messages), "Chat messages")

    st.markdown(
        '<div class="section-title">Your AI toolkit</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="section-subtitle">Choose what you want to work on today.</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        feature_card(
            "🧩", "AI Quiz",
            "Create practice questions from any topic and test your understanding."
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button(
            "Create a quiz →",
            key="dash_quiz",
            type="primary",
            use_container_width=True
        ):
            go_to("AI Quiz")
            st.rerun()

    with c2:
        feature_card(
            "📄", "PDF Notes",
            "Turn your study PDF into structured, readable notes."
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button(
            "Make notes →",
            key="dash_notes",
            type="primary",
            use_container_width=True
        ):
            go_to("PDF Notes")
            st.rerun()

    with c3:
        feature_card(
            "💬", "Study Chat",
            "Ask questions and get explanations in simple language."
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button(
            "Ask a doubt →",
            key="dash_chat",
            type="primary",
            use_container_width=True
        ):
            go_to("Study Chat")
            st.rerun()

    st.markdown(
        '<div class="section-title">Recent activity</div>',
        unsafe_allow_html=True
    )

    st.markdown(f"""
    <div class="panel">
      <span class="status-chip">● SESSION STATUS</span>
      <div style="font-size:17px;font-weight:700;margin-top:13px">{escape(st.session_state.last_activity)}</div>
      <div style="color:#75819a;font-size:12px;margin-top:6px">Your activity is tracked while this app session is active.</div>
    </div>
    """, unsafe_allow_html=True)


elif st.session_state.page == "AI Quiz":
    show_heading(
        "AI Quiz Studio",
        "Generate topic-based practice questions for your next study session."
    )

    st.markdown(
        '<div class="panel"><div class="panel-title">Configure your quiz</div>'
        '<div class="panel-subtitle">Set the topic, difficulty and question format.</div>',
        unsafe_allow_html=True
    )

    topic = st.text_input(
        "Study topic",
        placeholder="e.g. BJT, C programming, Data Structures"
    )

    c1, c2 = st.columns(2)

    with c1:
        difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard", "Mixed"],
            index=1
        )
        question_type = st.selectbox(
            "Question format",
            ["MCQ", "Short Answer", "Mixed"]
        )

    with c2:
        question_count = st.selectbox(
            "Number of questions",
            [5, 10, 20, 30, 40, 50, 75, 100],
            index=2
        )
        language = st.selectbox(
            "Answer language",
            ["English", "Simple Hindi", "Hinglish"],
            index=0
        )

    extra_instructions = st.text_input(
        "Extra instructions (optional)",
        placeholder="e.g. Focus on formulas and exam-important concepts"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button(
        "✨ Generate my quiz",
        type="primary",
        use_container_width=True
    ):
        if not topic.strip():
            st.warning("Pehle study topic enter karo.")
        else:
            batch_size = 10
            batches = (question_count + batch_size - 1) // batch_size
            generated_parts = []
            progress = st.progress(0)
            status = st.empty()
            st.session_state.quiz_partial = False

            for batch_index in range(batches):
                start_num = batch_index * batch_size + 1
                end_num = min(
                    (batch_index + 1) * batch_size,
                    question_count
                )
                current_count = end_num - start_num + 1

                status.info(
                    f"Generating questions {start_num}–{end_num} "
                    f"of {question_count}..."
                )

                prompt = f"""
You are an expert tutor creating an accurate study quiz.

Topic: {topic}
Difficulty: {difficulty}
Question format: {question_type}
Language: {language}
Question numbers in this batch: {start_num} to {end_num}
Number of questions in this batch: {current_count}
Additional instructions: {extra_instructions or "None"}

Requirements:
1. Generate exactly {current_count} distinct questions for this batch.
2. Number questions from {start_num} to {end_num}.
3. For MCQ questions, provide four options labelled A, B, C, D and mark the correct answer.
4. For short-answer questions, provide a clear model answer.
5. For mixed format, use a sensible mix of MCQs and short-answer questions.
6. Explain the answer briefly where useful.
7. Keep the content relevant, correct and useful for students.
8. Do not repeat questions from earlier batches. Focus on different concepts.
9. Use readable headings and spacing.
10. Do not add an introduction or claim to generate more questions than requested.
"""

                result = ask_ai(
                    prompt,
                    max_tokens=5000,
                    temperature=0.4
                )

                if not result:
                    st.session_state.quiz_partial = bool(generated_parts)
                    break

                generated_parts.append(result)
                progress.progress(len(generated_parts) / batches)

            status.empty()
            progress.empty()

            if generated_parts:
                quiz_text = "\n\n".join(generated_parts)
                st.session_state.last_quiz = quiz_text
                st.session_state.quiz_topic = topic
                st.session_state.generated_quizzes += 1

                st.session_state.quiz_history.insert(0, {
                    "topic": topic,
                    "questions_requested": question_count,
                    "batches_generated": len(generated_parts),
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "difficulty": difficulty
                })

                st.session_state.last_activity = f"Generated quiz: {topic}"

                if st.session_state.quiz_partial:
                    st.warning(
                        f"Quiz partially generated. {len(generated_parts)} "
                        f"of {batches} batches completed. You can download "
                        "or use the generated questions below."
                    )
                else:
                    st.success(
                        f"Quiz generated! Requested {question_count} questions."
                    )
            else:
                st.error(
                    "Quiz generate nahi ho paya. API key, internet "
                    "connection ya provider limit check karo."
                )

    if st.session_state.last_quiz:
        st.markdown(
            '<div class="section-title">Your generated quiz</div>',
            unsafe_allow_html=True
        )
        st.caption(f"Topic: {st.session_state.quiz_topic}")
        st.markdown(st.session_state.last_quiz)

        st.download_button(
            "⬇️ Download quiz as TXT",
            data=st.session_state.last_quiz,
            file_name="study_buddy_quiz.txt",
            mime="text/plain",
            use_container_width=True
        )


elif st.session_state.page == "PDF Notes":
    show_heading(
        "PDF Notes Studio",
        "Transform your study material into clear, organised notes."
    )

    st.markdown(
        '<div class="panel"><div class="panel-title">Upload your study material</div>'
        '<div class="panel-subtitle">Select a text-based PDF to begin.</div>',
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"]
    )

    if uploaded_file is not None:
        pdf_text = extract_pdf_text(uploaded_file)

        if pdf_text:
            st.session_state.pdf_text = pdf_text
            st.success(
                f"PDF loaded successfully · {len(pdf_text.split())} words detected."
            )

            with st.expander("Preview extracted text"):
                st.text(pdf_text[:3000])
                if len(pdf_text) > 3000:
                    st.caption(
                        "Preview shortened. The full extracted text is "
                        "available to the note generator."
                    )
        else:
            st.warning(
                "PDF se readable text nahi mila. Agar PDF scanned image "
                "hai, toh OCR ki zaroorat ho sakti hai."
            )

    note_style = st.selectbox(
        "Notes style",
        [
            "Short Notes",
            "Detailed Notes",
            "Key Points",
            "Summary Notes",
            "Question–Answer Notes"
        ]
    )

    detail_level = st.select_slider(
        "Detail level",
        options=["Concise", "Balanced", "Detailed"],
        value="Balanced"
    )

    note_language = st.selectbox(
        "Notes language",
        ["English", "Simple Hindi", "Hinglish"]
    )

    note_instructions = st.text_input(
        "Special instructions (optional)",
        placeholder="e.g. Include definitions, formulas and exam questions"
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if st.button(
        "📚 Generate study notes",
        type="primary",
        use_container_width=True
    ):
        if not st.session_state.pdf_text:
            st.warning("Pehle readable PDF upload karo.")
        else:
            with st.spinner("PDF ko analyse karke notes banaye ja rahe hain..."):
                source_text = st.session_state.pdf_text[:26000]

                prompt = f"""
You are an expert academic note-maker.

Create study notes using the source text below.

Notes style: {note_style}
Detail level: {detail_level}
Language: {note_language}
Additional instructions: {note_instructions or "None"}

Rules:
1. Cover the important concepts in the supplied source.
2. Use clear headings and subheadings.
3. Explain concepts in student-friendly language.
4. Preserve important definitions, formulas, symbols and examples.
5. Use numbered steps for processes and bullet points for lists.
6. Do not invent facts that are not supported by the source.
7. For Question–Answer Notes, write clear questions followed by answers.
8. For Key Points, use concise bullet points.
9. Make the result useful for revision and examinations.
10. If the source is incomplete, state that briefly instead of inventing missing material.

SOURCE TEXT:
{source_text}
"""

                notes = ask_ai(
                    prompt,
                    max_tokens=6000,
                    temperature=0.3
                )

            if notes:
                st.session_state.last_notes = notes
                st.session_state.notes_created += 1

                st.session_state.notes_history.insert(0, {
                    "style": note_style,
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "words": len(notes.split())
                })

                st.session_state.last_activity = f"Created {note_style.lower()}"

                if len(st.session_state.pdf_text) > 26000:
                    st.info(
                        "Large PDF hai, isliye first section of extracted "
                        "text was sent to the AI. Check that your important "
                        "chapters are included."
                    )

                st.success("Notes ready!")

    if st.session_state.last_notes:
        st.markdown(
            '<div class="section-title">Your study notes</div>',
            unsafe_allow_html=True
        )
        st.markdown(st.session_state.last_notes)

        c1, c2 = st.columns(2)

        with c1:
            st.download_button(
                "⬇️ Download TXT",
                data=st.session_state.last_notes,
                file_name="study_buddy_notes.txt",
                mime="text/plain",
                use_container_width=True
            )

        with c2:
            try:
                pdf_data = make_pdf(st.session_state.last_notes)

                st.download_button(
                    "📄 Download PDF",
                    data=pdf_data,
                    file_name="study_buddy_notes.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF export fail hua: {e}")


elif st.session_state.page == "Study Chat":
    show_heading(
        "Study Chat",
        "Ask doubts, explore concepts and get step-by-step explanations."
    )

    st.markdown("""
    <div class="panel">
      <div class="panel-title">💬 Your AI tutor</div>
      <div class="panel-subtitle">Ask one question at a time for focused explanations.</div>
      <span class="status-chip">● GROQ AI CONNECTED THROUGH API</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("＋ New chat", key="new_chat"):
        st.session_state.chat_messages = []
        st.session_state.last_activity = "Started a new chat"
        st.rerun()

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input(
        "Ask your study question...",
        key="study_chat_input"
    )

    if user_prompt:
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_prompt
        })

        with st.chat_message("user"):
            st.markdown(user_prompt)

        history = st.session_state.chat_messages[-11:]

        messages = [{
            "role": "system",
            "content": (
                "You are Study Buddy AI, a helpful academic tutor. "
                "Explain concepts clearly in simple student-friendly language. "
                "Use headings, examples, formulas and step-by-step reasoning when helpful. "
                "If the user asks for code, provide complete working code and explain it simply. "
                "Do not invent facts. If a question is ambiguous, state your assumption."
            )
        }]

        messages.extend(history)

        client = get_client()
        answer = None

        if client:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = client.chat.completions.create(
                            model=MODEL,
                            messages=messages,
                            max_tokens=3000,
                            temperature=0.4
                        )
                        answer = response.choices[0].message.content

                    except Exception as e:
                        st.error(f"Chat response nahi aa paya: {e}")

                if answer:
                    st.markdown(answer)

        if answer:
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": answer
            })

            st.session_state.last_activity = "Used Study Chat"
            st.rerun() 

elif st.session_state.page == "Performance":
    show_heading(
        "Your Performance",
        "Track the study activities completed in this session."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("🧠", st.session_state.generated_quizzes, "Quizzes created")

    with c2:
        metric_card("📚", st.session_state.notes_created, "Notes created")

    with c3:
        metric_card("💬", len(st.session_state.chat_messages), "Chat messages")

    st.markdown(
        '<div class="section-title">Quiz history</div>',
        unsafe_allow_html=True
    )

    if st.session_state.quiz_history:
        for item in st.session_state.quiz_history:
            st.markdown(f"""
            <div class="panel">
              <div style="font-size:16px;font-weight:800">{escape(item['topic'])}</div>
              <div style="color:#75819a;font-size:12px;margin-top:8px">
                {item['questions_requested']} questions requested ·
                {escape(item['difficulty'])} ·
                {item['batches_generated']} batches ·
                {escape(item['date'])}
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(
            "Abhi quiz history nahi hai. AI Quiz section se apna pehla quiz banao."
        )

    st.markdown(
        '<div class="section-title">Notes history</div>',
        unsafe_allow_html=True
    )

    if st.session_state.notes_history:
        for item in st.session_state.notes_history:
            st.markdown(f"""
            <div class="panel">
              <div style="font-size:16px;font-weight:800">{escape(item['style'])}</div>
              <div style="color:#75819a;font-size:12px;margin-top:8px">
                {item['words']} words · {escape(item['date'])}
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info(
            "Abhi notes history nahi hai. PDF Notes section se notes generate karo."
        )

    st.caption(
        "Note: Performance data currently stays in the active app session "
        "and may reset when the session restarts."
    )


elif st.session_state.page == "Settings":
    show_heading(
        "Settings",
        "Manage your study workspace and app information."
    )

    st.markdown("""
    <div class="panel">
      <div class="panel-title">🎨 Interface</div>
      <div class="panel-subtitle">A clean workspace designed for focused learning.</div>
      <span class="status-chip">PREMIUM STUDY WORKSPACE</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="panel">
      <div class="panel-title">🤖 AI configuration</div>
      <div class="panel-subtitle">Study Buddy AI uses the Groq API with the configured model.</div>
      <div style="font-weight:700">Model</div>
      <code>openai/gpt-oss-20b</code>
      <div style="height:12px"></div>
      <div style="font-weight:700">API key</div>
      <div style="color:#75819a;font-size:13px">Read from Streamlit Secrets. The key is not displayed in the app.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="section-title">Data management</div>',
        unsafe_allow_html=True
    )

    st.warning(
        "Clearing history will remove session data. This action cannot be undone."
    )

    c1, c2 = st.columns(2)

    with c1:
        if st.button(
            "🗑️ Clear quiz and notes history",
            use_container_width=True
        ):
            st.session_state.quiz_history = []
            st.session_state.notes_history = []
            st.session_state.generated_quizzes = 0
            st.session_state.notes_created = 0
            st.session_state.last_quiz = ""
            st.session_state.last_notes = ""
            st.session_state.quiz_partial = False
            st.session_state.last_activity = "Quiz and notes history cleared"

            st.success("Quiz aur notes history clear ho gayi.")
            st.rerun()

    with c2:
        if st.button("🧹 Clear chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.session_state.last_activity = "Chat history cleared"
            st.success("Chat history clear ho gayi.")
            st.rerun()

    st.markdown(
        '<div class="section-title">About</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="panel">
      <div style="font-size:20px;font-weight:800">Study Buddy AI 🎓</div>
      <div style="color:#75819a;font-size:13px;line-height:1.8;margin-top:8px">
        A student-focused learning workspace with AI quiz generation,
        PDF-based notes, conversational doubt solving and session performance tracking.
      </div>
    </div>
    """, unsafe_allow_html=True)


st.markdown("""
<div class="footer">
  STUDY BUDDY AI · Learn at your own pace · Keep making progress ✦
</div>
""", unsafe_allow_html=True)