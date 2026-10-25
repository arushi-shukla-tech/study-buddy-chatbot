import streamlit as st
import json
import re
from io import BytesIO
from groq import Groq
from pypdf import PdfReader

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)

defaults = {
    "page": "Dashboard",
    "quiz_data": None,
    "quiz_answers": {},
    "quiz_submitted": False,
    "quiz_score_saved": False,
    "chat_history": [],
    "pdf_text": "",
    "pdf_name": "",
    "notes": "",
    "topics_done": 0,
    "quiz_count": 0,
    "correct_count": 0,
    "last_summary": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def set_page(page_name):
    st.session_state["page"] = page_name


def get_client():
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        api_key = ""

    if not api_key:
        return None

    try:
        return Groq(api_key=api_key)
    except Exception:
        return None


def ask_ai(prompt, system_message="You are a helpful study assistant."):
    client = get_client()

    if client is None:
        return (
            "AI connection is not configured. "
            "Please add your GROQ_API_KEY in Streamlit Secrets."
        )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_completion_tokens=4000
        )

        return response.choices[0].message.content or "No response received."

    except Exception as error:
        return (
            "Sorry, the AI request failed. Please check your API key "
            "and internet connection, then try again.\n\n"
            f"Error: {error}"
        )


def extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return None

    return None


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    .stApp {
        background:
            radial-gradient(ellipse at 12% 0%, rgba(92,78,180,.16), transparent 34%),
            radial-gradient(ellipse at 90% 8%, rgba(42,164,180,.09), transparent 28%),
            #0b1020;
        color: #eef2ff;
        font-family: 'DM Sans', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: #f4f5ff !important;
    }

    p, label, li {
        color: #cbd2e8;
    }

    [data-testid="stSidebar"] {
        background: #10162a;
        border-right: 1px solid rgba(255,255,255,.08);
    }

    [data-testid="stSidebar"] h1 {
        font-size: 25px;
    }

    .hero {
        padding: 30px;
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(98,78,190,.27), rgba(35,147,167,.12));
        border: 1px solid rgba(180,190,255,.15);
        margin-bottom: 22px;
    }

    .hero-label {
        color: #a8b4ff;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .hero h1 {
        font-size: 38px;
        margin-top: 8px;
        margin-bottom: 10px;
    }

    .hero p {
        font-size: 16px;
        color: #c5cde7;
    }

    .stat-card {
        padding: 20px;
        min-height: 125px;
        border-radius: 18px;
        background: rgba(22,30,54,.9);
        border: 1px solid rgba(180,190,255,.12);
    }

    .stat-label {
        color: #9da9ca;
        font-size: 13px;
        margin-bottom: 12px;
    }

    .stat-value {
        color: #f5f6ff;
        font-size: 29px;
        font-weight: 700;
    }

    .stat-icon {
        font-size: 23px;
        margin-bottom: 8px;
    }

    .section-heading {
        font-size: 22px;
        font-weight: 700;
        margin-top: 18px;
        margin-bottom: 5px;
        color: #f4f5ff;
    }

    .muted {
        color: #9da9ca;
        font-size: 14px;
    }

    .feature-card {
        background: rgba(22,30,54,.85);
        border: 1px solid rgba(180,190,255,.12);
        padding: 20px;
        border-radius: 18px;
        min-height: 150px;
    }

    .feature-icon {
        font-size: 28px;
        margin-bottom: 12px;
    }

    .feature-title {
        font-size: 17px;
        font-weight: 700;
        color: #f5f6ff;
        margin-bottom: 8px;
    }

    .feature-description {
        color: #aeb9d6;
        font-size: 13px;
    }

    div.stButton > button {
        border-radius: 11px;
        min-height: 44px;
        font-weight: 600;
        border: 1px solid rgba(180,190,255,.17);
        transition: .2s ease;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7565e8, #5b8fe8);
        color: white;
        border: none;
    }

    div.stButton > button:hover {
        border-color: #8f91ff;
        color: white;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {
        background: #111a30;
        color: #f4f5ff;
        border: 1px solid #303b5b;
        border-radius: 10px;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: #111a30;
        border-color: #303b5b;
    }

    div[data-testid="stRadio"] label {
        color: #dbe2f7;
    }

    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    hr {
        border-color: rgba(180,190,255,.12);
    }

    .footer {
        color: #7f8aaa;
        font-size: 12px;
        text-align: center;
        padding: 25px 0 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown("# 📘 Study Buddy AI")
    st.caption("Your personal AI learning companion")
    st.divider()

    nav_items = [
        ("🏠", "Dashboard"),
        ("🧠", "AI Quiz"),
        ("📚", "PDF Notes"),
        ("💬", "AI Study Chat"),
        ("📊", "Performance"),
        ("⚙️", "Settings")
    ]

    for symbol, name in nav_items:
        st.button(
            f"{symbol}   {name}",
            key=f"nav_{name}",
            use_container_width=True,
            type="primary" if st.session_state["page"] == name else "secondary",
            on_click=set_page,
            args=(name,)
        )

    st.divider()
    st.markdown("**✨ Study smarter, not harder.**")
    st.caption("Learn • Practice • Improve")


if st.session_state["page"] == "Dashboard":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-label">YOUR SMART STUDY SPACE</div>
            <h1>Welcome to Study Buddy AI 👋</h1>
            <p>
                Learn difficult topics, create notes from PDFs,
                practise questions, and improve your preparation
                with your personal AI study companion.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-icon">🧠</div>
                <div class="stat-label">Quizzes completed</div>
                <div class="stat-value">{st.session_state["quiz_count"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-icon">✅</div>
                <div class="stat-label">Correct answers</div>
                <div class="stat-value">{st.session_state["correct_count"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-icon">📚</div>
                <div class="stat-label">Study activities</div>
                <div class="stat-value">{st.session_state["topics_done"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        '<div class="section-heading">What would you like to do?</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p class="muted">Choose a tool to continue your learning.</p>',
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <div class="feature-title">AI Quiz</div>
                <div class="feature-description">
                    Generate topic-based questions and test your understanding.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.button(
            "Start a quiz →",
            key="dash_quiz",
            use_container_width=True,
            on_click=set_page,
            args=("AI Quiz",)
        )

    with c2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">📚</div>
                <div class="feature-title">PDF Notes</div>
                <div class="feature-description">
                    Upload study material and create summaries and revision notes.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.button(
            "Open my notes →",
            key="dash_pdf",
            use_container_width=True,
            on_click=set_page,
            args=("PDF Notes",)
        )

    with c3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">💬</div>
                <div class="feature-title">AI Study Chat</div>
                <div class="feature-description">
                    Ask questions and understand topics in simple language.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.button(
            "Ask a question →",
            key="dash_chat",
            use_container_width=True,
            on_click=set_page,
            args=("AI Study Chat",)
        )

    st.markdown("---")
    st.markdown("### 🚀 How to get started")
    st.markdown(
        """
        1. **Choose a tool** from the Dashboard or sidebar.
        2. **Enter your topic** or upload your PDF.
        3. **Practise and revise** using the generated study material.
        """
    )


elif st.session_state["page"] == "AI Quiz":

    st.title("🧠 AI Quiz Generator")
    st.write("Create a practice quiz for any subject or topic.")

    with st.form("quiz_generation_form"):
        topic = st.text_input(
            "Enter subject or topic",
            placeholder="Example: C programming, matrices, semiconductors"
        )
        difficulty = st.selectbox(
            "Select difficulty",
            ["Easy", "Medium", "Hard"]
        )
        number_of_questions = st.selectbox(
            "Number of questions",
            [5, 10, 15]
        )
        generate_quiz = st.form_submit_button(
            "Generate quiz ✨",
            type="primary",
            use_container_width=True
        )

    if generate_quiz:
        if not topic.strip():
            st.warning("Please enter a topic first.")
        elif get_client() is None:
            st.error(
                "AI connection is not configured. Add GROQ_API_KEY "
                "in Streamlit Secrets before generating a quiz."
            )
        else:
            prompt = f"""
Create exactly {number_of_questions} multiple-choice questions
about: {topic}

Difficulty: {difficulty}

Return only valid JSON in this format:
{{
  "title": "Quiz title",
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
- Each question must have exactly four options.
- The answer must be an integer from 0 to 3.
- The answer index must point to the correct option.
- Include exactly {number_of_questions} questions.
- Do not include Markdown or text outside the JSON.
"""

            with st.spinner("Preparing your quiz..."):
                result = ask_ai(
                    prompt,
                    "You create accurate educational multiple-choice quizzes. Return valid JSON only."
                )

            quiz = extract_json(result)

            if (
                isinstance(quiz, dict)
                and isinstance(quiz.get("questions"), list)
                and len(quiz["questions"]) > 0
            ):
                valid_questions = []

                for question in quiz["questions"]:
                    if not isinstance(question, dict):
                        continue

                    options = question.get("options", [])
                    answer = question.get("answer")

                    if (
                        isinstance(question.get("question"), str)
                        and isinstance(options, list)
                        and len(options) == 4
                        and isinstance(answer, int)
                        and not isinstance(answer, bool)
                        and 0 <= answer <= 3
                    ):
                        valid_questions.append(question)

                if valid_questions:
                    st.session_state["quiz_data"] = {
                        "title": quiz.get("title", topic),
                        "questions": valid_questions,
                        "topic": topic,
                        "difficulty": difficulty
                    }
                    st.session_state["quiz_answers"] = {}
                    st.session_state["quiz_submitted"] = False
                    st.session_state["quiz_score_saved"] = False
                    st.rerun()
                else:
                    st.error(
                        "The AI returned an invalid quiz format. "
                        "Please generate the quiz again."
                    )
            else:
                st.error(
                    "Could not create the quiz. Please try again with a different topic."
                )

    quiz_data = st.session_state["quiz_data"]

    if quiz_data:
        st.divider()
        st.subheader(quiz_data["title"])
        st.caption(
            f'Topic: {quiz_data["topic"]} · Difficulty: {quiz_data["difficulty"]}'
        )

        questions = quiz_data["questions"]

        if not st.session_state["quiz_submitted"]:
            with st.form("quiz_answer_form"):
                selected_answers = {}

                for i, question in enumerate(questions):
                    st.markdown(f"**Q{i + 1}. {question['question']}**")
                    options = question["options"]

                    selected_answers[i] = st.radio(
                        f"Choose your answer for question {i + 1}",
                        options=list(range(len(options))),
                        format_func=lambda index, opts=options: opts[index],
                        index=None,
                        key=f"quiz_answer_{i}",
                        label_visibility="collapsed"
                    )
                    st.markdown("")

                submitted = st.form_submit_button(
                    "Submit answers",
                    type="primary",
                    use_container_width=True
                )

            if submitted:
                st.session_state["quiz_answers"] = selected_answers
                st.session_state["quiz_submitted"] = True
                st.rerun()

        else:
            score = 0

            for i, question in enumerate(questions):
                selected = st.session_state["quiz_answers"].get(i)
                if selected == question["answer"]:
                    score += 1

            if not st.session_state["quiz_score_saved"]:
                st.session_state["quiz_count"] += 1
                st.session_state["correct_count"] += score
                st.session_state["topics_done"] += 1
                st.session_state["quiz_score_saved"] = True

            percentage = round((score / len(questions)) * 100)

            st.markdown("### 🎉 Quiz Results")
            r1, r2 = st.columns(2)

            with r1:
                st.metric("Your score", f"{score}/{len(questions)}")

            with r2:
                st.metric("Percentage", f"{percentage}%")

            st.progress(percentage / 100)

            if percentage >= 80:
                st.success("Excellent work! You understand this topic well.")
            elif percentage >= 50:
                st.info("Good effort! Revise the incorrect answers and practise again.")
            else:
                st.warning("Keep practising. Review the explanations below.")

            st.markdown("### Answer review")

            for i, question in enumerate(questions):
                selected = st.session_state["quiz_answers"].get(i)
                correct = question["answer"]
                options = question["options"]

                st.markdown(f"**Q{i + 1}. {question['question']}**")

                if selected is None:
                    st.warning("You did not answer this question.")
                elif selected == correct:
                    st.success(f"Correct! {options[correct]}")
                else:
                    st.error(
                        f"Your answer: {options[selected]}\n\n"
                        f"Correct answer: {options[correct]}"
                    )

                st.write(
                    question.get(
                        "explanation",
                        "Review this question to strengthen your understanding."
                    )
                )
                st.divider()

            if st.button(
                "Create another quiz",
                type="primary",
                use_container_width=True
            ):
                st.session_state["quiz_data"] = None
                st.session_state["quiz_answers"] = {}
                st.session_state["quiz_submitted"] = False
                st.session_state["quiz_score_saved"] = False
                st.rerun()


elif st.session_state["page"] == "PDF Notes":

    st.title("📚 PDF Notes Generator")
    st.write("Upload a text-based PDF and turn it into useful study material.")

    uploaded_pdf = st.file_uploader(
        "Upload your study PDF",
        type=["pdf"],
        help="Scanned PDFs may not contain extractable text."
    )

    if uploaded_pdf is not None:
        if st.session_state["pdf_name"] != uploaded_pdf.name:
            st.session_state["pdf_text"] = ""
            st.session_state["pdf_name"] = uploaded_pdf.name
            st.session_state["notes"] = ""

        if not st.session_state["pdf_text"]:
            try:
                reader = PdfReader(BytesIO(uploaded_pdf.getvalue()))
                extracted_pages = [
                    page.extract_text() or "" for page in reader.pages
                ]
                extracted_text = "\n".join(extracted_pages).strip()

                if not extracted_text:
                    st.error(
                        "No readable text was found. If this is a scanned PDF, "
                        "text extraction may not work."
                    )
                else:
                    st.session_state["pdf_text"] = extracted_text

            except Exception as error:
                st.error(f"Could not read the PDF: {error}")

        if st.session_state["pdf_text"]:
            text_content = st.session_state["pdf_text"]

            st.success(f"Loaded: {st.session_state['pdf_name']}")
            st.caption(
                f"Extracted approximately {len(text_content):,} characters."
            )

            with st.expander("Preview extracted text"):
                st.text(text_content[:5000])

            note_type = st.selectbox(
                "What would you like to create?",
                [
                    "Simple Summary",
                    "Exam Preparation Notes",
                    "Important Points",
                    "Revision Notes",
                    "Practice Questions",
                    "Explain in Simple English"
                ]
            )

            language_style = st.selectbox(
                "Writing style",
                ["Simple English", "Detailed English", "Hinglish"]
            )

            if st.button(
                "Generate study material ✨",
                type="primary",
                use_container_width=True
            ):
                if get_client() is None:
                    st.error(
                        "AI connection is not configured. "
                        "Add GROQ_API_KEY in Streamlit Secrets."
                    )
                else:
                    source_text = text_content[:60000]

                    prompt = f"""
Create study material from the following PDF text.

Requested format: {note_type}
Language style: {language_style}

Instructions:
- Use information from the supplied text.
- Keep the notes clear and well organised.
- Use suitable headings and bullet points.
- For exam notes, focus on definitions, concepts, differences,
  formulas and likely exam points when relevant.
- For practice questions, include answers after the questions.
- Do not invent facts that are not supported by the text.
- If the text is incomplete, mention that clearly.

PDF TEXT:
{source_text}
"""

                    with st.spinner("Preparing your study material..."):
                        generated_notes = ask_ai(
                            prompt,
                            "You are an educational assistant who creates accurate, student-friendly study notes."
                        )

                    if generated_notes.startswith("Sorry, the AI request failed."):
                        st.error(generated_notes)
                    elif generated_notes.startswith("AI connection is not configured."):
                        st.error(generated_notes)
                    else:
                        st.session_state["notes"] = generated_notes
                        st.session_state["last_summary"] = note_type
                        st.session_state["topics_done"] += 1
                        st.rerun()

            if st.session_state["notes"]:
                st.divider()
                st.subheader("Your Study Material")
                st.markdown(st.session_state["notes"])

                st.download_button(
                    "Download notes as TXT",
                    data=st.session_state["notes"],
                    file_name="study_buddy_notes.txt",
                    mime="text/plain",
                    use_container_width=True
                )

                if st.button("Clear generated notes"):
                    st.session_state["notes"] = ""
                    st.rerun()

    else:
        st.info("Upload a PDF to begin creating your notes.")


elif st.session_state["page"] == "AI Study Chat":

    st.title("💬 AI Study Chat")
    st.write(
        "Ask questions about your subjects and get explanations "
        "that match your learning style."
    )

    response_style = st.selectbox(
        "Choose explanation style",
        [
            "Simple English",
            "Step-by-step explanation",
            "Exam-ready answer",
            "Hinglish explanation"
        ]
    )

    if st.button("Clear chat"):
        st.session_state["chat_history"] = []
        st.rerun()

    st.divider()

    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_question = st.chat_input("Ask a study question...")

    if user_question:
        st.session_state["chat_history"].append(
            {"role": "user", "content": user_question}
        )

        with st.chat_message("user"):
            st.markdown(user_question)

        system_prompt = f"""
You are Study Buddy AI, a friendly educational assistant.

The student wants this response style: {response_style}.

Rules:
- Explain concepts accurately and clearly.
- Use simple language suitable for a beginner.
- For programming, provide complete code when requested.
- For maths, show steps and calculations.
- For exam-ready answers, use headings and points.
- If you do not know something, be honest.
"""

        previous_messages = st.session_state["chat_history"][-12:]
        client = get_client()

        if client is None:
            answer = (
                "AI connection is not configured. Please add "
                "GROQ_API_KEY in Streamlit Secrets."
            )
        else:
            try:
                with st.spinner("Thinking..."):
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=[
                            {"role": "system", "content": system_prompt}
                        ] + previous_messages,
                        temperature=0.5,
                        max_completion_tokens=4000
                    )

                    answer = (
                        response.choices[0].message.content
                        or "I could not generate a response. Please try again."
                    )

            except Exception as error:
                answer = (
                    "The AI request failed. Please check your API key "
                    "and try again.\n\n"
                    f"Error: {error}"
                )

        st.session_state["chat_history"].append(
            {"role": "assistant", "content": answer}
        )

        with st.chat_message("assistant"):
            st.markdown(answer)


elif st.session_state["page"] == "Performance":

    st.title("📊 Your Performance")
    st.write("Review your study activity during this session.")

    quiz_count = st.session_state["quiz_count"]
    correct_count = st.session_state["correct_count"]
    topics_done = st.session_state["topics_done"]

    average_score = round(correct_count / quiz_count, 2) if quiz_count else 0

    p1, p2, p3 = st.columns(3)

    with p1:
        st.metric("Quizzes completed", quiz_count)

    with p2:
        st.metric("Correct answers", correct_count)

    with p3:
        st.metric("Study activities", topics_done)

    st.divider()
    st.subheader("Learning overview")

    if quiz_count == 0:
        st.info(
            "You have not completed a quiz in this session yet. "
            "Complete a quiz to see your results here."
        )
    else:
        st.write(f"Average correct answers per quiz: **{average_score}**")
        st.write(f"Total correct answers recorded: **{correct_count}**")
        st.caption(
            "These statistics are for the current app session. "
            "They may reset when the session is restarted."
        )

    st.divider()
    st.subheader("Study suggestions")
    st.markdown(
        """
        - Revise the topics where you make mistakes.
        - Use PDF Notes to prepare short revision material.
        - Try quizzes with different difficulty levels.
        - Ask AI Study Chat to explain difficult concepts step by step.
        """
    )


elif st.session_state["page"] == "Settings":

    st.title("⚙️ Settings")
    st.write("Manage your AI connection and current study session.")

    st.subheader("AI connection")
    client = get_client()

    if client is None:
        st.warning(
            "Groq API key not found. Add GROQ_API_KEY to Streamlit Secrets."
        )
    else:
        st.success("Groq API key is available.")

        if st.button(
            "Test AI connection",
            type="primary",
            use_container_width=True
        ):
            with st.spinner("Testing connection..."):
                test_result = ask_ai(
                    "Reply with exactly: Connection successful.",
                    "You are a connection test assistant."
                )

            if test_result.startswith("Sorry, the AI request failed."):
                st.error(test_result)
            elif test_result.startswith("AI connection is not configured."):
                st.error(test_result)
            else:
                st.success("The AI service responded successfully.")
                st.write(test_result)

    st.divider()
    st.subheader("Session information")
    st.write(f"Current page: **{st.session_state['page']}**")
    st.write(f"Quizzes completed: **{st.session_state['quiz_count']}**")
    st.write(f"Study activities: **{st.session_state['topics_done']}**")

    st.divider()
    st.subheader("Reset session")
    st.warning(
        "This clears your current quiz, chat history, generated notes, "
        "and session statistics."
    )

    if st.button(
        "Reset study session",
        type="primary",
        use_container_width=True
    ):
        for key, value in defaults.items():
            st.session_state[key] = value
        st.rerun()


st.markdown(
    """
    <div class="footer">
        Study Buddy AI · Learn at your own pace ✨
    </div>
    """,
    unsafe_allow_html=True
)
