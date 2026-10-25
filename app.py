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
    initial_sidebar_state="expanded",
    menu_items={}
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

.stApp { background: var(--paper); }

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

[data-testid="stMetricLabel"] { color: var(--muted); }

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

.hero-content { max-width: 590px; }

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

hr { border-color: var(--line); }

@media (max-width: 700px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .hero {
        padding: 25px;
        min-height: 270px;
    }
    [data-testid="stMetric"] { padding: 12px; }
}
</style>
""", unsafe_allow_html=True)

MODEL = "openai/gpt-oss-20b"

def init_state():
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
        "last_quiz": None,
        "manual_api_key": ""
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()

def api_key():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return st.session_state.manual_api_key

def client():
    key = api_key()
    if not key:
        return None
    return Groq(api_key=key)

def ai(prompt, system="You are a helpful educational assistant.", max_tokens=3000):
    connection = client()
    if connection is None:
        raise ValueError("Configure your Groq API key in Settings.")
    response = connection.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()

def activity(text):
    st.session_state.activities.insert(0, {
        "text": text,
        "time": datetime.now().strftime("%d %b %Y, %I:%M %p")
    })
    st.session_state.activities = st.session_state.activities[:50]

def hero(title, subtitle, label="YOUR LEARNING WORKSPACE"):
    st.markdown(f"""
    <div class="hero">
      <div class="hero-content">
        <div class="eyebrow">{html.escape(label)}</div>
        <h1>{html.escape(title)}</h1>
        <p>{html.escape(subtitle)}</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

def feature(icon, title, description):
    st.markdown(f"""
    <div class="feature-card">
      <div class="feature-icon">{icon}</div>
      <h3>{html.escape(title)}</h3>
      <p>{html.escape(description)}</p>
    </div>
    """, unsafe_allow_html=True)

def parse_json(text):
    cleaned = re.sub(r"```(?:json)?", "", text, flags=re.I).replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}|\[.*\]", cleaned, re.S)
        if match:
            return json.loads(match.group(0))
    raise ValueError("The AI returned invalid JSON. Please try again.")

def generate_batch(topic, subject, count, difficulty, language):
    prompt = f"""
Create exactly {count} multiple-choice questions.

Subject: {subject}
Topic: {topic}
Difficulty: {difficulty}
Language: {language}

Return JSON only:
{{
 "questions": [
  {{
   "question": "Question",
   "options": ["A", "B", "C", "D"],
   "answer": 0,
   "explanation": "Short explanation"
  }}
 ]
}}

Rules:
- Four options for each question.
- answer is a zero-based integer from 0 to 3.
- One correct answer only.
- Do not repeat questions.
- Make the questions educational and accurate.
"""
    result = parse_json(ai(
        prompt,
        system="You create accurate quizzes for students. Return valid JSON only.",
        max_tokens=max(2500, count * 250)
    ))
    questions = result.get("questions", []) if isinstance(result, dict) else result
    valid = []

    for item in questions:
        if not isinstance(item, dict):
            continue
        options = item.get("options")
        try:
            answer = int(item.get("answer"))
        except (TypeError, ValueError):
            continue

        if not isinstance(options, list) or len(options) != 4:
            continue
        if answer not in range(4) or not item.get("question"):
            continue

        valid.append({
            "question": str(item["question"]),
            "options": [str(option) for option in options],
            "answer": answer,
            "explanation": str(item.get("explanation", "Review the topic again."))
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
    heading = ParagraphStyle(
        "SBHeading",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=26,
        textColor=colors.HexColor("#405D4B"),
        spaceAfter=18
    )
    body = ParagraphStyle(
        "SBBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#303730"),
        spaceAfter=8
    )
    story = [Paragraph(escape(title), heading)]
    for line in text.splitlines():
        story.append(Paragraph(escape(line) if line.strip() else "&nbsp;", body))
        story.append(Spacer(1, 3))
    document.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def download_material(text, name, title):
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download TXT",
            data=text.encode("utf-8"),
            file_name=name + ".txt",
            mime="text/plain",
            use_container_width=True
        )
    with col2:
        st.download_button(
            "Download PDF",
            data=make_pdf(text, title),
            file_name=name + ".pdf",
            mime="application/pdf",
            use_container_width=True
        )

with st.sidebar:
    st.markdown("## 📚 Study Buddy AI")
    st.caption("Your personal learning space")
    st.divider()

    navigation = {
        "Dashboard": "⌂  Dashboard",
        "AI Quiz": "✦  AI Quiz",
        "PDF Notes": "▤  PDF Notes",
        "Study Chat": "✎  Study Chat",
        "Performance": "◷  Performance",
        "Settings": "⚙  Settings"
    }

    selected = st.radio(
        "NAVIGATION",
        list(navigation.keys()),
        format_func=lambda key: navigation[key],
        index=list(navigation.keys()).index(st.session_state.page)
        if st.session_state.page in navigation else 0
    )
    st.session_state.page = selected

    st.divider()
    if api_key():
        st.success("AI key configured")
    else:
        st.warning("AI key not configured")
        if st.button("Configure AI", use_container_width=True):
            st.session_state.page = "Settings"
            st.rerun()

    st.markdown("---")
    st.caption("STUDY • PRACTISE • IMPROVE")

page = st.session_state.page

if page == "Dashboard":
    hero(
        "Make every study session count.",
        "Turn your notes into knowledge. Practise difficult topics, "
        "prepare for exams and build better study habits.",
        "WELCOME BACK"
    )

    a, b, c = st.columns(3)
    a.metric("Quizzes completed", len(st.session_state.quiz_history))
    b.metric("PDF loaded", "Yes" if st.session_state.pdf_text else "No")
    c.metric("Chat messages", len(st.session_state.chat_history))

    st.markdown("### Explore your workspace")
    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        feature("✦", "AI Quiz", "Create custom practice questions with explanations.")
        if st.button("Create a quiz", key="go_quiz", use_container_width=True):
            st.session_state.page = "AI Quiz"
            st.rerun()

    with c2:
        feature("▤", "PDF Notes", "Turn your study PDFs into revision material.")
        if st.button("Open PDF Notes", key="go_pdf", use_container_width=True):
            st.session_state.page = "PDF Notes"
            st.rerun()

    with c3:
        feature("✎", "Study Chat", "Ask questions and learn concepts step by step.")
        if st.button("Open AI Tutor", key="go_chat", use_container_width=True):
            st.session_state.page = "Study Chat"
            st.rerun()

    c4, c5, c6 = st.columns(3, gap="medium")

    with c4:
        feature("◷", "Performance", "See your quiz results and previous scores.")
        if st.button("View performance", key="go_performance", use_container_width=True):
            st.session_state.page = "Performance"
            st.rerun()

    with c5:
        feature("◎", "Study preferences", "Choose language and difficulty for learning.")
        if st.button("Open settings", key="go_settings", use_container_width=True):
            st.session_state.page = "Settings"
            st.rerun()

    with c6:
        feature("↗", "Revision workspace", "Generate summaries and important questions.")
        if st.button("Start revision", key="go_revision", use_container_width=True):
            st.session_state.page = "PDF Notes"
            st.rerun()

    st.markdown("### Recent activity")
    if st.session_state.activities:
        for item in st.session_state.activities[:5]:
            st.markdown(
                f"**{html.escape(item['text'])}**  \n"
                f"<span class='small-muted'>{html.escape(item['time'])}</span>",
                unsafe_allow_html=True
            )
    else:
        st.info("Your recent study activity will appear here.")

elif page == "AI Quiz":
    hero(
        "Practise with purpose.",
        "Create a topic-based quiz, test your understanding and review the answers.",
        "PERSONALISED PRACTICE"
    )

    with st.form("quiz_form"):
        left, right = st.columns(2)
        with left:
            subject = st.text_input("Subject", value=st.session_state.quiz_subject)
            topic = st.text_input("Topic", value=st.session_state.quiz_topic)
            difficulty = st.selectbox(
                "Difficulty",
                ["Easy", "Medium", "Hard", "Mixed"],
                index=["Easy", "Medium", "Hard", "Mixed"].index(
                    st.session_state.quiz_difficulty
                )
            )
        with right:
            count = st.select_slider(
                "Number of questions",
                options=[5, 10, 15, 20, 30, 40, 50, 75, 100],
                value=st.session_state.quiz_count
            )
            language = st.selectbox(
                "Language",
                ["Simple English", "Hinglish", "Detailed English"],
                index=["Simple English", "Hinglish", "Detailed English"].index(
                    st.session_state.quiz_language
                )
            )

        create = st.form_submit_button(
            "Generate quiz",
            type="primary",
            use_container_width=True
        )

    if create:
        if not topic.strip():
            st.error("Enter a topic to continue.")
        elif not api_key():
            st.error("Configure your Groq API key in Settings first.")
        else:
            st.session_state.quiz_subject = subject.strip() or "General"
            st.session_state.quiz_topic = topic.strip()
            st.session_state.quiz_count = count
            st.session_state.quiz_difficulty = difficulty
            st.session_state.quiz_language = language

            questions = []
            progress = st.progress(0)
            status = st.empty()

            try:
                batches = (count + 9) // 10
                for batch_number in range(batches):
                    batch_size = min(10, count - len(questions))
                    status.write(f"Generating batch {batch_number + 1} of {batches}...")
                    questions.extend(generate_batch(
                        topic.strip(),
                        subject.strip() or "General",
                        batch_size,
                        difficulty,
                        language
                    ))
                    progress.progress(min(1.0, len(questions) / count))

                status.empty()
                progress.empty()

                if not questions:
                    st.error("No valid questions were returned. Please try again.")
                else:
                    st.session_state.quiz = questions[:count]
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_result = None
                    st.session_state.last_quiz = {
                        "topic": topic.strip(),
                        "subject": subject.strip() or "General",
                        "date": datetime.now().strftime("%d %b %Y, %I:%M %p")
                    }
                    activity("Generated quiz: " + topic.strip())
                    if len(questions) < count:
                        st.warning(
                            f"Only {len(questions)} valid questions were generated. "
                            "You can use these or try again."
                        )
                    else:
                        st.success(f"{len(questions)} questions are ready.")
            except Exception as error:
                progress.empty()
                status.empty()
                st.error(f"Quiz generation failed: {error}")

    if st.session_state.quiz:
        st.divider()
        topic_label = st.session_state.last_quiz["topic"] if st.session_state.last_quiz else "Practice"
        st.subheader("Quiz: " + topic_label)
        st.caption(f"{len(st.session_state.quiz)} questions")

        if st.session_state.quiz_result is None:
            with st.form("answer_form"):
                answers = {}
                for index, question in enumerate(st.session_state.quiz):
                    st.markdown(f"**Q{index + 1}. {question['question']}**")
                    answers[index] = st.radio(
                        "Select an answer",
                        options=range(4),
                        format_func=lambda value, opts=question["options"]: opts[value],
                        key=f"answer_{index}",
                        index=None
                    )
                    st.markdown("---")

                submitted = st.form_submit_button(
                    "Submit answers",
                    type="primary",
                    use_container_width=True
                )

            if submitted:
                score = sum(
                    answers.get(i) == question["answer"]
                    for i, question in enumerate(st.session_state.quiz)
                )
                total = len(st.session_state.quiz)
                result = {
                    "score": score,
                    "total": total,
                    "percentage": round(score / total * 100) if total else 0,
                    "answers": answers,
                    "topic": topic_label,
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p")
                }
                st.session_state.quiz_answers = answers
                st.session_state.quiz_result = result
                st.session_state.quiz_history.insert(0, result)
                st.session_state.quiz_history = st.session_state.quiz_history[:100]
                activity("Completed quiz: " + topic_label)
                st.rerun()

        else:
            result = st.session_state.quiz_result
            x, y, z = st.columns(3)
            x.metric("Score", f"{result['score']}/{result['total']}")
            y.metric("Percentage", f"{result['percentage']}%")
            z.metric("Incorrect / unanswered", result["total"] - result["score"])
            st.progress(result["percentage"] / 100)

            if result["percentage"] >= 80:
                st.success("Excellent work. Keep building on what you know.")
            elif result["percentage"] >= 50:
                st.info("Good effort. Review the explanations to improve.")
            else:
                st.warning("Review the concepts and try again.")

            st.subheader("Answer review")
            for index, question in enumerate(st.session_state.quiz):
                chosen = result["answers"].get(index)
                with st.expander(f"Q{index + 1}. {question['question']}"):
                    if chosen == question["answer"]:
                        st.success("Correct answer.")
                    else:
                        st.error("Incorrect or unanswered.")
                    st.write(
                        "Your answer: " +
                        (question["options"][chosen] if chosen is not None else "Not answered")
                    )
                    st.write("Correct answer: " + question["options"][question["answer"]])
                    st.write("Explanation: " + question["explanation"])

            if st.button("Create another quiz", type="primary", use_container_width=True):
                st.session_state.quiz = []
                st.session_state.quiz_answers = {}
                st.session_state.quiz_result = None
                st.rerun()

elif page == "PDF Notes":
    hero(
        "Your notes, made clearer.",
        "Upload a PDF and generate summaries, revision notes, important questions and practice material.",
        "SMART NOTES"
    )

    uploaded = st.file_uploader("Upload your PDF", type=["pdf"])

    if uploaded is not None and uploaded.name != st.session_state.pdf_name:
        try:
            reader = PdfReader(uploaded)
            pages = [p.extract_text() or "" for p in reader.pages]
            st.session_state.pdf_text = "\n".join(pages).strip()
            st.session_state.pdf_name = uploaded.name
            st.session_state.pdf_output = ""
            if st.session_state.pdf_text:
                st.success(f"Loaded {len(reader.pages)} pages.")
            else:
                st.warning("No selectable text found. Scanned PDFs may need OCR.")
        except Exception as error:
            st.error(f"Could not read the PDF: {error}")

    if st.session_state.pdf_text:
        st.markdown(
            f'<div class="panel"><strong>{html.escape(st.session_state.pdf_name)}</strong>'
            f'<p class="small-muted">{len(st.session_state.pdf_text):,} characters extracted</p></div>',
            unsafe_allow_html=True
        )

        task = st.selectbox(
            "Choose your study material",
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
            key="notes_language"
        )

        if st.button("Generate study material", type="primary", use_container_width=True):
            if not api_key():
                st.error("Configure your Groq API key in Settings.")
            else:
                try:
                    with st.spinner("Preparing your study material..."):
                        output = ai(
                            f"""
Task: {task}
Language: {language}

Use the following PDF text as the source. Cover the important points,
use clear headings, and do not invent unsupported facts. For questions,
include their answers. For MCQs, include four options and identify the correct answer.

PDF text:
{st.session_state.pdf_text[:24000]}
""",
                            system="You are an accurate academic notes assistant.",
                            max_tokens=5000
                        )
                    st.session_state.pdf_output = output
                    activity("Generated PDF material: " + task)
                except Exception as error:
                    st.error(f"Could not generate notes: {error}")

    if st.session_state.pdf_output:
        st.subheader("Your study material")
        st.markdown(st.session_state.pdf_output)
        download_material(
            st.session_state.pdf_output,
            "study_buddy_notes",
            "Study Buddy AI Notes"
        )

elif page == "Study Chat":
    hero(
        "Let's understand it together.",
        "Ask a question, clear a doubt or request a step-by-step explanation.",
        "YOUR AI TUTOR"
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

    user_text = st.chat_input("Ask a study question...")

    if user_text:
        st.session_state.chat_history.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)

        with st.chat_message("assistant"):
            try:
                connection = client()
                if connection is None:
                    raise ValueError("Configure your Groq API key in Settings.")

                messages = [{
                    "role": "system",
                    "content": (
                        "You are Study Buddy AI, a helpful tutor. "
                        f"Respond in {language}. Explain concepts clearly, "
                        "use examples where useful, and avoid unsupported claims."
                    )
                }]
                messages.extend(st.session_state.chat_history[-12:])

                with st.spinner("Preparing your answer..."):
                    response = connection.chat.completions.create(
                        model=MODEL,
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
                activity("Asked a question in Study Chat")
            except Exception as error:
                st.error(f"Could not get a response: {error}")
                st.session_state.chat_history.pop()

elif page == "Performance":
    hero(
        "Your progress, at a glance.",
        "Review quiz results and see how your practice is developing.",
        "LEARNING INSIGHTS"
    )

    history = st.session_state.quiz_history
    if not history:
        st.info("Complete a quiz to start building your performance history.")
    else:
        scores = [item["percentage"] for item in history]
        a, b, c = st.columns(3)
        a.metric("Quizzes completed", len(history))
        b.metric("Average score", f"{round(sum(scores) / len(scores))}%")
        c.metric("Best score", f"{max(scores)}%")

        chart = [
            {"Quiz": f"{i + 1}. {item['topic'][:20]}", "Score (%)": item["percentage"]}
            for i, item in enumerate(reversed(history[-10:]))
        ]
        st.subheader("Recent scores")
        st.bar_chart(chart, x="Quiz", y="Score (%)")

        st.subheader("Quiz history")
        for item in history[:20]:
            with st.expander(f"{item['topic']} — {item['percentage']}%"):
                st.write(f"Score: {item['score']}/{item['total']}")
                st.write(f"Date: {item['date']}")

        export = "Study Buddy AI - Performance History\n\n"
        for item in history:
            export += (
                f"Topic: {item['topic']}\n"
                f"Score: {item['score']}/{item['total']}\n"
                f"Percentage: {item['percentage']}%\n"
                f"Date: {item['date']}\n\n"
            )

        st.download_button(
            "Export performance",
            data=export,
            file_name="study_buddy_performance.txt",
            mime="text/plain",
            use_container_width=True
        )

elif page == "Settings":
    hero(
        "Make it work for you.",
        "Configure the AI connection and manage your learning workspace.",
        "SETTINGS"
    )

    st.subheader("AI connection")
    st.write("Study Buddy AI uses Groq to power its AI features.")

    st.markdown("**Recommended: Streamlit Secrets**")
    st.write("In Streamlit Cloud, open Settings → Secrets and add:")
    st.code('GROQ_API_KEY = "your_groq_api_key_here"', language="toml")
    st.caption("Never put your real API key into a public GitHub repository.")

    with st.expander("Use a temporary key for this session"):
        key_input = st.text_input("Groq API key", type="password")
        if st.button("Save session key", type="primary"):
            st.session_state.manual_api_key = key_input.strip()
            st.success("Key saved for this running session.")
            st.rerun()

    if api_key():
        st.success("An API key is configured.")
    else:
        st.warning("No API key has been configured.")

    if st.button("Test AI connection", use_container_width=True):
        if not api_key():
            st.error("Add your API key first.")
        else:
            try:
                with st.spinner("Testing the connection..."):
                    answer = ai(
                        "Reply with exactly: Connection successful.",
                        max_tokens=50
                    )
                st.success(answer)
            except Exception as error:
                st.error(f"Connection test failed: {error}")

    st.divider()
    st.subheader("About this workspace")
    st.write("Application: Study Buddy AI")
    st.write("Theme: Sage Green and Off-White")
    st.write("AI provider: Groq")
    st.write("Quiz generator: Batch-based generation, up to 100 requested questions")
    st.caption(
        "Session history may reset when the app restarts. AI-generated answers "
        "can contain mistakes, so verify important academic information."
    )

st.divider()
st.markdown(
    '<p class="small-muted" style="text-align:center;">'
    'Study Buddy AI · Learn clearly. Practise consistently. Grow confidently.'
    '</p>',
    unsafe_allow_html=True
)
