import streamlit as st
import json
import re
from groq import Groq
from pypdf import PdfReader

st.set_page_config(page_title="Study Buddy AI", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #101426, #201633);
    color: white;
}
h1, h2, h3 {
    color: #d9c9ff;
}
div.stButton > button {
    border-radius: 12px;
    border: 1px solid #8b6cff;
}
</style>
""", unsafe_allow_html=True)

st.title("🎓 Study Buddy AI")
st.subheader("Learn • Practise • Improve")
st.write("Understand your notes, practise with AI, and track your progress.")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    client = None

if "notes" not in st.session_state:
    st.session_state.notes = ""

if "chat" not in st.session_state:
    st.session_state.chat = []

if "quiz" not in st.session_state:
    st.session_state.quiz = []

if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "answered" not in st.session_state:
    st.session_state.answered = []

if "total_answered" not in st.session_state:
    st.session_state.total_answered = 0


def ask_ai(prompt):
    if client is None:
        return "GROQ_API_KEY missing. Check Streamlit Secrets."

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b", 
            messages=[
                {
                    "role": "system",
                    "content": "You are Study Buddy AI. Explain topics in simple English or Hinglish. Help students learn clearly."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=2500
        )
        return response.choices[0].message.content
    except Exception as e:
        return "AI error: " + str(e)


def make_quiz(notes, count):
    prompt = f"""
Create exactly {count} multiple-choice questions from these notes.
Return ONLY a valid JSON array without Markdown.

Each question must contain:
"question": question text
"options": list of exactly four choices
"answer": exact correct option text
"explanation": short explanation

NOTES:
{notes[:18000]}
"""
    result = ask_ai(prompt)

    try:
        match = re.search(r"\[.*\]", result, re.DOTALL)
        if not match:
            raise ValueError("Invalid response")

        data = json.loads(match.group(0))
        valid = []

        for item in data:
            if (
                isinstance(item, dict)
                and isinstance(item.get("question"), str)
                and isinstance(item.get("options"), list)
                and len(item["options"]) == 4
                and isinstance(item.get("answer"), str)
            ):
                valid.append(item)

        return valid
    except Exception:
        st.error("Quiz generation failed. Please try again.")
        with st.expander("Error details"):
            st.write(result[:1500])
        return []


st.sidebar.title("📚 Study Menu")
page = st.sidebar.radio(
    "Choose a section",
    ["Dashboard", "My Notes", "AI Chat", "Quiz Maker"]
)

st.sidebar.caption("Study Buddy AI")

if page == "Dashboard":
    st.header("📊 Your Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Questions Answered", st.session_state.total_answered)
    col2.metric("Correct Answers", st.session_state.score)

    accuracy = 0
    if st.session_state.total_answered:
        accuracy = round(
            st.session_state.score / st.session_state.total_answered * 100
        )

    col3.metric("Accuracy", f"{accuracy}%")

    st.divider()
    st.subheader("🚀 Quick Start")
    st.write("📖 Add notes in My Notes.")
    st.write("💬 Ask questions in AI Chat.")
    st.write("📝 Practise in Quiz Maker.")

    if st.session_state.notes:
        st.success("Your notes are ready.")
    else:
        st.info("Start by adding your notes.")

elif page == "My Notes":
    st.header("📖 My Notes")

    uploaded_file = st.file_uploader("Upload PDF notes", type=["pdf"])

    if uploaded_file is not None:
        if st.button("Read PDF"):
            try:
                reader = PdfReader(uploaded_file)
                text = "\n".join(
                    pdf_page.extract_text() or ""
                    for pdf_page in reader.pages
                )

                if text.strip():
                    st.session_state.notes = text
                    st.success("PDF notes loaded.")
                else:
                    st.warning("No text found in this PDF.")
            except Exception as e:
                st.error("PDF error: " + str(e))

    pasted_notes = st.text_area(
        "Paste your notes",
        value=st.session_state.notes,
        height=250
    )

    if st.button("Save Notes"):
        st.session_state.notes = pasted_notes
        st.success("Notes saved.")

    if st.session_state.notes:
        st.caption(f"Characters saved: {len(st.session_state.notes)}")

        if st.button("Summarise My Notes"):
            with st.spinner("Preparing summary..."):
                summary = ask_ai(
                    "Summarise these notes with headings and simple language:\n\n"
                    + st.session_state.notes[:18000]
                )
            st.markdown(summary)

elif page == "AI Chat":
    st.header("💬 Chat with Your Notes")

    for message in st.session_state.chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask a question about your notes...")

    if question:
        st.session_state.chat.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        prompt = (
            "Answer clearly and simply.\n\nNOTES:\n"
            + (st.session_state.notes[:12000] or "No notes provided.")
            + "\n\nQUESTION:\n"
            + question
        )

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_ai(prompt)
            st.markdown(answer)

        st.session_state.chat.append(
            {"role": "assistant", "content": answer}
        )

    if st.button("🧹 Clear Chat"):
        st.session_state.chat = []
        st.rerun()

elif page == "Quiz Maker":
    st.header("📝 AI Quiz Maker")

    if not st.session_state.notes:
        st.warning("Add notes in My Notes before generating a quiz.")

    count = st.select_slider(
        "Number of questions",
        options=[5, 10, 15, 20, 30, 50, 75, 100],
        value=5
    )

    if st.button(
        "✨ Generate Quiz",
        disabled=not bool(st.session_state.notes)
    ):
        with st.spinner("Generating quiz..."):
            questions = make_quiz(st.session_state.notes, count)

        if questions:
            st.session_state.quiz = questions
            st.session_state.quiz_index = 0
            st.session_state.answered = []
            st.rerun()

    if st.session_state.quiz:
        questions = st.session_state.quiz
        index = st.session_state.quiz_index

        if index < len(questions):
            item = questions[index]
            st.progress((index + 1) / len(questions))
            st.subheader(f"Question {index + 1} of {len(questions)}")
            st.write(item["question"])

            already_answered = index in st.session_state.answered

            choice = st.radio(
                "Choose your answer",
                item["options"],
                key=f"quiz_choice_{index}",
                disabled=already_answered
            )

            if not already_answered:
                if st.button("Check Answer"):
                    st.session_state.answered.append(index)
                    st.session_state.total_answered += 1

                    correct = choice == item["answer"]
                    st.session_state[f"result_{index}"] = correct

                    if correct:
                        st.session_state.score += 1

                    st.rerun()

            if already_answered:
                if st.session_state.get(f"result_{index}", False):
                    st.success("Correct!")
                else:
                    st.error("Incorrect.")

                st.write("Correct answer:", item["answer"])
                st.write("Explanation:", item.get("explanation", ""))

                if index < len(questions) - 1:
                    if st.button("Next Question ➜"):
                        st.session_state.quiz_index += 1
                        st.rerun()
                else:
                    st.success("Quiz completed!")
                    correct_count = sum(
                        1 for i in st.session_state.answered
                        if st.session_state.get(f"result_{i}", False)
                    )
                    st.write(f"Score: {correct_count}/{len(questions)}")

        if st.button("🔄 Generate More Questions"):
            st.session_state.quiz = []
            st.session_state.quiz_index = 0
            st.session_state.answered = []
            st.rerun()

st.divider()
st.caption("🎓 Study Buddy AI | Learn • Practise • Improve")
