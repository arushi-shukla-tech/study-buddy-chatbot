import streamlit as st
from groq import Groq
from pypdf import PdfReader
from io import BytesIO
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from xml.sax.saxutils import escape
import json
import re
import html

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --green: #405D4B;
    --green-dark: #2E4537;
    --sage: #E8EEE7;
    --paper: #F7F8F5;
    --ink: #252C27;
    --muted: #788178;
    --line: #E4E8E1;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--ink);
}

.stApp {
    background: var(--paper);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: #FFFFFF;
    border-right: 1px solid var(--line);
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #58645A;
}

h1, h2, h3 {
    font-family: 'Manrope', sans-serif !important;
    letter-spacing: -0.6px;
    color: var(--ink);
}

h1 { font-weight: 800 !important; }
h2, h3 { font-weight: 700 !important; }

.block-container {
    max-width: 1440px;
    padding-top: 1.6rem;
    padding-bottom: 3rem;
}

[data-testid="stMetric"] {
    background: #FFFFFF;
    padding: 20px;
    border: 1px solid var(--line);
    border-radius: 17px;
}

[data-testid="stMetricLabel"] {
    color: var(--muted);
}

[data-testid="stMetricValue"] {
    color: var(--green-dark);
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 600;
    border: 1px solid #DCE3DA;
    transition: 0.2s ease;
}

.stButton > button[kind="primary"],
.stDownloadButton > button[kind="primary"] {
    background: var(--green);
    color: white;
    border: 1px solid var(--green);
}

.stButton > button:hover {
    border-color: var(--green);
    color: var(--green-dark);
}

.stButton > button[kind="primary"]:hover {
    background: var(--green-dark);
    color: white;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox [data-baseweb="select"],
.stNumberInput input {
    border-radius: 10px;
}

[data-testid="stFileUploader"] {
    background: #FFFFFF;
    border: 1px dashed #BAC9BA;
    border-radius: 15px;
    padding: 10px;
}

[data-testid="stExpander"] {
    background: #FFFFFF;
    border: 1px solid var(--line);
    border-radius: 12px;
}

.hero {
    position: relative;
    overflow: hidden;
    border-radius: 24px;
    min-height: 300px;
    display: flex;
    align-items: center;
    padding: 38px;
    color: white;
    background:
      linear-gradient(90deg, rgba(27,47,35,.96) 0%,
      rgba(37,62,46,.86) 48%, rgba(37,62,46,.12) 100%),
      url("https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1800&q=85")
      center/cover;
    margin-bottom: 25px;
}

.hero-content {
    max-width: 590px;
}

.eyebrow {
    display: inline-block;
    background: rgba(255,255,255,.14);
    border: 1px solid rgba(255,255,255,.25);
    padding: 7px 12px;
    border-radius: 30px;
    font-size: 12px;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #E6F0E5;
    margin-bottom: 15px;
}

.hero h1 {
    color: white !important;
    font-size: clamp(30px, 4vw, 48px);
    line-height: 1.13;
    margin: 0 0 12px 0;
}

.hero p {
    color: #E2E9E0;
    font-size: 15px;
    line-height: 1.8;
    max-width: 480px;
    margin: 0;
}

.section-label {
    color: var(--green);
    font-size: 12px;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 1.4px;
    margin-bottom: 6px;
}

.feature-card {
    background: white;
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 22px;
    min-height: 190px;
    height: 100%;
}

.feature-icon {
    display: inline-flex;
    width: 47px;
    height: 47px;
    border-radius: 14px;
    align-items: center;
    justify-content: center;
    background: var(--sage);
    font-size: 23px;
    margin-bottom: 17px;
}

.feature-card h3 {
    font-size: 17px;
    margin: 0 0 8px 0;
}

.feature-card p {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.7;
    margin: 0;
}

.panel {
    background: white;
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 16px;
}

.small-muted {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.7;
}

div[data-testid="stProgressBar"] > div > div {
    background-color: var(--green);
}

hr {
    border-color: var(--line);
}

@media (max-width: 700px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .hero {
        padding: 25px;
        min-height: 270px;
    }
    [data-testid="stMetric"] {
        padding: 12px;
    }
}
</style>
""", unsafe_allow_html=True)

DEFAULT_MODEL = "openai/gpt-oss-20b"

def initialize_state():
    defaults = {
        "page": "Dashboard",
        "quiz": [],
        "quiz_answers": {},
        "quiz_result": None,
        "quiz_history": [],
        "pdf_text": "",
        "pdf_name": "",
        "pdf_output": "",
        "chat_history": [],
        "activities": [],
        "quiz_topic": "",
        "quiz_subject": "General",
        "quiz_count": 10,
        "quiz_difficulty": "Medium",
        "quiz_language": "Simple English",
        "last_quiz": None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_state()

def get_api_key():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return st.session_state.get("manual_api_key", "")

def get_client():
    key = get_api_key()
    if not key:
        return None
    return Groq(api_key=key)

def ask_ai(prompt, system=None, temperature=0.4, max_tokens=3500):
    client = get_client()
    if client is None:
        raise ValueError(
            "Groq API key is missing. Add GROQ_API_KEY in Streamlit Secrets."
        )

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()

def log_activity(label):
    st.session_state.activities.insert(0, {
        "activity": label,
        "time": datetime.now().strftime("%d %b %Y, %I:%M %p")
    })
    st.session_state.activities = st.session_state.activities[:50]

def extract_json(text):
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}|\[.*\]", text, flags=re.DOTALL)
    if match:
        return json.loads(match.group(0))

    raise ValueError("AI returned an invalid response. Please try again.")

def generate_quiz_batch(topic, subject, count, difficulty, language):
    prompt = f"""
Create exactly {count} multiple-choice questions for a student.

Subject: {subject}
Topic: {topic}
Difficulty: {difficulty}
Language: {language}

Rules:
- Each question must have exactly four options.
- Only one option must be correct.
- Use clear, educational questions.
- Do not repeat questions.
- Give a short explanation for the correct answer.
- Return valid JSON only, with no Markdown.

Required JSON format:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": 0,
      "explanation": "Short explanation"
    }}
  ]
}}
The answer field must be a zero-based integer from 0 to 3.
"""
    raw = ask_ai(
        prompt,
        system="You are an accurate educational question writer. Return valid JSON only.",
        temperature=0.3,
        max_tokens=max(2500, count * 250)
    )
    data = extract_json(raw)
    questions = data.get("questions", []) if isinstance(data, dict) else data

    valid = []
    for q in questions:
        if not isinstance(q, dict):
            continue
        options = q.get("options", [])
        answer = q.get("answer")
        if not isinstance(options, list) or len(options) != 4:
            continue
        try:
            answer = int(answer)
        except (ValueError, TypeError):
            continue
        if not 0 <= answer <= 3:
            continue
        if not q.get("question"):
            continue

        valid.append({
            "question": str(q["question"]),
            "options": [str(x) for x in options],
            "answer": answer,
            "explanation": str(q.get("explanation", "Review the correct concept."))
        })

    return valid

def make_pdf(text, title="Study Buddy AI Notes"):
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=(8.27 * inch, 11.69 * inch),
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=26,
        textColor=colors.HexColor("#405D4B"),
        spaceAfter=18
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#303730"),
        spaceAfter=8
    )
    story = [Paragraph(escape(title), title_style)]

    for line in text.splitlines():
        safe_line = escape(line) if line.strip() else "&nbsp;"
        story.append(Paragraph(safe_line, body_style))
        story.append(Spacer(1, 3))

    document.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def download_buttons(text, filename, title):
    st.download_button(
        "Download TXT",
        data=text.encode("utf-8"),
        file_name=filename + ".txt",
        mime="text/plain",
        use_container_width=True
    )
    pdf_data = make_pdf(text, title)
    st.download_button(
        "Download PDF",
        data=pdf_data,
        file_name=filename + ".pdf",
        mime="application/pdf",
        use_container_width=True
    )

def hero(title, subtitle, eyebrow="YOUR PERSONAL LEARNING SPACE"):
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)
    safe_eyebrow = html.escape(eyebrow)
    st.markdown(f"""
    <div class="hero">
      <div class="hero-content">
        <div class="eyebrow">{safe_eyebrow}</div>
        <h1>{safe_title}</h1>
        <p>{safe_subtitle}</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

def feature_card(icon, title, description):
    st.markdown(f"""
    <div class="feature-card">
      <div class="feature-icon">{icon}</div>
      <h3>{html.escape(title)}</h3>
      <p>{html.escape(description)}</p>
    </div>
    """, unsafe_allow_html=True)

def page_title(title, description):
    st.title(title)
    st.markdown(f'<p class="small-muted">{html.escape(description)}</p>',
                unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 📚 Study Buddy AI")
    st.caption("A smarter way to study")
    st.divider()

    pages = [
        "Dashboard",
        "AI Quiz",
        "PDF Notes",
        "Study Chat",
        "Performance",
        "Settings"
    ]

    selected_page = st.radio(
        "WORKSPACE",
        pages,
        index=pages.index(st.session_state.page)
        if st.session_state.page in pages else 0
    )
    st.session_state.page = selected_page

    st.divider()
    if get_api_key():
        st.success("AI connection key found")
    else:
        st.warning("API key not configured")

    st.markdown(
        '<p class="small-muted">Learn at your own pace. '
        'Your workspace, your progress.</p>',
        unsafe_allow_html=True
    )

page = st.session_state.page

if page == "Dashboard":
    hero(
        "Make every study session count.",
        "Turn your notes into knowledge. Create practice quizzes, "
        "understand difficult topics and build better study habits.",
        "WELCOME TO YOUR LEARNING WORKSPACE"
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Quizzes completed", len(st.session_state.quiz_history))
    col2.metric("Notes uploaded", 1 if st.session_state.pdf_text else 0)
    col3.metric("Chat messages", len(st.session_state.chat_history))

    st.markdown("### Your workspace")
    st.markdown(
        '<p class="small-muted">Everything you need, in one place.</p>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3, gap="medium")
    with c1:
        feature_card("✦", "AI Quiz", "Build topic-based practice tests and review every answer.")
        if st.button("Create a quiz", key="dash_quiz", use_container_width=True):
            st.session_state.page = "AI Quiz"
            st.rerun()

    with c2:
        feature_card("▤", "PDF Notes", "Upload study material and turn it into useful revision notes.")
        if st.button("Open PDF Notes", key="dash_pdf", use_container_width=True):
            st.session_state.page = "PDF Notes"
            st.rerun()

    with c3:
        feature_card("✎", "Study Chat", "Ask questions and learn difficult concepts step by step.")
        if st.button("Start studying", key="dash_chat", use_container_width=True):
            st.session_state.page = "Study Chat"
            st.rerun()

    c4, c5, c6 = st.columns(3, gap="medium")
    with c4:
        feature_card("◷", "Performance", "Review previous scores and follow your learning progress.")
        if st.button("View performance", key="dash_perf", use_container_width=True):
            st.session_state.page = "Performance"
            st.rerun()

    with c5:
        feature_card("◎", "Personal learning", "Choose your preferred language and difficulty.")
        if st.button("Study settings", key="dash_settings", use_container_width=True):
            st.session_state.page = "Settings"
            st.rerun()

    with c6:
        feature_card("↗", "Learn from PDFs", "Generate summaries, key points and practice questions.")
        if st.button("Explore notes", key="dash_notes", use_container_width=True):
            st.session_state.page = "PDF Notes"
            st.rerun()

    st.markdown("### Recent activity")
    if st.session_state.activities:
        for item in st.session_state.activities[:5]:
            st.markdown(
                f"**{html.escape(item['activity'])}**  \n"
                f"<span class='small-muted'>{html.escape(item['time'])}</span>",
                unsafe_allow_html=True
            )
    else:
        st.info("Your recent study activities will appear here.")

elif page == "AI Quiz":
    hero(
        "Practice with purpose.",
        "Generate questions for your topic, test your understanding and "
        "learn from every answer.",
        "PERSONALISED PRACTICE"
    )

    with st.form("quiz_setup"):
        col1, col2 = st.columns(2)
        with col1:
            subject = st.text_input(
                "Subject",
                value=st.session_state.quiz_subject,
                placeholder="e.g. Applied Chemistry"
            )
            topic = st.text_input(
                "Topic",
                value=st.session_state.quiz_topic,
                placeholder="e.g. Nernst equation"
            )
            difficulty = st.selectbox(
                "Difficulty",
                ["Easy", "Medium", "Hard", "Mixed"],
                index=["Easy", "Medium", "Hard", "Mixed"].index(
                    st.session_state.quiz_difficulty
                )
            )
        with col2:
            count = st.select_slider(
                "Number of questions",
                options=[5, 10, 15, 20, 30, 40, 50, 75, 100],
                value=st.session_state.quiz_count
            )
            language = st.selectbox(
                "Question language",
                ["Simple English", "Hinglish", "Detailed English"],
                index=["Simple English", "Hinglish", "Detailed English"].index(
                    st.session_state.quiz_language
                )
            )

        generate = st.form_submit_button(
            "Generate practice quiz",
            type="primary",
            use_container_width=True
        )

    if generate:
        if not topic.strip():
            st.error("Please enter a topic first.")
        elif not get_api_key():
            st.error("Add your Groq API key in Settings before generating a quiz.")
        else:
            st.session_state.quiz_subject = subject.strip() or "General"
            st.session_state.quiz_topic = topic.strip()
            st.session_state.quiz_difficulty = difficulty
            st.session_state.quiz_count = count
            st.session_state.quiz_language = language

            collected = []
            failed = False
            progress = st.progress(0)
            status = st.empty()

            try:
                batches = (count + 9) // 10
                for batch_index in range(batches):
                    amount = min(10, count - len(collected))
                    status.write(
                        f"Creating questions: batch {batch_index + 1} of {batches}..."
                    )
                    batch = generate_quiz_batch(
                        topic.strip(),
                        subject.strip() or "General",
                        amount,
                        difficulty,
                        language
                    )
                    collected.extend(batch)
                    progress.progress(min(1.0, len(collected) / count))

                if len(collected) < count:
                    status.warning(
                        f"The AI returned {len(collected)} valid questions "
                        f"instead of {count}. You can try again."
                    )
                    failed = True

                if collected:
                    st.session_state.quiz = collected[:count]
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_result = None
                    st.session_state.last_quiz = {
                        "topic": topic.strip(),
                        "subject": subject.strip() or "General",
                        "difficulty": difficulty,
                        "date": datetime.now().strftime("%d %b %Y, %I:%M %p")
                    }
                    log_activity(f"Generated quiz: {topic.strip()}")

                status.empty()
                progress.empty()

                if failed:
                    st.warning("A partial quiz is available below.")
                elif collected:
                    st.success(f"Created {len(collected)} questions.")
            except Exception as e:
                progress.empty()
                status.empty()
                st.error(f"Quiz generation failed: {e}")

    if st.session_state.quiz:
        st.divider()
        st.subheader(
            f"Practice quiz: {st.session_state.last_quiz['topic']}"
            if st.session_state.last_quiz else "Practice quiz"
        )
        st.caption(
            f"{len(st.session_state.quiz)} questions · "
            "Choose one answer for each question."
        )

        if st.session_state.quiz_result is None:
            with st.form("quiz_answers_form"):
                selected_answers = {}
                for i, question in enumerate(st.session_state.quiz):
                    st.markdown(f"**Q{i + 1}. {question['question']}**")
                    selected_answers[i] = st.radio(
                        "Choose your answer",
                        options=list(range(4)),
                        format_func=lambda x, opts=question["options"]: opts[x],
                        key=f"quiz_answer_{i}",
                        index=None
                    )
                    st.markdown("---")

                submitted = st.form_submit_button(
                    "Submit quiz",
                    type="primary",
                    use_container_width=True
                )

            if submitted:
                score = 0
                answers = {}
                for i, question in enumerate(st.session_state.quiz):
                    chosen = selected_answers.get(i)
                    answers[i] = chosen
                    if chosen == question["answer"]:
                        score += 1

                total = len(st.session_state.quiz)
                percentage = round(score / total * 100) if total else 0

                result = {
                    "score": score,
                    "total": total,
                    "percentage": percentage,
                    "answers": answers,
                    "topic": st.session_state.last_quiz["topic"]
                    if st.session_state.last_quiz else "Practice quiz",
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p")
                }
                st.session_state.quiz_answers = answers
                st.session_state.quiz_result = result
                st.session_state.quiz_history.insert(0, result)
                st.session_state.quiz_history = st.session_state.quiz_history[:100]
                log_activity(f"Completed quiz: {result['topic']}")
                st.rerun()

        else:
            result = st.session_state.quiz_result
            m1, m2, m3 = st.columns(3)
            m1.metric("Your score", f"{result['score']}/{result['total']}")
            m2.metric("Percentage", f"{result['percentage']}%")
            m3.metric(
                "Incorrect or unanswered",
                result["total"] - result["score"]
            )

            st.progress(result["percentage"] / 100)

            if result["percentage"] >= 80:
                st.success("Excellent work! Review the explanations to strengthen your knowledge.")
            elif result["percentage"] >= 50:
                st.info("Good effort. Review the questions you missed and try again.")
            else:
                st.warning("Keep practising. Read the explanations and try another quiz.")

            st.subheader("Answer review")
            for i, question in enumerate(st.session_state.quiz):
                chosen = result["answers"].get(i)
                correct = question["answer"]
                with st.expander(f"Question {i + 1}: {question['question']}"):
                    if chosen == correct:
                        st.success("Your answer is correct.")
                    else:
                        st.error("Your answer is incorrect or unanswered.")

                    st.write(
                        "**Your answer:** " +
                        (question["options"][chosen] if chosen is not None else "Not answered")
                    )
                    st.write("**Correct answer:** " + question["options"][correct])
                    st.write("**Explanation:** " + question["explanation"])

            result_text = (
                f"Study Buddy AI Quiz Results\n"
                f"Topic: {result['topic']}\n"
                f"Score: {result['score']}/{result['total']}\n"
                f"Percentage: {result['percentage']}%\n\n"
            )
            for i, question in enumerate(st.session_state.quiz):
                chosen = result["answers"].get(i)
                result_text += f"Q{i + 1}. {question['question']}\n"
                result_text += f"Correct answer: {question['options'][question['answer']]}\n"
                result_text += f"Explanation: {question['explanation']}\n\n"

            st.download_button(
                "Download quiz results",
                data=result_text,
                file_name="study_buddy_quiz_results.txt",
                mime="text/plain",
                use_container_width=True
            )

            if st.button("Create another quiz", type="primary", use_container_width=True):
                st.session_state.quiz = []
                st.session_state.quiz_answers = {}
                st.session_state.quiz_result = None
                st.rerun()

elif page == "PDF Notes":
    hero(
        "Your notes, made clearer.",
        "Upload a PDF and transform study material into summaries, "
        "important concepts, revision notes and practice questions.",
        "SMART NOTE WORKSPACE"
    )

    uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"])

    if uploaded_file is not None:
        if st.session_state.pdf_name != uploaded_file.name:
            try:
                reader = PdfReader(uploaded_file)
                extracted = []
                for page_number, pdf_page in enumerate(reader.pages):
                    extracted.append(pdf_page.extract_text() or "")

                st.session_state.pdf_text = "\n".join(extracted).strip()
                st.session_state.pdf_name = uploaded_file.name
                st.session_state.pdf_output = ""

                if not st.session_state.pdf_text:
                    st.warning(
                        "No selectable text was found. This may be a scanned PDF "
                        "that needs OCR before it can be processed."
                    )
                else:
                    st.success(
                        f"Loaded {len(reader.pages)} pages from {uploaded_file.name}."
                    )
            except Exception as e:
                st.error(f"Could not read this PDF: {e}")

    if st.session_state.pdf_text:
        st.markdown("### Document details")
        st.markdown(
            f'<div class="panel"><strong>{html.escape(st.session_state.pdf_name)}</strong>'
            f'<p class="small-muted">{len(st.session_state.pdf_text):,} characters extracted</p></div>',
            unsafe_allow_html=True
        )

        action = st.selectbox(
            "What would you like to create?",
            [
                "Complete summary",
                "Exam-ready notes",
                "Important questions with answers",
                "Quick revision points",
                "Explain in simple language",
                "Practice MCQs"
            ]
        )

        language = st.selectbox(
            "Output language",
            ["Simple English", "Hinglish", "Detailed English"],
            key="pdf_language"
        )

        if st.button("Generate study material", type="primary", use_container_width=True):
            if not get_api_key():
                st.error("Add your Groq API key in Settings first.")
            else:
                try:
                    with st.spinner("Reading your notes and preparing study material..."):
                        source_text = st.session_state.pdf_text[:24000]
                        prompt = f"""
Use the following PDF text as the main source.

Task: {action}
Output language: {language}

Instructions:
- Cover the important information present in the supplied text.
- Do not invent facts that are not supported by the source.
- Use clear headings and readable paragraphs.
- For exam notes, use definitions, key points and examples where relevant.
- For questions, provide answers too.
- For practice MCQs, provide four options and clearly identify the correct answer.
- If the source is incomplete, state that clearly.

PDF text:
{source_text}
"""
                        output = ask_ai(
                            prompt,
                            system="You are a careful study-notes assistant. Be accurate and well organised.",
                            temperature=0.3,
                            max_tokens=5000
                        )
                        st.session_state.pdf_output = output
                        log_activity(f"Generated PDF material: {action}")
                except Exception as e:
                    st.error(f"Could not generate notes: {e}")

    if st.session_state.pdf_output:
        st.divider()
        st.subheader("Your study material")
        st.markdown(st.session_state.pdf_output)
        download_buttons(
            st.session_state.pdf_output,
            "study_buddy_notes",
            "Study Buddy AI Notes"
        )

elif page == "Study Chat":
    hero(
        "Let's understand it together.",
        "Ask about a concept, solve a doubt or request a step-by-step "
        "explanation in your preferred learning style.",
        "YOUR AI STUDY ASSISTANT"
    )

    language = st.selectbox(
        "Explanation style",
        ["Simple English", "Hinglish", "Detailed English"],
        key="chat_language"
    )

    if st.button("Clear conversation"):
        st.session_state.chat_history = []
        st.rerun()

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_message = st.chat_input("Ask a question about your studies...")

    if user_message:
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_message
        })

        with st.chat_message("user"):
            st.markdown(user_message)

        with st.chat_message("assistant"):
            try:
                client = get_client()
                if client is None:
                    raise ValueError("Add your Groq API key in Settings first.")

                recent = st.session_state.chat_history[-12:]
                system_message = (
                    "You are Study Buddy AI, a helpful educational tutor. "
                    f"Respond in {language}. "
                    "Explain step by step when useful. "
                    "Use clear headings and examples. "
                    "For programming questions, provide complete correct code "
                    "when requested. Do not make up facts."
                )

                messages = [{"role": "system", "content": system_message}]
                messages.extend(recent)

                with st.spinner("Preparing your explanation..."):
                    response = client.chat.completions.create(
                        model=DEFAULT_MODEL,
                        messages=messages,
                        temperature=0.4,
                        max_tokens=3000
                    )

                answer = response.choices[0].message.content.strip()
                st.markdown(answer)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer
                })
                log_activity("Asked a question in Study Chat")

            except Exception as e:
                st.error(f"Could not get a response: {e}")
                st.session_state.chat_history.pop()

elif page == "Performance":
    hero(
        "Your progress, at a glance.",
        "Review your completed quizzes, track your scores and identify "
        "topics that deserve more practice.",
        "LEARNING INSIGHTS"
    )

    history = st.session_state.quiz_history
    if not history:
        st.info("Complete an AI quiz to start building your performance history.")
    else:
        total_quizzes = len(history)
        percentages = [x["percentage"] for x in history]
        average = round(sum(percentages) / len(percentages))
        best = max(percentages)

        c1, c2, c3 = st.columns(3)
        c1.metric("Completed quizzes", total_quizzes)
        c2.metric("Average score", f"{average}%")
        c3.metric("Best score", f"{best}%")

        st.subheader("Score history")
        chart_data = [
            {
                "Quiz": f"{i + 1}. {item['topic'][:24]}",
                "Score (%)": item["percentage"]
            }
            for i, item in enumerate(reversed(history[-10:]))
        ]
        st.bar_chart(chart_data, x="Quiz", y="Score (%)")

        st.subheader("Recent quizzes")
        for item in history[:20]:
            with st.expander(
                f"{item['topic']} — {item['percentage']}% · {item['date']}"
            ):
                st.write(f"Score: {item['score']}/{item['total']}")
                st.progress(item["percentage"] / 100)

        export_text = "Study Buddy AI - Performance History\n\n"
        for item in history:
            export_text += (
                f"Topic: {item['topic']}\n"
                f"Score: {item['score']}/{item['total']}\n"
                f"Percentage: {item['percentage']}%\n"
                f"Date: {item['date']}\n\n"
            )

        st.download_button(
            "Export performance history",
            data=export_text,
            file_name="study_buddy_performance.txt",
            mime="text/plain",
            use_container_width=True
        )

elif page == "Settings":
    hero(
        "Make it work for you.",
        "Configure your AI connection and choose how you want to use "
        "your personal learning workspace.",
        "WORKSPACE SETTINGS"
    )

    st.subheader("AI connection")
    st.markdown(
        "Study Buddy AI uses Groq to generate questions, prepare notes "
        "and answer study questions."
    )

    st.markdown("**Recommended: Streamlit Secrets**")
    st.markdown(
        "Open your app in Streamlit Cloud → Settings → Secrets, "
        "then add the following line:"
    )
    st.code('GROQ_API_KEY = "your_groq_api_key_here"', language="toml")

    st.markdown(
        "Keep the real API key private. Do not paste it into public GitHub files."
    )

    with st.expander("Use a temporary key for this session"):
        manual_key = st.text_input(
            "Groq API key",
            type="password",
            value=st.session_state.get("manual_api_key", ""),
            help="Stored only in this running Streamlit session."
        )
        if st.button("Save key for this session", type="primary"):
            st.session_state.manual_api_key = manual_key.strip()
            st.success("Key saved for this session.")
            st.rerun()

    if st.button("Test AI connection", use_container_width=True):
        if not get_api_key():
            st.error("No API key found. Configure it above.")
        else:
            try:
                with st.spinner("Testing connection..."):
                    test = ask_ai(
                        "Reply with exactly: Connection successful.",
                        max_tokens=50
                    )
                st.success(f"AI connection is working: {test}")
            except Exception as e:
                st.error(f"Connection test failed: {e}")

    st.divider()
    st.subheader("Workspace information")
    st.write("Application: Study Buddy AI")
    st.write("Interface: Sage Green + Off-White")
    st.write("AI provider: Groq")
    st.write("Quiz generation: Batch-based, up to 100 requested questions")

    st.caption(
        "Session history is stored in memory and may reset when the app restarts. "
        "Generated answers can contain mistakes, so verify important academic information."
    )

st.markdown("---")
st.markdown(
    '<p class="small-muted" style="text-align:center;">'
    'Study Buddy AI · Learn clearly. Practise consistently. Grow confidently.'
    '</p>',
    unsafe_allow_html=True
)
