import streamlit as st
import json
import re
from io import BytesIO
from datetime import datetime
from groq import Groq
from pypdf import PdfReader
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from xml.sax.saxutils import escape


st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------- DESIGN ----------

st.markdown("""
<style>
.stApp {
    background: #0b1020;
    color: #edf2ff;
}
[data-testid="stSidebar"] {
    background: #111a30;
    border-right: 1px solid #25314e;
}
.block-container {
    padding-top: 1.8rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}
h1, h2, h3 {
    color: #f3f6ff !important;
}
p, label, li {
    color: #c7d2e8;
}
[data-testid="stMetric"] {
    background: #151f37;
    border: 1px solid #2a3858;
    padding: 18px;
    border-radius: 15px;
}
div.stButton > button {
    background: #5268f5;
    color: white;
    border: none;
    border-radius: 10px;
    min-height: 42px;
    font-weight: 600;
}
div.stButton > button:hover {
    background: #7182ff;
    color: white;
}
div[data-testid="stForm"] {
    background: #111a30;
    border: 1px solid #25314e;
    padding: 18px;
    border-radius: 14px;
}
div[data-testid="stAlert"] {
    border-radius: 12px;
}
.stTextInput input, .stTextArea textarea {
    background: #111a30;
    color: #f3f6ff;
}
</style>
""", unsafe_allow_html=True)


# ---------- SESSION DATA ----------

DEFAULTS = {
    "nav_page": "Dashboard",
    "quiz_history": [],
    "notes_created": 0,
    "chat_messages": [],
    "last_notes": "",
    "last_pdf_name": "",
    "quiz_data": [],
    "quiz_topic": "",
    "quiz_submitted": False,
    "quiz_result": None,
    "quiz_language": "Simple English",
    "quiz_count": 10,
    "notes_language": "Simple English",
    "notes_type": "Exam Notes",
    "chat_language": "Simple English",
    "session_api_key": "",
    "last_activity": "Not yet",
    "total_questions": 0
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def set_page(page):
    st.session_state["nav_page"] = page


def get_api_key():
    key = st.session_state.get("session_api_key", "").strip()

    if key:
        return key

    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return ""


def ask_ai(prompt, temperature=0.3):
    api_key = get_api_key()

    if not api_key:
        raise ValueError(
            "Groq API key nahi mili. Settings page mein API key add karo."
        )

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Study Buddy AI, a helpful college study "
                    "assistant. Give accurate, well-organized answers "
                    "in the requested language. Use clear headings "
                    "and simple explanations."
                )
            },
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_completion_tokens=6000
    )

    return response.choices[0].message.content.strip()


def extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start:end + 1])
        raise ValueError("AI ka response valid JSON mein nahi aaya.")


def generate_quiz_batch(topic, count, language, previous_questions):
    previous_text = "\n".join(
        f"- {question}" for question in previous_questions[-100:]
    )
    if not previous_text:
        previous_text = "None"

    prompt = f"""
Create exactly {count} multiple-choice questions for a student.

Topic or source:
{topic}

Language: {language}

Avoid repeating these earlier questions:
{previous_text}

Return ONLY valid JSON in this exact structure:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": [
        "Option A",
        "Option B",
        "Option C",
        "Option D"
      ],
      "answer": 0,
      "explanation": "Short explanation"
    }}
  ]
}}

Rules:
- Create exactly {count} questions.
- Each question must have exactly four options.
- The answer must be an integer: 0, 1, 2, or 3.
- Make the questions useful for college-level revision.
- Do not include markdown fences or text outside the JSON.
- Keep questions distinct and explanations understandable.
"""

    raw = ask_ai(prompt, temperature=0.4)
    data = extract_json(raw)
    questions = data.get("questions", [])

    cleaned = []

    for item in questions:
        if not isinstance(item, dict):
            continue

        question = str(item.get("question", "")).strip()
        options = item.get("options", [])
        answer = item.get("answer", 0)
        explanation = str(item.get("explanation", "")).strip()

        if not question or not isinstance(options, list):
            continue

        if len(options) != 4:
            continue

        try:
            answer = int(answer)
        except (ValueError, TypeError):
            continue

        if answer not in [0, 1, 2, 3]:
            continue

        cleaned.append({
            "question": question,
            "options": [str(option) for option in options],
            "answer": answer,
            "explanation": explanation
        })

    if not cleaned:
        raise ValueError("Valid questions generate nahi hue. Dobara try karo.")

    return cleaned


def create_notes_pdf(title, content):
    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=(8.27 * inch, 11.69 * inch),
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.7 * inch
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="MainTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=26,
        textColor=colors.HexColor("#253c80"),
        spaceAfter=18
    ))

    styles.add(ParagraphStyle(
        name="NoteBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        spaceAfter=8
    ))

    story = [
        Paragraph(escape(title), styles["MainTitle"]),
        Paragraph(
            "Generated by Study Buddy AI",
            styles["Italic"]
        ),
        Spacer(1, 12)
    ]

    for line in content.splitlines():
        safe_line = escape(line.strip())

        if not safe_line:
            story.append(Spacer(1, 7))
        elif line.strip().startswith("#"):
            heading = escape(line.strip().lstrip("# ").strip())
            story.append(Paragraph(heading, styles["Heading2"]))
        else:
            story.append(Paragraph(safe_line, styles["NoteBody"]))

    document.build(story)
    output.seek(0)
    return output.getvalue()


def record_activity():
    st.session_state["last_activity"] = datetime.now().strftime(
        "%d %b %Y, %I:%M %p"
    )


# ---------- SIDEBAR ----------

with st.sidebar:
    st.markdown("## 📘 Study Buddy AI")
    st.caption("Your personal study workspace")
    st.divider()

    pages = [
        "Dashboard",
        "AI Quiz",
        "PDF Notes",
        "Study Chat",
        "Performance",
        "Settings"
    ]

    current_page = st.session_state["nav_page"]
    if current_page not in pages:
        current_page = "Dashboard"

    st.radio(
        "NAVIGATION",
        pages,
        index=pages.index(current_page),
        key="nav_page"
    )

    st.divider()
    st.caption("Study smarter. Learn better.")


page = st.session_state["nav_page"]


# ---------- DASHBOARD ----------

if page == "Dashboard":
    st.markdown("# Welcome to Study Buddy AI")
    st.write(
        "Your personal workspace for notes, quizzes and focused learning."
    )

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Quizzes completed",
            len(st.session_state["quiz_history"])
        )

    with col2:
        st.metric(
            "Notes generated",
            st.session_state["notes_created"]
        )

    with col3:
        st.metric(
            "Questions attempted",
            st.session_state["total_questions"]
        )

    st.write("")
    st.markdown("### Your study workspace")

    a, b = st.columns(2)

    with a:
        with st.container(border=True):
            st.markdown("#### 📝 AI Quiz")
            st.write(
                "Create topic-based MCQs, attempt them and review "
                "your answers with explanations."
            )
            if st.button("Open AI Quiz", use_container_width=True):
                set_page("AI Quiz")
                st.rerun()

        with st.container(border=True):
            st.markdown("#### 💬 Study Chat")
            st.write(
                "Ask questions and understand difficult topics "
                "in your preferred language."
            )
            if st.button("Open Study Chat", use_container_width=True):
                set_page("Study Chat")
                st.rerun()

    with b:
        with st.container(border=True):
            st.markdown("#### 📄 PDF Notes")
            st.write(
                "Upload class notes and create summaries, revision "
                "material and exam-focused answers."
            )
            if st.button("Open PDF Notes", use_container_width=True):
                set_page("PDF Notes")
                st.rerun()

        with st.container(border=True):
            st.markdown("#### 📊 Performance")
            st.write(
                "Review your previous quiz attempts and track "
                "your scores."
            )
            if st.button("View Performance", use_container_width=True):
                set_page("Performance")
                st.rerun()

    st.write("")
    st.caption(
        "Last activity: " + st.session_state["last_activity"]
    )


# ---------- AI QUIZ ----------

elif page == "AI Quiz":
    st.markdown("# AI Quiz")
    st.write(
        "Generate questions from a topic or your PDF notes. "
        "You can request between 5 and 100 questions."
    )

    with st.form("quiz_setup"):
        topic = st.text_area(
            "Enter your topic or paste study material",
            placeholder="Example: BJT working, recursion in C, or matrices",
            height=120
        )

        uploaded_quiz_pdf = st.file_uploader(
            "Or upload a PDF for quiz generation",
            type=["pdf"],
            key="quiz_pdf"
        )

        question_count = st.number_input(
            "Number of questions",
            min_value=5,
            max_value=100,
            value=10,
            step=5
        )

        quiz_language = st.selectbox(
            "Question language",
            ["Simple English", "Hinglish", "Detailed English"]
        )

        generate = st.form_submit_button(
            "Generate Quiz",
            use_container_width=True
        )

    if generate:
        source = topic.strip()

        if uploaded_quiz_pdf is not None:
            try:
                reader = PdfReader(uploaded_quiz_pdf)
                pdf_text = "\n".join(
                    page.extract_text() or "" for page in reader.pages
                )
                if pdf_text.strip():
                    source = (
                        "Create questions from this PDF content:\n"
                        + pdf_text[:50000]
                    )
                elif not source:
                    st.error(
                        "PDF se readable text nahi mila. "
                        "Scanned PDF ho sakti hai."
                    )
            except Exception as error:
                st.error(f"PDF read nahi ho paayi: {error}")

        if not source:
            st.warning("Pehle topic likho ya readable PDF upload karo.")
        else:
            try:
                st.session_state["quiz_data"] = []
                st.session_state["quiz_submitted"] = False
                st.session_state["quiz_result"] = None
                st.session_state["quiz_topic"] = topic.strip() or "Uploaded PDF"
                st.session_state["quiz_language"] = quiz_language
                st.session_state["quiz_count"] = int(question_count)

                progress = st.progress(0)
                status = st.empty()
                all_questions = []
                target = int(question_count)

                while len(all_questions) < target:
                    batch_size = min(10, target - len(all_questions))
                    status.write(
                        f"Generating questions: {len(all_questions)} "
                        f"of {target}..."
                    )

                    previous = [
                        item["question"] for item in all_questions
                    ]

                    batch = generate_quiz_batch(
                        source,
                        batch_size,
                        quiz_language,
                        previous
                    )

                    all_questions.extend(batch)
                    progress.progress(min(len(all_questions) / target, 1.0))

                st.session_state["quiz_data"] = all_questions[:target]
                status.success("Quiz ready. All questions are below.")
                record_activity()
                st.rerun()

            except Exception as error:
                st.error(f"Quiz generate nahi hua: {error}")

    questions = st.session_state["quiz_data"]

    if questions:
        st.divider()
        st.markdown("### Your quiz")
        st.caption(
            f"Topic: {st.session_state['quiz_topic']} · "
            f"{len(questions)} questions"
        )

        if not st.session_state["quiz_submitted"]:
            with st.form("quiz_attempt"):
                selected_answers = []

                for i, item in enumerate(questions):
                    st.markdown(
                        f"**Q{i + 1}. {item['question']}**"
                    )

                    answer = st.radio(
                        f"Choose an answer for question {i + 1}",
                        item["options"],
                        index=None,
                        key=f"quiz_answer_{i}",
                        label_visibility="collapsed"
                    )
                    selected_answers.append(answer)
                    st.write("")

                submit_quiz = st.form_submit_button(
                    "Submit Quiz",
                    use_container_width=True
                )

            if submit_quiz:
                score = 0
                reviewed = []

                for i, item in enumerate(questions):
                    selected = selected_answers[i]
                    correct = item["options"][item["answer"]]

                    is_correct = selected == correct
                    if is_correct:
                        score += 1

                    reviewed.append({
                        "question": item["question"],
                        "options": item["options"],
                        "selected": selected,
                        "correct": correct,
                        "is_correct": is_correct,
                        "explanation": item["explanation"]
                    })

                total = len(questions)
                percentage = round(score / total * 100, 1)

                result = {
                    "topic": st.session_state["quiz_topic"],
                    "score": score,
                    "total": total,
                    "percentage": percentage,
                    "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                    "review": reviewed
                }

                st.session_state["quiz_result"] = result
                st.session_state["quiz_submitted"] = True
                st.session_state["quiz_history"].append({
                    "topic": result["topic"],
                    "score": score,
                    "total": total,
                    "percentage": percentage,
                    "date": result["date"]
                })
                st.session_state["total_questions"] += total
                record_activity()
                st.rerun()

        if st.session_state["quiz_submitted"]:
            result = st.session_state["quiz_result"]

            if result:
                st.markdown("### Quiz result")

                c1, c2, c3 = st.columns(3)
                c1.metric("Score", f"{result['score']}/{result['total']}")
                c2.metric("Percentage", f"{result['percentage']}%")
                c3.metric(
                    "Incorrect / unanswered",
                    result["total"] - result["score"]
                )

                if result["percentage"] >= 80:
                    st.success("Great work! You have a strong score.")
                elif result["percentage"] >= 50:
                    st.info("Good effort. Review the explanations below.")
                else:
                    st.warning(
                        "Keep practising. Review each explanation "
                        "and try another quiz."
                    )

                st.markdown("### Answer review")

                for i, item in enumerate(result["review"]):
                    with st.container(border=True):
                        st.markdown(
                            f"**Q{i + 1}. {item['question']}**"
                        )

                        st.write(
                            "Your answer: "
                            + (item["selected"] or "Not answered")
                        )
                        st.write("Correct answer: " + item["correct"])

                        if item["is_correct"]:
                            st.success("Correct")
                        else:
                            st.error("Incorrect")

                        st.write(
                            "Explanation: "
                            + (item["explanation"] or "No explanation provided.")
                        )

                if st.button("Create another quiz", use_container_width=True):
                    st.session_state["quiz_data"] = []
                    st.session_state["quiz_submitted"] = False
                    st.session_state["quiz_result"] = None
                    st.rerun()


# ---------- PDF NOTES ----------

elif page == "PDF Notes":
    st.markdown("# PDF Notes")
    st.write(
        "Upload your notes and turn them into study material "
        "for revision and exam preparation."
    )

    uploaded_pdf = st.file_uploader(
        "Upload a PDF file",
        type=["pdf"],
        key="notes_pdf"
    )

    note_type = st.selectbox(
        "What would you like to create?",
        [
            "Exam Notes",
            "Short Summary",
            "Important Questions and Answers",
            "Revision Points",
            "Practice MCQs",
            "Explain in Simple Language"
        ]
    )

    notes_language = st.selectbox(
        "Output language",
        ["Simple English", "Hinglish", "Detailed English"]
    )

    extra_instructions = st.text_area(
        "Extra instructions (optional)",
        placeholder="Example: Make answers suitable for 7 marks."
    )

    if st.button("Create Study Material", use_container_width=True):
        if uploaded_pdf is None:
            st.warning("Pehle PDF upload karo.")
        else:
            try:
                reader = PdfReader(uploaded_pdf)
                pdf_text = "\n".join(
                    page.extract_text() or "" for page in reader.pages
                )

                if not pdf_text.strip():
                    st.error(
                        "PDF se text nahi mila. Ho sakta hai PDF scanned "
                        "images wali ho."
                    )
                else:
                    prompt = f"""
Create study material using ONLY the supplied PDF content.

Type: {note_type}
Language: {notes_language}
Extra instructions: {extra_instructions or "None"}

Requirements:
- Cover the important material from the PDF.
- Use clear headings and numbered points where useful.
- Keep the language easy to understand.
- Do not invent facts that are not supported by the PDF.
- For exam answers, include a definition, explanation, key points,
  examples where relevant, and a conclusion when appropriate.
- Make the result useful for a college student.

PDF content:
{pdf_text[:50000]}
"""
                    with st.spinner("Preparing your study material..."):
                        generated_notes = ask_ai(prompt, temperature=0.3)

                    st.session_state["last_notes"] = generated_notes
                    st.session_state["last_pdf_name"] = uploaded_pdf.name
                    st.session_state["notes_created"] += 1
                    st.session_state["notes_type"] = note_type
                    st.session_state["notes_language"] = notes_language
                    record_activity()
                    st.rerun()

            except Exception as error:
                st.error(f"Notes create nahi hue: {error}")

    if st.session_state["last_notes"]:
        st.divider()
        st.markdown("### Your study material")
        st.markdown(st.session_state["last_notes"])

        st.download_button(
            "Download notes as TXT",
            data=st.session_state["last_notes"],
            file_name="study_buddy_notes.txt",
            mime="text/plain",
            use_container_width=True
        )

        try:
            pdf_bytes = create_notes_pdf(
                "Study Buddy AI - " + st.session_state["notes_type"],
                st.session_state["last_notes"]
            )

            st.download_button(
                "Download notes as PDF",
                data=pdf_bytes,
                file_name="study_buddy_notes.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as error:
            st.warning(f"PDF export nahi ho paaya: {error}")


# ---------- STUDY CHAT ----------

elif page == "Study Chat":
    st.markdown("# Study Chat")
    st.write(
        "Ask academic questions, get concepts explained and "
        "prepare for college exams."
    )

    st.session_state["chat_language"] = st.selectbox(
        "Answer style",
        ["Simple English", "Hinglish", "Detailed English"],
        index=[
            "Simple English",
            "Hinglish",
            "Detailed English"
        ].index(st.session_state["chat_language"])
    )

    for message in st.session_state["chat_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input(
        "Ask a study question..."
    )

    if user_prompt:
        st.session_state["chat_messages"].append({
            "role": "user",
            "content": user_prompt
        })

        with st.chat_message("user"):
            st.markdown(user_prompt)

        language = st.session_state["chat_language"]

        prompt = f"""
Answer this student's question in {language}.

Question:
{user_prompt}

Make the answer accurate and easy to understand.
For programming questions, give complete beginner-friendly code
when needed, with proper indentation and explanations.
For exam questions, use clear headings and exam-friendly points.
"""

        try:
            with st.chat_message("assistant"):
                with st.spinner("Preparing your answer..."):
                    answer = ask_ai(prompt, temperature=0.4)
                st.markdown(answer)

            st.session_state["chat_messages"].append({
                "role": "assistant",
                "content": answer
            })
            record_activity()

        except Exception as error:
            st.error(f"Answer generate nahi hua: {error}")

    if st.session_state["chat_messages"]:
        if st.button("Clear chat history"):
            st.session_state["chat_messages"] = []
            st.rerun()


# ---------- PERFORMANCE ----------

elif page == "Performance":
    st.markdown("# Performance")
    st.write("Your quiz history and learning progress.")

    history = st.session_state["quiz_history"]

    if not history:
        st.info(
            "Abhi koi completed quiz nahi hai. AI Quiz page par "
            "jaakar apna pehla quiz attempt karo."
        )
    else:
        total_quizzes = len(history)
        total_correct = sum(item["score"] for item in history)
        total_attempted = sum(item["total"] for item in history)

        average = (
            round(total_correct / total_attempted * 100, 1)
            if total_attempted else 0
        )

        c1, c2, c3 = st.columns(3)
        c1.metric("Quizzes completed", total_quizzes)
        c2.metric("Questions attempted", total_attempted)
        c3.metric("Overall accuracy", f"{average}%")

        st.markdown("### Previous quizzes")

        for i, item in enumerate(reversed(history), start=1):
            with st.container(border=True):
                st.markdown(f"**{item['topic']}**")
                st.write("Date: " + item["date"])
                st.write(
                    f"Score: {item['score']}/{item['total']} "
                    f"({item['percentage']}%)"
                )

        history_text = "Study Buddy AI - Quiz History\n\n"

        for item in history:
            history_text += (
                f"Topic: {item['topic']}\n"
                f"Score: {item['score']}/{item['total']}\n"
                f"Percentage: {item['percentage']}%\n"
                f"Date: {item['date']}\n\n"
            )

        st.download_button(
            "Download quiz history",
            data=history_text,
            file_name="study_buddy_performance.txt",
            mime="text/plain"
        )


# ---------- SETTINGS ----------

elif page == "Settings":
    st.markdown("# Settings")
    st.write("Manage your API key and current study session.")

    st.markdown("### Groq API")

    st.write(
        "API key ko neeche enter kar sakti ho. Ye session mein rahegi. "
        "Permanent setup ke liye Streamlit Secrets use karo."
    )

    api_key_input = st.text_input(
        "Groq API key",
        type="password",
        placeholder="Enter your Groq API key",
        value=st.session_state["session_api_key"]
    )

    if st.button("Save API key for this session"):
        st.session_state["session_api_key"] = api_key_input.strip()
        st.success("API key current session ke liye set kar di gayi hai.")

    st.caption(
        "API key ko public GitHub repository, screenshots ya shared "
        "messages mein kabhi paste mat karna."
    )

    st.divider()
    st.markdown("### Session information")
    st.write(
        f"Quizzes completed: {len(st.session_state['quiz_history'])}"
    )
    st.write(
        f"Notes generated: {st.session_state['notes_created']}"
    )
    st.write(
        f"Chat messages: {len(st.session_state['chat_messages'])}"
    )

    st.divider()
    st.markdown("### Reset session")

    st.warning(
        "Reset karne se current session ki quiz history, chat aur "
        "generated notes clear ho jayenge."
    )

    if st.button("Reset study session"):
        for key, value in DEFAULTS.items():
            st.session_state[key] = value

        st.rerun()


# ---------- FOOTER ----------

st.divider()
st.caption(
    "Study Buddy AI · Personal study workspace · "
    "Quiz scores and session history are stored in the current session."
)