import streamlit as st
from groq import Groq
from pypdf import PdfReader
import json
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

st.set_page_config(page_title="Study Buddy AI", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.stApp { background: #0b1020; color: #f3f4f6; }
[data-testid="stSidebar"] { background: #111827; }
.block-container { max-width: 1150px; padding-top: 1.5rem; }
div.stButton > button { border-radius: 10px; font-weight: 600; min-height: 42px; }
div[data-testid="stMetric"] { background: #151d32; padding: 14px; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)


def initialize():
    defaults = {
        "notes": "",
        "file_name": "",
        "chat_history": [],
        "quiz_questions": [],
        "quiz_topic": "",
        "quiz_count": 10,
        "quiz_submitted": False,
        "quiz_answers": {},
        "last_score": None,
        "summary": ""
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize()


def get_client():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        key = ""

    if not key:
        key = os.getenv("GROQ_API_KEY", "")

    if not key:
        return None

    return Groq(api_key=key)


def ask_ai(prompt, system_prompt="You are a helpful college study assistant.",
            max_tokens=2500):
    client = get_client()

    if client is None:
        raise ValueError(
            "Groq API key missing. Add GROQ_API_KEY in Streamlit Secrets."
        )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=max_tokens
    )

    return response.choices[0].message.content or ""


def parse_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")

        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])

        raise ValueError("AI returned invalid JSON. Please try again.")


def read_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    pages = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return "\n".join(pages).strip()


def create_question_batch(topic, notes, first_number, batch_size):
    if notes:
        source = notes[:12000]
    else:
        source = (
            "No uploaded notes. Use accurate general knowledge "
            "about the requested topic."
        )

    prompt = f"""
Create exactly {batch_size} different MCQ questions.

Topic: {topic}

Study material:
{source}

Question numbers: {first_number} to {first_number + batch_size - 1}.

Return ONLY valid JSON in this format:
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
1. Generate exactly {batch_size} questions.
2. Every question must have exactly four options.
3. Answer must be an integer: 0, 1, 2, or 3.
4. Explanation must explain the correct answer.
5. Do not repeat questions in this batch.
6. Use clear college-level language.
7. If notes are provided, prioritize them.
8. Return JSON only. Do not add Markdown.
"""

    result = ask_ai(
        prompt,
        system_prompt=(
            "You are an accurate educational quiz generator. "
            "Follow the requested JSON structure exactly."
        ),
        max_tokens=min(6000, 500 + batch_size * 350)
    )

    data = parse_json(result)
    raw_questions = data.get("questions", [])
    valid_questions = []

    for item in raw_questions:
        if not isinstance(item, dict):
            continue

        question = item.get("question")
        options = item.get("options")
        answer = item.get("answer")
        explanation = item.get("explanation", "")

        if not isinstance(question, str) or not question.strip():
            continue

        if not isinstance(options, list) or len(options) != 4:
            continue

        if not all(
            isinstance(option, str) and option.strip()
            for option in options
        ):
            continue

        if (
            not isinstance(answer, int)
            or isinstance(answer, bool)
            or answer not in range(4)
        ):
            continue

        valid_questions.append({
            "question": question.strip(),
            "options": [option.strip() for option in options],
            "answer": answer,
            "explanation": str(explanation).strip()
        })

    return valid_questions


def generate_quiz(topic, notes, total_questions):
    batch_size = 10
    batches = []

    for start in range(0, total_questions, batch_size):
        size = min(batch_size, total_questions - start)
        batches.append((start, size))

    results = {}
    errors = []
    progress = st.progress(0)
    status = st.empty()

    with ThreadPoolExecutor(max_workers=min(3, len(batches))) as executor:
        future_map = {}

        for start, size in batches:
            future = executor.submit(
                create_question_batch,
                topic,
                notes,
                start + 1,
                size
            )
            future_map[future] = start

        completed = 0

        for future in as_completed(future_map):
            start = future_map[future]

            try:
                results[start] = future.result()
            except Exception as error:
                results[start] = []
                errors.append(str(error))

            completed += 1
            progress.progress(completed / len(batches))
            status.write(
                f"Generating quiz: {completed}/{len(batches)} batches"
            )

    progress.empty()
    status.empty()

    questions = []

    for start, size in batches:
        questions.extend(results.get(start, []))

    return questions[:total_questions], errors


def clear_quiz():
    st.session_state.quiz_questions = []
    st.session_state.quiz_answers = {}
    st.session_state.quiz_submitted = False
    st.session_state.last_score = None


st.sidebar.title("🎓 Study Buddy AI")
st.sidebar.caption("Your personal study assistant")

page = st.sidebar.radio(
    "Choose a section",
    [
        "Dashboard",
        "AI Study Chat",
        "Upload Notes",
        "Quick Summary",
        "Quiz Generator"
    ]
)

st.sidebar.divider()

if st.session_state.notes:
    st.sidebar.success(
        f"Notes ready: {len(st.session_state.notes):,} characters"
    )
else:
    st.sidebar.info("Upload a PDF or paste notes to begin.")

st.sidebar.caption("AI features require a Groq API key.")


if page == "Dashboard":
    st.title("🎓 Study Buddy AI")
    st.write("Learn smarter, revise faster, and test your knowledge.")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Study Material",
        "Ready" if st.session_state.notes else "Not added"
    )

    col2.metric(
        "Quiz Questions",
        len(st.session_state.quiz_questions)
    )

    if st.session_state.last_score is None:
        score_text = "Not attempted"
    else:
        score_text = f"{st.session_state.last_score}%"

    col3.metric("Last Quiz Score", score_text)

    st.divider()
    st.subheader("Start learning")

    st.markdown("""
    - **AI Study Chat:** Ask questions about any subject.
    - **Upload Notes:** Upload a PDF or paste your notes.
    - **Quick Summary:** Create revision notes.
    - **Quiz Generator:** Generate up to 100 AI-created MCQs.
    """)


elif page == "Upload Notes":
    st.title("📚 Upload Study Notes")

    uploaded = st.file_uploader(
        "Upload a text-based PDF",
        type=["pdf"]
    )

    if uploaded is not None:
        if st.button("Read PDF", type="primary"):
            try:
                with st.spinner("Reading PDF..."):
                    text = read_pdf(uploaded)

                if not text:
                    st.warning(
                        "No readable text found. "
                        "This PDF may contain scanned images."
                    )
                else:
                    st.session_state.notes = text
                    st.session_state.file_name = uploaded.name
                    clear_quiz()
                    st.success(
                        f"PDF loaded: {len(text):,} characters."
                    )

            except Exception as error:
                st.error(f"PDF reading failed: {error}")

    st.divider()
    st.subheader("Or paste your notes")

    pasted = st.text_area(
        "Study material",
        value=st.session_state.notes,
        height=250,
        placeholder="Paste your class notes here..."
    )

    if st.button("Save Notes", type="primary"):
        if pasted.strip():
            st.session_state.notes = pasted.strip()
            st.session_state.file_name = "Pasted notes"
            clear_quiz()
            st.success("Notes saved successfully.")
        else:
            st.warning("Please paste your notes first.")

    if st.session_state.notes:
        with st.expander("Preview saved notes"):
            st.write(st.session_state.notes[:3000])


elif page == "AI Study Chat":
    st.title("💬 AI Study Chat")
    st.write("Ask questions about your subjects and notes.")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask your study question...")

    if prompt:
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                client = get_client()

                if client is None:
                    raise ValueError(
                        "Add GROQ_API_KEY in Streamlit Secrets."
                    )

                history = st.session_state.chat_history[-10:]

                messages = [{
                    "role": "system",
                    "content": (
                        "You are Study Buddy AI, a helpful college tutor. "
                        "Explain in simple English with examples when useful. "
                        "Use the supplied notes when relevant.\n\n"
                        "STUDY NOTES:\n"
                        + st.session_state.notes[:10000]
                    )
                }]

                messages.extend(history)

                with st.spinner("Preparing your answer..."):
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=messages,
                        temperature=0.4,
                        max_tokens=1800
                    )

                answer = (
                    response.choices[0].message.content
                    or "No answer was returned."
                )

                st.markdown(answer)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as error:
                st.error(f"Could not get an answer: {error}")

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()


elif page == "Quick Summary":
    st.title("⚡ Quick Summary")
    st.write("Turn lengthy notes into revision points.")

    if not st.session_state.notes:
        st.warning("Please add study notes first.")
    else:
        if st.button("Generate Summary", type="primary"):
            try:
                with st.spinner("Creating summary..."):
                    summary = ask_ai(
                        "Summarize these notes in simple English. "
                        "Use headings, key definitions, formulas where "
                        "present, and a short revision checklist. "
                        "Do not invent facts.\n\n"
                        + st.session_state.notes[:16000],
                        max_tokens=3000
                    )

                st.session_state.summary = summary

            except Exception as error:
                st.error(f"Summary failed: {error}")

        if st.session_state.summary:
            st.markdown(st.session_state.summary)

            st.download_button(
                "Download Summary",
                data=st.session_state.summary,
                file_name="study_summary.txt",
                mime="text/plain"
            )


elif page == "Quiz Generator":
    st.title("🧠 AI Quiz Generator")

    st.write(
        "Generate new questions from your notes or any subject topic."
    )

    topic = st.text_input(
        "Subject or topic",
        value=st.session_state.quiz_topic,
        placeholder="Example: C Programming, Applied Chemistry, Matrices"
    )

    count = st.select_slider(
        "Number of questions",
        options=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        value=st.session_state.quiz_count
    )

    st.caption(
        "Questions are generated in batches of 10. "
        "Speed depends on API availability and limits."
    )

    if st.button(
        "⚡ Generate New Quiz",
        type="primary",
        use_container_width=True
    ):
        if not topic.strip():
            st.warning("Please enter a subject or topic.")
        else:
            clear_quiz()

            try:
                questions, errors = generate_quiz(
                    topic.strip(),
                    st.session_state.notes,
                    count
                )

                st.session_state.quiz_questions = questions
                st.session_state.quiz_topic = topic.strip()
                st.session_state.quiz_count = count

                if questions:
                    st.success(
                        f"Quiz ready! {len(questions)} questions generated."
                    )

                if errors:
                    st.warning(
                        f"{len(errors)} batch(es) failed. "
                        f"{len(questions)} questions are available. "
                        "You can retry if some questions are missing."
                    )

                if not questions:
                    st.error(
                        "No questions generated. Check your API key, "
                        "API quota, and internet connection."
                    )

            except Exception as error:
                st.error(f"Quiz generation failed: {error}")

    questions = st.session_state.quiz_questions

    if questions:
        st.divider()
        st.subheader(f"Topic: {st.session_state.quiz_topic}")

        with st.form("study_buddy_quiz_form"):
            selected_answers = {}

            for index, question in enumerate(questions):
                st.markdown(
                    f"**Q{index + 1}. {question['question']}**"
                )

                previous = st.session_state.quiz_answers.get(
                    str(index)
                )

                selected_answers[str(index)] = st.radio(
                    "Choose an answer",
                    options=[0, 1, 2, 3],
                    index=previous,
                    format_func=lambda n, opts=question["options"]: (
                        f"{chr(65 + n)}. {opts[n]}"
                    ),
                    key=f"quiz_answer_{index}",
                    label_visibility="collapsed"
                )

                st.divider()

            submitted = st.form_submit_button(
                "Submit Quiz",
                type="primary",
                use_container_width=True
            )

        if submitted:
            st.session_state.quiz_answers = selected_answers
            st.session_state.quiz_submitted = True
            st.rerun()

        if st.session_state.quiz_submitted:
            correct = 0

            for index, question in enumerate(questions):
                if (
                    st.session_state.quiz_answers.get(str(index))
                    == question["answer"]
                ):
                    correct += 1

            total = len(questions)
            percentage = round(correct * 100 / total)

            st.session_state.last_score = percentage

            st.subheader("📊 Your Result")

            col1, col2, col3 = st.columns(3)
            col1.metric("Correct", correct)
            col2.metric("Incorrect", total - correct)
            col3.metric("Score", f"{percentage}%")

            st.progress(percentage / 100)

            st.subheader("Answer Review")

            for index, question in enumerate(questions):
                user_answer = st.session_state.quiz_answers.get(
                    str(index)
                )

                is_correct = user_answer == question["answer"]

                label = "✅ Correct" if is_correct else "❌ Incorrect"

                with st.expander(f"Question {index + 1}: {label}"):
                    st.write(question["question"])

                    if user_answer is not None:
                        st.write(
                            "**Your answer:** "
                            + question["options"][user_answer]
                        )

                    st.write(
                        "**Correct answer:** "
                        + question["options"][question["answer"]]
                    )

                    st.write(
                        "**Explanation:** "
                        + (
                            question["explanation"]
                            or "No explanation was provided."
                        )
                    )

            if st.button("Generate Another Quiz"):
                clear_quiz()
                st.rerun()
