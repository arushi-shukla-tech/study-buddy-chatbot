
import streamlit as st
import PyPDF2
import re
import random
from collections import Counter

st.set_page_config(
    page_title="Study Buddy Chatbot",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Study Buddy Chatbot")
st.caption("Upload your notes, learn concepts and test yourself.")

st.sidebar.title("Study Menu")
page = st.sidebar.radio(
    "Choose a feature",
    ["My Notes", "Ask Questions", "Take a Quiz"]
)

if "notes" not in st.session_state:
    st.session_state.notes = ""

if "questions" not in st.session_state:
    st.session_state.questions = []

if "score" not in st.session_state:
    st.session_state.score = None


def read_pdf(file):
    reader = PyPDF2.PdfReader(file)
    pages = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)

    return "\n".join(pages)


def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text)
    return [
        s.strip() for s in sentences
        if len(s.split()) >= 6
    ]


def find_relevant_notes(text, question):
    sentences = split_sentences(text)
    words = set(re.findall(r'\b[a-zA-Z]{3,}\b',
                           question.lower()))

    stop_words = {
        "what", "when", "where", "which", "who",
        "does", "this", "that", "with", "from",
        "have", "about", "explain", "tell", "give",
        "notes", "your", "the", "and", "for"
    }

    words = words - stop_words
    ranked = []

    for sentence in sentences:
        sentence_words = set(
            re.findall(r'\b[a-zA-Z]{3,}\b',
                       sentence.lower())
        )
        score = len(words & sentence_words)

        if score > 0:
            ranked.append((score, sentence))

    ranked.sort(key=lambda x: x[0], reverse=True)

    return [s for score, s in ranked[:3]]


def make_quiz(text, count=5):
    sentences = split_sentences(text)
    quiz = []

    random.shuffle(sentences)

    for sentence in sentences:
        words = re.findall(r'\b[A-Za-z]{4,}\b', sentence)

        if len(words) < 7:
            continue

        answer = max(words, key=len)
        pattern = re.compile(re.escape(answer),
                             re.IGNORECASE)
        question = pattern.sub("________", sentence, count=1)

        other_words = list(set(
            re.findall(r'\b[A-Za-z]{4,}\b', text)
        ))
        other_words = [
            w for w in other_words
            if w.lower() != answer.lower()
        ]

        options = random.sample(
            other_words, min(3, len(other_words))
        )

        options.append(answer)
        random.shuffle(options)

        if len(options) != 4:
            continue

        quiz.append({
            "question": question,
            "options": options,
            "answer": answer,
            "explanation": sentence
        })

        if len(quiz) >= count:
            break

    return quiz


if page == "My Notes":
    st.header("Upload Your Study Notes")

    uploaded_file = st.file_uploader(
        "Upload a PDF or TXT file",
        type=["pdf", "txt"]
    )

    if uploaded_file:
        try:
            if uploaded_file.name.lower().endswith(".pdf"):
                text = read_pdf(uploaded_file)
            else:
                text = uploaded_file.getvalue().decode(
                    "utf-8", errors="ignore"
                )

            if text.strip():
                st.session_state.notes = text
                st.success("Your notes are ready!")
            else:
                st.warning(
                    "No readable text found in this file."
                )
        except Exception as e:
            st.error("Could not read the file: " + str(e))

    st.text_area(
        "Or paste your notes here",
        key="pasted_notes",
        height=180,
        placeholder="Paste your chapter or class notes..."
    )

    if st.button("Use Pasted Notes"):
        pasted = st.session_state.pasted_notes.strip()

        if pasted:
            st.session_state.notes = pasted
            st.success("Pasted notes saved for this session!")
        else:
            st.warning("Please paste some notes first.")

    if st.session_state.notes:
        st.subheader("Notes Preview")
        st.write(st.session_state.notes[:3000])
        st.caption(
            "The preview shows up to 3000 characters."
        )
        st.info(
            f"Total characters: {len(st.session_state.notes)}"
        )


elif page == "Ask Questions":
    st.header("💬 Ask Your Notes")

    if not st.session_state.notes:
        st.warning("Please upload or paste notes first.")
    else:
        question = st.text_input(
            "Ask a question about your notes",
            placeholder="What is the main concept?"
        )

        if st.button("Find Answer"):
            if question.strip():
                results = find_relevant_notes(
                    st.session_state.notes, question
                )

                if results:
                    st.subheader("Relevant Notes")
                    for item in results:
                        st.write("• " + item)
                    st.caption(
                        "These are matching sentences from "
                        "your notes, not independently verified "
                        "AI-generated answers."
                    )
                else:
                    st.info(
                        "No matching information found. "
                        "Try different keywords from your notes."
                    )


elif page == "Take a Quiz":
    st.header("📝 Quiz From Your Notes")

    if not st.session_state.notes:
        st.warning("Upload or paste notes before starting.")
    else:
        count = st.select_slider(
            "Number of questions",
            options=[3, 5, 10],
            value=5
        )

        if st.button("Generate Quiz"):
            st.session_state.questions = make_quiz(
                st.session_state.notes, count
            )
            st.session_state.score = None

        quiz = st.session_state.questions

        if quiz:
            if len(quiz) < count:
                st.info(
                    f"Generated {len(quiz)} questions. "
                    "Add more complete sentences to your notes "
                    "for a longer quiz."
                )

            with st.form("quiz_form"):
                answers = []

                for i, item in enumerate(quiz):
                    st.write(
                        f"**Q{i + 1}. {item['question']}**"
                    )

                    selected = st.radio(
                        "Choose an answer",
                        item["options"],
                        key=f"answer_{i}",
                        index=None
                    )
                    answers.append(selected)

                submitted = st.form_submit_button(
                    "Submit Quiz"
                )

            if submitted:
                score = 0

                for i, item in enumerate(quiz):
                    if answers[i] and (
                        answers[i].lower()
                        == item["answer"].lower()
                    ):
                        score += 1

                st.session_state.score = score

            if st.session_state.score is not None:
                score = st.session_state.score

                st.success(
                    f"Your Score: {score}/{len(quiz)}"
                )

                for i, item in enumerate(quiz):
                    st.write(f"Question {i + 1}")
                    st.write(
                        "Correct answer: " + item["answer"]
                    )
                    st.caption(
                        "From notes: " + item["explanation"]
                    )
