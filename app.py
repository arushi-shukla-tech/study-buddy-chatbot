import os
import json
import random
import streamlit as st
from groq import Groq
from pypdf import PdfReader

# ==================== PAGE CONFIG ====================

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== SESSION STATE ====================

defaults = {
    "chat_messages": [],
    "quiz_questions": [],
    "quiz_answers": {},
    "quiz_submitted": False,
    "quiz_score": None,
    "total_answered": 0,
    "total_correct": 0,
    "pdf_text": "",
    "pdf_name": "",
    "notes": "",
    "quiz_count": 5,
    "difficulty": "Medium",
    "language": "Simple English",
    "api_key": os.getenv("GROQ_API_KEY", ""),
    "topic": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ==================== CSS ====================

st.markdown("""
<style>
.stApp {
    background-color: #f4f7fb;
    color: #17233c;
}

[data-testid="stSidebar"] {
    background-color: #eaf0fa;
}

h1, h2, h3, h4, p, label, li {
    color: #17233c;
}

.stTextInput input,
.stTextArea textarea,
[data-testid="stChatInput"] textarea {
    background-color: #ffffff !important;
    color: #17233c !important;
    -webkit-text-fill-color: #17233c !important;
    caret-color: #17233c !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder,
[data-testid="stChatInput"] textarea::placeholder {
    color: #64748b !important;
    -webkit-text-fill-color: #64748b !important;
    opacity: 1 !important;
}

[data-testid="stChatInput"] {
    background-color: #ffffff !important;
}

[data-testid="stChatMessage"] {
    background-color: #ffffff !important;
    color: #17233c !important;
    border: 1px solid #dbe3ef;
    border-radius: 12px;
    padding: 12px;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] h4,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] em {
    color: #17233c !important;
    -webkit-text-fill-color: #17233c !important;
}

[data-testid="stChatMessage"] code,
[data-testid="stChatMessage"] pre {
    background-color: #eef2f8 !important;
    color: #17233c !important;
    -webkit-text-fill-color: #17233c !important;
}

[data-testid="stChatMessage"] pre code {
    color: #17233c !important;
    -webkit-text-fill-color: #17233c !important;
}

.stButton button {
    border-radius: 8px;
    font-weight: 600;
}

div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #dbe3ef;
    padding: 15px;
    border-radius: 12px;
}

hr {
    border-color: #dbe3ef;
}
</style>
""", unsafe_allow_html=True)

# ==================== HELPER FUNCTIONS ====================

def get_client():
    api_key = st.session_state.api_key.strip()

    if not api_key:
        return None

    return Groq(api_key=api_key)


def ask_ai(prompt, system_prompt=None, max_tokens=3000):
    client = get_client()

    if client is None:
        return None, "Groq API key missing. Settings mein apni API key enter karo."

    messages = []

    if system_prompt:
        messages.append({
            "role": "system",
            "content": system_prompt
        })

    messages.append({
        "role": "user",
        "content": prompt
    })

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.4
        )

        answer = response.choices[0].message.content

        if not answer:
            return None, "AI se empty response mila. Dobara try karo."

        return answer, None

    except Exception as e:
        return None, f"AI request failed: {str(e)}"


def extract_pdf_text(uploaded_file):
    try:
        reader = PdfReader(uploaded_file)
        pages = []

        for page in reader.pages:
            pages.append(page.extract_text() or "")

        return "\n".join(pages).strip(), None

    except Exception as e:
        return "", f"PDF read nahi ho payi: {str(e)}"


def reset_quiz():
    st.session_state.quiz_questions = []
    st.session_state.quiz_answers = {}
    st.session_state.quiz_submitted = False
    st.session_state.quiz_score = None


def get_study_source():
    if st.session_state.pdf_text.strip():
        return st.session_state.pdf_text[:18000]

    if st.session_state.notes.strip():
        return st.session_state.notes[:18000]

    return ""


def generate_quiz(topic, count, difficulty, source):
    system_prompt = """
You are a helpful educational quiz generator.
Create questions appropriate to the requested difficulty.
Return ONLY valid JSON in this format:
{
  "questions": [
    {
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": 0,
      "explanation": "Short explanation"
    }
  ]
}
The answer field must be an integer from 0 to 3.
Create exactly the requested number of questions.
Do not add markdown fences around the JSON.
"""

    prompt = f"""
Topic: {topic}
Difficulty: {difficulty}
Number of questions: {count}

Study material:
{source if source else "Use standard educational knowledge for this topic."}

Generate the quiz using the required JSON format.
"""

    answer, error = ask_ai(
        prompt,
        system_prompt=system_prompt,
        max_tokens=5000
    )

    if error:
        return None, error

    try:
        cleaned = answer.strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0].strip()

        data = json.loads(cleaned)
        questions = data.get("questions", [])

        valid_questions = []

        for q in questions:
            options = q.get("options", [])
            correct = q.get("answer")

            if (
                isinstance(q.get("question"), str)
                and isinstance(options, list)
                and len(options) == 4
                and isinstance(correct, int)
                and 0 <= correct <= 3
            ):
                valid_questions.append({
                    "question": q["question"],
                    "options": options,
                    "answer": correct,
                    "explanation": q.get("explanation", "")
                })

        if not valid_questions:
            return None, "Valid questions generate nahi hue. Dobara try karo."

        return valid_questions[:count], None

    except (json.JSONDecodeError, TypeError, ValueError):
        return None, "Quiz response read nahi ho paya. Dobara generate karo."


# ==================== SIDEBAR ====================

with st.sidebar:
    st.title("📚 Study Buddy AI")
    st.caption("Your personal AI study assistant")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Home",
            "📄 PDF Notes",
            "📝 AI Quiz",
            "💬 Study Chat",
            "📊 Performance",
            "⚙️ Settings"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    if st.session_state.pdf_name:
        st.success(f"PDF loaded: {st.session_state.pdf_name}")
    else:
        st.info("Notes ke liye PDF upload kar sakte ho.")

    if st.session_state.api_key:
        st.caption("API key configured")
    else:
        st.warning("Settings mein Groq API key add karo.")


# ==================== HOME ====================

if page == "🏠 Home":
    st.title("📚 Welcome to Study Buddy AI")
    st.write(
        "Learn topics, create notes, practise questions, "
        "and track your study progress in one place."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Questions Attempted",
            st.session_state.total_answered
        )

    with col2:
        st.metric(
            "Correct Answers",
            st.session_state.total_correct
        )

    with col3:
        if st.session_state.total_answered:
            accuracy = (
                st.session_state.total_correct
                / st.session_state.total_answered
            ) * 100
        else:
            accuracy = 0

        st.metric("Accuracy", f"{accuracy:.1f}%")

    st.subheader("What would you like to do?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📄 PDF Notes")
        st.write("Upload a PDF and generate easy-to-understand notes.")

        if st.button("Open PDF Notes", use_container_width=True):
            st.session_state["navigation_target"] = "📄 PDF Notes"
            st.rerun()

        st.markdown("### 📝 AI Quiz")
        st.write("Create practice quizzes on your study topics.")

        if st.button("Open AI Quiz", use_container_width=True):
            st.session_state["navigation_target"] = "📝 AI Quiz"
            st.rerun()

    with col2:
        st.markdown("### 💬 Study Chat")
        st.write("Ask questions and understand difficult concepts.")

        if st.button("Open Study Chat", use_container_width=True):
            st.session_state["navigation_target"] = "💬 Study Chat"
            st.rerun()

        st.markdown("### 📊 Performance")
        st.write("Review your quiz scores and accuracy.")

        if st.button("Open Performance", use_container_width=True):
            st.session_state["navigation_target"] = "📊 Performance"
            st.rerun()

    if st.session_state.get("navigation_target"):
        st.info(
            "Selected section: "
            + st.session_state["navigation_target"]
            + ". Use the Navigation menu in the sidebar to open it."
        )


# ==================== PDF NOTES ====================

elif page == "📄 PDF Notes":
    st.title("📄 PDF Notes Generator")
    st.write("Upload your study PDF and generate simplified notes.")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        key="notes_pdf_uploader"
    )

    if uploaded_file is not None:
        if st.button("Load PDF", type="primary"):
            with st.spinner("Reading PDF..."):
                text, error = extract_pdf_text(uploaded_file)

            if error:
                st.error(error)

            elif not text:
                st.warning(
                    "PDF se readable text nahi mila. "
                    "Ho sakta hai PDF scanned image ho."
                )

            else:
                st.session_state.pdf_text = text
                st.session_state.pdf_name = uploaded_file.name
                st.session_state.notes = ""
                st.success("PDF successfully loaded!")

    if st.session_state.pdf_text:
        st.subheader("PDF Information")
        st.write(f"**File:** {st.session_state.pdf_name}")
        st.write(f"**Extracted characters:** {len(st.session_state.pdf_text)}")

        with st.expander("Preview extracted text"):
            st.text(st.session_state.pdf_text[:5000])

        notes_style = st.selectbox(
            "Notes style",
            [
                "Simple English",
                "Detailed exam notes",
                "Short revision notes",
                "Question and answer format"
            ]
        )

        if st.button("Generate Notes", type="primary"):
            system_prompt = """
You are an educational notes assistant.
Use the supplied study material as the main source.
Keep the language clear and easy to understand.
Preserve important headings, definitions, formulas, examples,
and relevant points. Do not invent claims about the source.
If information is missing, state that clearly.
"""

            prompt = f"""
Create study notes from the following PDF text.

Notes style: {notes_style}
Preferred language: {st.session_state.language}

Instructions:
- Use headings and bullet points.
- Explain difficult concepts in simple words.
- Include formulas present in the source.
- Include important definitions and examples.
- Do not silently invent information absent from the source.

PDF text:
{st.session_state.pdf_text[:18000]}
"""

            with st.spinner("Generating notes..."):
                answer, error = ask_ai(
                    prompt,
                    system_prompt=system_prompt,
                    max_tokens=6000
                )

            if error:
                st.error(error)
            else:
                st.session_state.notes = answer
                st.success("Notes generated!")

    if st.session_state.notes:
        st.divider()
        st.subheader("Your Notes")
        st.markdown(st.session_state.notes)

        st.download_button(
            "Download Notes as TXT",
            data=st.session_state.notes,
            file_name="study_notes.txt",
            mime="text/plain"
        )


# ==================== AI QUIZ ====================

elif page == "📝 AI Quiz":
    st.title("📝 AI Quiz Generator")
    st.write("Generate a quiz from your PDF, notes, or a topic.")

    topic = st.text_input(
        "Enter topic",
        value=st.session_state.topic,
        placeholder="e.g. BJT, Semiconductor, C Programming"
    )

    count = st.selectbox(
        "Number of questions",
        [5, 10, 15, 20],
        index=[5, 10, 15, 20].index(st.session_state.quiz_count)
        if st.session_state.quiz_count in [5, 10, 15, 20]
        else 0
    )

    difficulty = st.selectbox(
        "Difficulty",
        ["Easy", "Medium", "Hard"],
        index=["Easy", "Medium", "Hard"].index(
            st.session_state.difficulty
        )
        if st.session_state.difficulty in ["Easy", "Medium", "Hard"]
        else 1
    )

    source = get_study_source()

    if source:
        st.info("Quiz will use your loaded PDF or generated notes where relevant.")
    else:
        st.info("No PDF or notes loaded. Quiz will use the selected topic.")

    if st.button("Generate Quiz", type="primary"):
        if not topic.strip() and not source:
            st.warning("Topic enter karo ya pehle PDF load karo.")

        else:
            actual_topic = topic.strip() or st.session_state.pdf_name

            st.session_state.topic = actual_topic
            st.session_state.quiz_count = count
            st.session_state.difficulty = difficulty

            with st.spinner("Creating your quiz..."):
                questions, error = generate_quiz(
                    actual_topic,
                    count,
                    difficulty,
                    source
                )

            if error:
                st.error(error)

            else:
                st.session_state.quiz_questions = questions
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_score = None
                st.success(f"{len(questions)} questions ready!")

    if st.session_state.quiz_questions:
        st.divider()
        st.subheader("Practice Questions")

        if not st.session_state.quiz_submitted:
            with st.form("quiz_form"):
                for i, question in enumerate(
                    st.session_state.quiz_questions
                ):
                    st.markdown(f"**Q{i + 1}. {question['question']}**")

                    selected = st.radio(
                        "Select your answer",
                        options=range(4),
                        format_func=lambda x, q=question: q["options"][x],
                        key=f"quiz_question_{i}",
                        index=None
                    )

                    st.session_state.quiz_answers[i] = selected
                    st.divider()

                submitted = st.form_submit_button(
                    "Submit Quiz",
                    type="primary"
                )

            if submitted:
                score = 0
                attempted = 0

                for i, question in enumerate(
                    st.session_state.quiz_questions
                ):
                    selected = st.session_state.quiz_answers.get(i)

                    if selected is not None:
                        attempted += 1

                        if selected == question["answer"]:
                            score += 1

                st.session_state.quiz_score = score
                st.session_state.quiz_submitted = True
                st.session_state.total_answered += attempted
                st.session_state.total_correct += score
                st.rerun()

        else:
            score = st.session_state.quiz_score or 0
            total = len(st.session_state.quiz_questions)

            st.metric("Your Score", f"{score} / {total}")

            if total:
                st.progress(score / total)

            st.subheader("Answer Review")

            for i, question in enumerate(
                st.session_state.quiz_questions
            ):
                selected = st.session_state.quiz_answers.get(i)
                correct = question["answer"]

                st.markdown(f"**Q{i + 1}. {question['question']}**")

                if selected is None:
                    st.warning("Not attempted.")
                elif selected == correct:
                    st.success(f"Correct: {question['options'][correct]}")
                else:
                    st.error(
                        f"Your answer: {question['options'][selected]}"
                    )
                    st.info(
                        f"Correct answer: {question['options'][correct]}"
                    )

                if question.get("explanation"):
                    st.write(f"Explanation: {question['explanation']}")

                st.divider()

            if st.button("Try Another Quiz"):
                reset_quiz()
                st.rerun()


# ==================== STUDY CHAT ====================

elif page == "💬 Study Chat":
    st.title("💬 Study Chat")
    st.write("Ask a question about your studies.")

    col1, col2 = st.columns([3, 1])

    with col1:
        st.caption("Ask for explanations, examples, definitions, or revision help.")

    with col2:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

    # Display existing chat messages.
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input.
    user_prompt = st.chat_input(
        "Ask your study question...",
        key="study_chat_input"
    )

    if user_prompt:
        # Show and save the user's message.
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_prompt
        })

        with st.chat_message("user"):
            st.markdown(user_prompt)

        # Include recent conversation for context.
        recent_messages = st.session_state.chat_messages[-12:]

        system_prompt = f"""
You are Study Buddy AI, a helpful educational assistant.

Preferred response language: {st.session_state.language}

Instructions:
- Explain concepts clearly and step by step.
- Use simple language suitable for a student.
- Include examples and formulas when relevant.
- If the user asks about their uploaded notes, use the provided source.
- Do not claim that information comes from a PDF unless the source supports it.
- If a question is ambiguous, explain the likely interpretation.
"""

        pdf_context = get_study_source()

        messages = [{"role": "system", "content": system_prompt}]

        if pdf_context:
            messages.append({
                "role": "system",
                "content": (
                    "Relevant study material:\n"
                    + pdf_context[:10000]
                )
            })

        messages.extend(recent_messages)

        client = get_client()

        if client is None:
            error_message = (
                "Groq API key missing. Settings mein API key add karo."
            )

            with st.chat_message("assistant"):
                st.markdown(error_message)

            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": error_message
            })

        else:
            try:
                with st.chat_message("assistant"):
                    with st.spinner("Thinking..."):
                        response = client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=messages,
                            max_tokens=3000,
                            temperature=0.4
                        )

                        answer = (
                            response.choices[0].message.content
                            or "AI se response nahi mila. Dobara try karo."
                        )

                    st.markdown(answer)

                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:
                error_message = f"AI error: {str(e)}"

                with st.chat_message("assistant"):
                    st.error(error_message)

                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": error_message
                })


# ==================== PERFORMANCE ====================

elif page == "📊 Performance":
    st.title("📊 Study Performance")
    st.write("Your quiz progress for this session.")

    total = st.session_state.total_answered
    correct = st.session_state.total_correct
    incorrect = total - correct

    accuracy = (correct / total * 100) if total else 0

    col1, col2, col3 = st.columns(3)

    col1.metric("Attempted", total)
    col2.metric("Correct", correct)
    col3.metric("Accuracy", f"{accuracy:.1f}%")

    st.divider()

    if total:
        st.subheader("Answer Summary")

        st.write(f"Correct answers: {correct}")
        st.progress(accuracy / 100)

        st.write(f"Incorrect answers: {incorrect}")

        if accuracy >= 80:
            st.success("Good progress! Keep practising.")
        elif accuracy >= 50:
            st.info("Review incorrect answers and practise again.")
        else:
            st.warning("Revise the topic and try another quiz.")

    else:
        st.info(
            "Abhi koi quiz attempt nahi kiya. "
            "AI Quiz section se quiz attempt karo."
        )

    st.caption(
        "Performance counts are stored for the current Streamlit session. "
        "They may reset when the session is restarted."
    )

    if st.button("Reset Performance"):
        st.session_state.total_answered = 0
        st.session_state.total_correct = 0
        st.rerun()


# ==================== SETTINGS ====================

elif page == "⚙️ Settings":
    st.title("⚙️ Settings")

    st.subheader("Groq API")

    st.write(
        "AI features use the Groq API. Enter your API key below. "
        "Keep your key private."
    )

    with st.form("settings_form"):
        api_key = st.text_input(
            "Groq API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder="Enter your Groq API key"
        )

        language = st.selectbox(
            "Preferred response language",
            ["Simple English", "Hindi", "Hinglish"],
            index=["Simple English", "Hindi", "Hinglish"].index(
                st.session_state.language
            )
            if st.session_state.language in [
                "Simple English", "Hindi", "Hinglish"
            ]
            else 0
        )

        save_settings = st.form_submit_button(
            "Save Settings",
            type="primary"
        )

    if save_settings:
        st.session_state.api_key = api_key.strip()
        st.session_state.language = language
        st.success("Settings saved for this session.")

    st.divider()

    st.subheader("Current Session")

    st.write(f"Chat messages: {len(st.session_state.chat_messages)}")
    st.write(f"Quiz questions in current quiz: {len(st.session_state.quiz_questions)}")
    st.write(f"PDF loaded: {'Yes' if st.session_state.pdf_text else 'No'}")

    if st.button("Clear Loaded PDF and Notes"):
        st.session_state.pdf_text = ""
        st.session_state.pdf_name = ""
        st.session_state.notes = ""
        st.success("Loaded PDF and notes cleared.")
        st.rerun()

    st.caption(
        "For deployment, store your API key in Streamlit secrets "
        "or an environment variable instead of sharing it in code."
    )