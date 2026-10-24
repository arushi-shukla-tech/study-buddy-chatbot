import streamlit as st
import json
import re
from io import BytesIO
from google import genai
from pypdf import PdfReader

# ---------- PAGE SETTINGS ----------
st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- DESIGN ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: Inter, sans-serif;
}
.stApp {
    background: linear-gradient(135deg, #0b1020, #15162c, #211638);
    color: #f4f5ff;
}
[data-testid="stSidebar"] {
    background: #0b1020;
    border-right: 1px solid #303456;
}
h1, h2, h3 {
    color: #e5ddff !important;
}
div[data-testid="stMetric"] {
    background: #1b2140;
    border: 1px solid #34395c;
    padding: 16px;
    border-radius: 15px;
}
div[data-testid="stMetricValue"] {
    color: #b8a7ff;
}
.stButton > button, .stFormSubmitButton > button {
    background: linear-gradient(90deg, #8067f7, #b06cf7);
    color: white;
    border: 0;
    border-radius: 10px;
    font-weight: 700;
    min-height: 42px;
}
.hero {
    padding: 26px;
    border-radius: 20px;
    background: linear-gradient(120deg, #292451, #202c4e, #3a2350);
    border: 1px solid #49436f;
    margin-bottom: 22px;
}
.panel {
    background: #151a30;
    border: 1px solid #2b3353;
    padding: 20px;
    border-radius: 16px;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION DATA ----------
defaults = {
    "notes": "",
    "filename": "",
    "chat": [],
    "quiz": [],
    "answers": {},
    "submitted": False,
    "score": None,
    "attempts": 0,
    "best": 0,
    "asked": 0,
    "activity": [],
    "batch": 0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def log_activity(message):
    st.session_state.activity.append(message)
    st.session_state.activity = st.session_state.activity[-25:]


def reset_quiz():
    st.session_state.answers = {}
    st.session_state.submitted = False
    st.session_state.score = None


# ---------- GEMINI AI ----------
def ask_ai(prompt):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        api_key = ""

    if not api_key:
        raise ValueError(
            "API key missing. Add GEMINI_API_KEY in Streamlit Secrets."
        )

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    if not response.text:
        raise ValueError("AI returned no answer. Please try again.")

    return response.text


# ---------- PDF READER ----------
def read_pdf(file):
    reader = PdfReader(BytesIO(file.getvalue()))
    pages = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return "\n".join(pages).strip()


# ---------- QUIZ GENERATOR ----------
def make_quiz(amount, difficulty):
    old_questions = [
        q["question"] for q in st.session_state.quiz
    ]

    previous = "\n".join(old_questions[-50:])

    prompt = f"""
You are an educational quiz generator.

Create {amount} multiple-choice questions.
Difficulty: {difficulty}

Return only valid JSON using this structure:
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

Rules:
- Use only the study notes as the main source.
- Each question must have four options.
- The correct answer must be an integer from 0 to 3.
- There must be only one correct answer.
- Avoid repeating the previous questions.
- Do not include Markdown or text outside JSON.

PREVIOUS QUESTIONS:
{previous[:6000]}

STUDY NOTES:
{st.session_state.notes[:35000]}
"""

    raw = ask_ai(prompt).strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    data = json.loads(raw)
    questions = []

    for q in data.get("questions", []):
        options = q.get("options", [])
        answer = q.get("answer")

        if (
            isinstance(q.get("question"), str)
            and isinstance(options, list)
            and len(options) == 4
            and all(isinstance(x, str) for x in options)
            and isinstance(answer, int)
            and not isinstance(answer, bool)
            and 0 <= answer <= 3
        ):
            questions.append({
                "question": q["question"],
                "options": options,
                "answer": answer,
                "explanation": q.get("explanation", "")
            })

    if not questions:
        raise ValueError(
            "The AI did not return valid questions. Please try again."
        )

    return questions


# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("🎓 Study Buddy AI")
    st.caption("Your personal learning assistant")
    st.divider()

    page = st.radio(
        "YOUR WORKSPACE",
        [
            "Dashboard",
            "My Notes",
            "AI Chat",
            "Quiz Maker"
        ]
    )

    st.divider()

    if st.session_state.notes:
        st.success("Notes loaded")
        st.caption(st.session_state.filename)
        st.caption(
            f"{len(st.session_state.notes.split()):,} words"
        )
    else:
        st.info("Upload notes to get started.")

    st.caption("Powered by Gemini AI")


# ---------- HEADER ----------
st.markdown("""
<div class="hero">
    <p style="color:#c9c1ff;letter-spacing:2px;font-weight:700">
        YOUR PERSONAL LEARNING ASSISTANT
    </p>
    <h1>Study smarter. Not harder. ✨</h1>
    <p>Understand your notes, practise with AI, and track your progress.</p>
</div>
""", unsafe_allow_html=True)


# ==================================================
# DASHBOARD
# ==================================================
if page == "Dashboard":
    st.subheader("📊 Your Learning Dashboard")

    a, b, c, d = st.columns(4)

    a.metric("📚 Notes Words", f"{len(st.session_state.notes.split()):,}")
    b.metric("💬 Questions Asked", st.session_state.asked)
    c.metric("📝 Quiz Attempts", st.session_state.attempts)
    d.metric("🏆 Best Score", f"{st.session_state.best}%")

    st.markdown("### 🚀 Your Study Tools")

    left, right = st.columns(2)

    with left:
        st.markdown("""
        <div class="panel">
            <h3>📚 My Notes</h3>
            <p>Upload PDF files or paste your class notes.</p>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="panel">
            <h3>🧠 AI Quiz Maker</h3>
            <p>Create practice questions and check your answers.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📈 Recent Activity")

    if st.session_state.activity:
        for item in reversed(st.session_state.activity):
            st.write("• " + item)
    else:
        st.info("Your study activities will appear here.")

    st.caption(
        "Progress is stored in the active session and may reset "
        "when the session ends."
    )


# ==================================================
# MY NOTES
# ==================================================
elif page == "My Notes":
    st.subheader("📚 My Notes Library")
    st.write("Upload a text-based PDF or paste your notes.")

    uploaded = st.file_uploader(
        "Choose your PDF",
        type=["pdf"]
    )

    if uploaded and st.button("📥 Read PDF", use_container_width=True):
        try:
            with st.spinner("Reading your PDF..."):
                extracted = read_pdf(uploaded)

            if not extracted:
                st.error(
                    "No selectable text found. Try another PDF "
                    "or paste your notes manually."
                )
            else:
                st.session_state.notes = extracted[:100000]
                st.session_state.filename = uploaded.name
                st.session_state.chat = []
                st.session_state.quiz = []
                st.session_state.batch = 0
                reset_quiz()
                log_activity("Uploaded PDF: " + uploaded.name)
                st.success("PDF uploaded successfully!")
                st.rerun()

        except Exception as e:
            st.error(f"PDF error: {e}")

    st.divider()

    pasted = st.text_area(
        "Or paste your study notes here",
        height=220,
        placeholder="Paste your chapter or class notes..."
    )

    if st.button("💾 Save Notes", use_container_width=True):
        if pasted.strip():
            st.session_state.notes = pasted.strip()[:100000]
            st.session_state.filename = "Pasted Study Notes"
            st.session_state.chat = []
            st.session_state.quiz = []
            st.session_state.batch = 0
            reset_quiz()
            log_activity("Saved pasted notes")
            st.success("Notes saved successfully!")
            st.rerun()
        else:
            st.warning("Please paste some notes first.")

    if st.session_state.notes:
        st.divider()

        x, y = st.columns(2)
        x.metric("Words", f"{len(st.session_state.notes.split()):,}")
        y.metric("Characters", f"{len(st.session_state.notes):,}")

        with st.expander("Preview Saved Notes"):
            st.text(st.session_state.notes[:5000])

        if st.button("🗑️ Clear Notes"):
            st.session_state.notes = ""
            st.session_state.filename = ""
            st.session_state.chat = []
            st.session_state.quiz = []
            st.session_state.batch = 0
            reset_quiz()
            st.rerun()


# ==================================================
# AI CHAT
# ==================================================
elif page == "AI Chat":
    st.subheader("💬 Chat with Your Notes")
    st.write("Ask questions, request summaries, or learn a difficult topic.")

    if not st.session_state.notes:
        st.warning("First upload a PDF or save notes in My Notes.")
    else:
        for msg in st.session_state.chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        question = st.chat_input("Ask a question about your notes...")

        if question:
            st.session_state.chat.append({
                "role": "user",
                "content": question
            })
            st.session_state.asked += 1

            with st.spinner("Study Buddy is thinking..."):
                try:
                    answer = ask_ai(f"""
You are Study Buddy AI, a friendly study tutor.

Explain concepts in simple, clear language.
Give examples when useful.
Base your answer on the notes below.
If the notes do not contain the answer, say so clearly.

STUDY NOTES:
{st.session_state.notes[:35000]}

STUDENT QUESTION:
{question}
""")

                    st.session_state.chat.append({
                        "role": "assistant",
                        "content": answer
                    })
                    log_activity("Asked a question in AI Chat")
                    st.rerun()

                except Exception as e:
                    st.error(f"AI error: {e}")

        if st.button("🧹 Clear Chat"):
            st.session_state.chat = []
            st.rerun()


# ==================================================
# QUIZ MAKER
# ==================================================
elif page == "Quiz Maker":
    st.subheader("🧠 AI Quiz Maker")
    st.write("Generate practice questions from your own study material.")

    if not st.session_state.notes:
        st.warning("First upload a PDF or save notes in My Notes.")
    else:
        st.success("Study notes are ready!")

        amount = st.selectbox(
            "Questions in each batch",
            [5, 10, 15, 20, 30, 50, 75, 100],
            index=3
        )

        difficulty = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard", "Mixed"]
        )

        st.caption(
            "Generate more batches to continue practising. "
            "API usage and response limits still apply."
        )

        if st.button("✨ Generate Quiz", use_container_width=True):
            try:
                with st.spinner("Generating your quiz..."):
                    questions = make_quiz(amount, difficulty)

                st.session_state.quiz = questions
                st.session_state.batch = 1
                reset_quiz()
                log_activity(
                    f"Generated a quiz with {len(questions)} questions"
                )
                st.rerun()

            except Exception as e:
                st.error(f"Quiz error: {e}")

        if st.session_state.quiz:
            st.divider()

            st.markdown(
                f"### 📝 Your Quiz — {len(st.session_state.quiz)} Questions"
            )

            st.caption(f"Quiz batch: {st.session_state.batch}")

            with st.form(f"quiz_form_{st.session_state.batch}"):
                for i, q in enumerate(st.session_state.quiz):
                    st.markdown(f"**Q{i + 1}. {q['question']}**")

                    choice = st.radio(
                        "Select an answer",
                        options=[0, 1, 2, 3],
                        format_func=lambda n, opts=q["options"]: opts[n],
                        index=st.session_state.answers.get(i),
                        key=f"choice_{st.session_state.batch}_{i}"
                    )

                    st.session_state.answers[i] = choice
                    st.divider()

                submitted = st.form_submit_button(
                    "✅ Submit Quiz",
                    use_container_width=True
                )

            if submitted:
                total = len(st.session_state.quiz)

                correct = sum(
                    1 for i, q in enumerate(st.session_state.quiz)
                    if st.session_state.answers.get(i) == q["answer"]
                )

                score = round(correct * 100 / total) if total else 0

                st.session_state.submitted = True
                st.session_state.score = score
                st.session_state.attempts += 1
                st.session_state.best = max(
                    st.session_state.best, score
                )

                log_activity(f"Completed quiz with score {score}%")
                st.rerun()

            if st.session_state.submitted:
                total = len(st.session_state.quiz)
                correct = sum(
                    1 for i, q in enumerate(st.session_state.quiz)
                    if st.session_state.answers.get(i) == q["answer"]
                )

                st.markdown("### 🏆 Your Result")

                x, y, z = st.columns(3)
                x.metric("Score", f"{st.session_state.score}%")
                y.metric("Correct Answers", correct)
                z.metric("Total Questions", total)

                st.progress(st.session_state.score / 100)

                if st.session_state.score >= 80:
                    st.success("Excellent work! Keep it up.")
                elif st.session_state.score >= 50:
                    st.info("Good effort. Review the answers below.")
                else:
                    st.warning("Keep practising. You can improve!")

                st.markdown("### 📖 Answer Review")

                for i, q in enumerate(st.session_state.quiz):
                    chosen = st.session_state.answers.get(i)
                    right = q["answer"]

                    if chosen == right:
                        st.success(f"Q{i + 1}: Correct")
                    else:
                        st.error(
                            f"Q{i + 1}: Correct answer — "
                            f"{q['options'][right]}"
                        )

                    if q.get("explanation"):
                        st.caption(q["explanation"])

                if st.button("🔄 Try This Quiz Again"):
                    st.session_state.batch += 1
                    reset_quiz()
                    st.rerun()

            st.divider()

            if st.button(
                "➕ Generate More Questions",
                use_container_width=True
            ):
                try:
                    with st.spinner("Creating the next batch..."):
                        more = make_quiz(amount, difficulty)

                    existing = {
                        q["question"].strip().lower()
                        for q in st.session_state.quiz
                    }

                    new_questions = [
                        q for q in more
                        if q["question"].strip().lower() not in existing
                    ]

                    if new_questions:
                        st.session_state.quiz.extend(new_questions)
                        st.session_state.batch += 1
                        reset_quiz()
                        log_activity(
                            f"Added {len(new_questions)} more questions"
                        )
                        st.success(
                            f"Added {len(new_questions)} new questions!"
                        )
                        st.rerun()
                    else:
                        st.warning(
                            "The AI repeated the questions. Try again."
                        )

                except Exception as e:
                    st.error(f"Could not generate more questions: {e}")


# ---------- FOOTER ----------
st.divider()
st.caption("🎓 Study Buddy AI | Learn • Practise • Improve")
