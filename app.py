import io
import streamlit as st
from groq import Groq
from pypdf import PdfReader


st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #080F1F;
    color: #E8EEFA;
}

[data-testid="stSidebar"] {
    background: #0D172B;
    border-right: 1px solid #23324B;
}

[data-testid="stSidebar"] * {
    color: #E8EEFA;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

.hero {
    background: linear-gradient(120deg, #142A4B, #163B68, #245A91);
    padding: 34px;
    border-radius: 22px;
    border: 1px solid #345B85;
    margin-bottom: 26px;
}

.hero h1 {
    color: white;
    font-size: 36px;
    font-weight: 800;
    margin-bottom: 10px;
}

.hero p {
    color: #D0E0F6;
    font-size: 15px;
    line-height: 1.8;
}

.eyebrow {
    color: #73B7FF;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 8px;
}

.metric-card {
    background: #111E33;
    border: 1px solid #263853;
    padding: 21px;
    border-radius: 16px;
    min-height: 125px;
}

.metric-label {
    color: #A6B6CD;
    font-size: 13px;
    margin-bottom: 12px;
}

.metric-value {
    color: #F4F7FF;
    font-size: 28px;
    font-weight: 800;
}

.feature-card {
    background: #111E33;
    border: 1px solid #263853;
    padding: 22px;
    border-radius: 17px;
    min-height: 165px;
}

.feature-card h3 {
    color: #F4F7FF;
    font-size: 18px;
}

.feature-card p {
    color: #AFC0D7;
    line-height: 1.7;
    font-size: 13px;
}

div.stButton > button {
    background: #2675D8;
    color: white;
    border: 1px solid #3988E8;
    border-radius: 10px;
    padding: 10px 16px;
    font-weight: 700;
    min-height: 42px;
}

div.stButton > button:hover {
    background: #3988E8;
    color: white;
    border-color: #70B1FF;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"],
.stNumberInput input {
    background: #111E33;
    color: white;
    border-radius: 9px;
}

div[data-testid="stFileUploader"] {
    background: #111E33;
    border: 1px dashed #42638D;
    border-radius: 13px;
    padding: 15px;
}

hr {
    border-color: #263853;
}

h1, h2, h3 {
    color: #F4F7FF;
}

p, label {
    color: #D0DAE9;
}

.small-note {
    color: #91A5C2;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)


def initialize_state():
    defaults = {
        "page_choice": "Dashboard",
        "quiz_result": "",
        "notes_result": "",
        "chat_history": [],
        "quiz_count": 0,
        "notes_count": 0,
        "chat_count": 0,
        "last_pdf_name": "",
        "last_pdf_pages": 0
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_state()


def ask_ai(prompt, system=None):
    api_key = st.secrets.get("GROQ_API_KEY", "")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it in Streamlit Cloud Secrets."
        )

    client = Groq(api_key=api_key)

    messages = []

    if system:
        messages.append({
            "role": "system",
            "content": system
        })

    messages.append({
        "role": "user",
        "content": prompt
    })

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        temperature=0.4,
        max_completion_tokens=6000
    )

    return response.choices[0].message.content or "No response was generated."


def metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def feature_card(icon, title, description):
    st.markdown(
        f"""
        <div class="feature-card">
            <h3>{icon} {title}</h3>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def split_text(text, max_chars=6000):
    parts = []
    start = 0

    while start < len(text):
        end = min(start + max_chars, len(text))

        if end < len(text):
            split_at = text.rfind("\n", start, end)

            if split_at > start + max_chars // 2:
                end = split_at

        part = text[start:end].strip()

        if part:
            parts.append(part)

        start = end

    return parts


def build_pdf_sections(pdf_bytes):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    total_pages = len(reader.pages)
    sections = []
    empty_pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""

        if not page_text.strip():
            empty_pages.append(page_number)
            continue

        page_parts = split_text(page_text)

        for part_number, part in enumerate(page_parts, start=1):
            sections.append({
                "page": page_number,
                "part": part_number,
                "total_parts": len(page_parts),
                "text": part
            })

    return total_pages, sections, empty_pages


def create_pdf_notes(uploaded, style, language):
    total_pages, sections, empty_pages = build_pdf_sections(
        uploaded.getvalue()
    )

    if total_pages == 0:
        st.error("The uploaded PDF has no pages.")
        return

    if not sections:
        st.error(
            "Selectable text was not found in this PDF. "
            "It may be a scanned PDF. Use an OCR-enabled or text-selectable PDF."
        )
        return

    st.session_state.notes_result = ""
    st.session_state.last_pdf_name = uploaded.name
    st.session_state.last_pdf_pages = total_pages

    progress = st.progress(0)
    status = st.empty()
    completed_notes = []

    if empty_pages:
        completed_notes.append(
            "## Pages without selectable text\n\n"
            + ", ".join(str(number) for number in empty_pages)
            + "\n\nThese pages may contain scanned images, handwritten "
            "content, or pages from which text could not be extracted."
        )

    for index, section in enumerate(sections):
        page_number = section["page"]
        part_number = section["part"]
        total_parts = section["total_parts"]

        status.info(
            f"Creating notes: section {index + 1} of {len(sections)} "
            f"(PDF page {page_number})"
        )

        prompt = f"""
Create clear study notes from the exact PDF text provided below.

Notes style: {style}
Language: {language}
PDF page: {page_number}
Text section: {part_number} of {total_parts}

Instructions:
1. Cover every important topic present in this section.
2. Keep the information in the original order.
3. Include definitions, formulas, examples, facts and technical terms.
4. Explain difficult concepts in student-friendly language.
5. Use headings and bullet points where useful.
6. Do not invent facts or formulas.
7. Do not write a general summary that ignores the supplied details.
8. If an equation or sentence is incomplete at a section boundary,
   preserve the available information without guessing.
9. These notes will be combined with notes from other sections.

PDF TEXT:
{section["text"]}
"""

        try:
            notes = ask_ai(
                prompt,
                system=(
                    "You are a careful study-notes assistant. "
                    "Use the supplied source text faithfully and cover "
                    "its important details. Never pretend to have read "
                    "pages that were not supplied."
                )
            )

            completed_notes.append(
                f"## PDF Page {page_number} "
                f"(Section {part_number}/{total_parts})\n\n{notes}"
            )

            st.session_state.notes_result = "\n\n---\n\n".join(
                completed_notes
            )

        except Exception as error:
            completed_notes.append(
                f"## PDF Page {page_number} — Processing issue\n\n"
                f"Notes could not be generated for this section. "
                f"Please retry this PDF. Error: {error}\n\n"
                f"Source text from this section:\n\n{section['text']}"
            )

            st.session_state.notes_result = "\n\n---\n\n".join(
                completed_notes
            )

            status.warning(
                f"One section had an error on PDF page {page_number}. "
                "The extracted text has been preserved in the output."
            )

        progress.progress((index + 1) / len(sections))

    st.session_state.notes_count += 1

    status.success(
        f"Finished processing {total_pages} PDF pages. "
        f"Created {len(sections)} text sections."
    )


with st.sidebar:
    st.markdown("## 📘 Study Buddy AI")
    st.caption("Your personal learning workspace")
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
        index=pages.index(st.session_state.page_choice)
        if st.session_state.page_choice in pages else 0
    )

    st.session_state.page_choice = selected_page

    st.divider()

    st.markdown("### Your learning space")
    st.caption("Learn concepts. Practise questions. Revise smarter.")


page = st.session_state.page_choice


if page == "Dashboard":

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">YOUR PERSONAL LEARNING SPACE</div>
            <h1>Study smarter with Study Buddy AI.</h1>
            <p>
                Turn study material into useful notes, practise with AI
                quizzes and understand difficult topics through conversation.
                Everything you need to organise your learning in one place.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("Your workspace")

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("Quizzes created", st.session_state.quiz_count)

    with c2:
        metric_card("PDF note sessions", st.session_state.notes_count)

    with c3:
        metric_card("Chat questions", st.session_state.chat_count)

    st.write("")
    st.subheader("Explore your tools")

    c1, c2 = st.columns(2)

    with c1:
        feature_card(
            "🧠",
            "AI Quiz",
            "Generate practice questions from your subject and test "
            "your understanding."
        )

        st.write("")
        if st.button("Open AI Quiz →", key="dashboard_quiz",
                     use_container_width=True):
            st.session_state.page_choice = "AI Quiz"
            st.rerun()

    with c2:
        feature_card(
            "📄",
            "PDF Notes Maker",
            "Turn text-based PDF study material into organised notes "
            "section by section."
        )

        st.write("")
        if st.button("Create PDF Notes →", key="dashboard_notes",
                     use_container_width=True):
            st.session_state.page_choice = "PDF Notes"
            st.rerun()

    c3, c4 = st.columns(2)

    with c3:
        feature_card(
            "💬",
            "Study Chat",
            "Ask questions and get explanations in language that is "
            "easy to understand."
        )

        st.write("")
        if st.button("Start Study Chat →", key="dashboard_chat",
                     use_container_width=True):
            st.session_state.page_choice = "Study Chat"
            st.rerun()

    with c4:
        feature_card(
            "📊",
            "Performance",
            "Review your quiz, notes and chat activity for this session."
        )

        st.write("")
        if st.button("View Performance →", key="dashboard_performance",
                     use_container_width=True):
            st.session_state.page_choice = "Performance"
            st.rerun()

    st.divider()
    st.caption("Study Buddy AI · Intelligent Learning Assistant")


elif page == "AI Quiz":

    st.markdown('<div class="eyebrow">PRACTISE AND IMPROVE</div>',
                unsafe_allow_html=True)
    st.title("🧠 AI Quiz")
    st.write("Create a practice quiz for any subject or topic.")

    with st.form("quiz_form"):
        topic = st.text_input(
            "Subject or topic",
            placeholder="e.g. C programming, matrices, semiconductors"
        )

        level = st.selectbox(
            "Difficulty",
            ["Easy", "Medium", "Hard", "Mixed"]
        )

        question_count = st.number_input(
            "Number of questions",
            min_value=1,
            max_value=50,
            value=10,
            step=1
        )

        question_type = st.selectbox(
            "Question format",
            [
                "Multiple-choice questions with answers",
                "Short-answer questions with answers",
                "Mixed questions with answers"
            ]
        )

        quiz_submit = st.form_submit_button(
            "Generate Quiz →",
            use_container_width=True
        )

    if quiz_submit:
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            prompt = f"""
Create a useful practice quiz.

Topic: {topic}
Difficulty: {level}
Number of questions requested: {question_count}
Format: {question_type}

Requirements:
- Generate the requested number of questions if possible.
- Number every question clearly.
- For multiple-choice questions, provide four options labelled A, B, C, D.
- Include the correct answer and a short explanation for each question.
- Cover different aspects of the topic.
- Avoid duplicate questions.
- Use accurate information and clear language.
- Do not omit answers.
"""

            with st.spinner("Preparing your quiz..."):
                try:
                    result = ask_ai(prompt)
                    st.session_state.quiz_result = result
                    st.session_state.quiz_count += 1
                except Exception as error:
                    st.error(f"Could not create the quiz: {error}")

    if st.session_state.quiz_result:
        st.divider()
        st.subheader("Your practice quiz")
        st.markdown(st.session_state.quiz_result)

        st.download_button(
            "⬇ Download Quiz",
            data=st.session_state.quiz_result,
            file_name="study_buddy_quiz.txt",
            mime="text/plain"
        )


elif page == "PDF Notes":

    st.markdown('<div class="eyebrow">READ LESS, UNDERSTAND MORE</div>',
                unsafe_allow_html=True)
    st.title("📄 PDF Notes Maker")
    st.write(
        "Create notes from all extractable PDF text, processing it "
        "in sections instead of sending the whole file in one request."
    )

    uploaded = st.file_uploader(
        "Upload your study PDF",
        type=["pdf"]
    )

    col1, col2 = st.columns(2)

    with col1:
        style = st.selectbox(
            "Notes format",
            [
                "Detailed notes with headings",
                "Short revision notes",
                "Exam preparation notes",
                "Key points and definitions"
            ]
        )

    with col2:
        language = st.selectbox(
            "Language",
            ["Simple English", "Hindi", "Hinglish"]
        )

    st.caption(
        "Large PDFs may take several AI requests. Scanned image-only pages "
        "may need OCR before their contents can be extracted."
    )

    if st.button(
        "Generate Complete PDF Notes →",
        use_container_width=True
    ):
        if uploaded is None:
            st.warning("Please upload a PDF first.")
        else:
            try:
                create_pdf_notes(uploaded, style, language)
            except Exception as error:
                st.error(
                    "The PDF could not be processed. "
                    f"Please try again. Details: {error}"
                )

    if st.session_state.notes_result:
        st.divider()
        st.subheader("Your PDF Notes")

        st.caption(
            f"Source: {st.session_state.last_pdf_name} · "
            f"{st.session_state.last_pdf_pages} pages"
        )

        st.markdown(st.session_state.notes_result)

        st.download_button(
            "⬇ Download Complete Notes",
            data=st.session_state.notes_result,
            file_name="study_buddy_complete_notes.txt",
            mime="text/plain",
            use_container_width=True
        )


elif page == "Study Chat":

    st.markdown('<div class="eyebrow">LEARN THROUGH CONVERSATION</div>',
                unsafe_allow_html=True)
    st.title("💬 Study Chat")
    st.write("Ask a study question and get a clear explanation.")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_question = st.chat_input(
        "Ask anything about your studies..."
    )

    if user_question:
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })

        with st.chat_message("user"):
            st.markdown(user_question)

        conversation = []

        for message in st.session_state.chat_history[-12:]:
            conversation.append(
                f'{message["role"].upper()}: {message["content"]}'
            )

        prompt = "\n\n".join(conversation)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = ask_ai(
                        prompt,
                        system=(
                            "You are Study Buddy AI, a helpful study tutor. "
                            "Explain concepts clearly using simple language, "
                            "step-by-step examples and exam-friendly points "
                            "when useful. If a question is ambiguous, say so."
                        )
                    )

                    st.markdown(answer)

                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer
                    })

                    st.session_state.chat_count += 1

                except Exception as error:
                    st.error(f"Could not get an answer: {error}")

    if st.session_state.chat_history:
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()


elif page == "Performance":

    st.markdown('<div class="eyebrow">YOUR LEARNING ACTIVITY</div>',
                unsafe_allow_html=True)
    st.title("📊 Performance")
    st.write("Activity recorded during the current app session.")

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("Quizzes", st.session_state.quiz_count)

    with c2:
        metric_card("PDF note sessions", st.session_state.notes_count)

    with c3:
        metric_card("Chat questions", st.session_state.chat_count)

    st.divider()
    st.subheader("Activity overview")

    activity = {
        "Activity": ["Quizzes", "PDF Notes", "Chat Questions"],
        "Count": [
            st.session_state.quiz_count,
            st.session_state.notes_count,
            st.session_state.chat_count
        ]
    }

    st.bar_chart(
        activity,
        x="Activity",
        y="Count"
    )

    st.info(
        "These are activity counts, not exam scores. "
        "They reset when the session state is cleared or the app session ends."
    )


elif page == "Settings":

    st.markdown('<div class="eyebrow">APP INFORMATION</div>',
                unsafe_allow_html=True)
    st.title("⚙️ Settings")

    st.subheader("Study Buddy AI")
    st.write("Intelligent Learning Assistant")

    st.markdown("""
    **Available tools**
    - AI-generated practice quizzes
    - PDF-based study notes
    - AI study chat
    - Session activity overview

    **Technology**
    - Python
    - Streamlit
    - Groq API
    - PyPDF

    **Privacy and API key**
    - Keep your Groq API key in Streamlit Cloud Secrets.
    - Do not publish your API key in your GitHub repository.
    - This version keeps chat and activity data in session state.
    """)

    st.divider()

    if st.button("Clear Session Activity and Results"):
        st.session_state.quiz_result = ""
        st.session_state.notes_result = ""
        st.session_state.chat_history = []
        st.session_state.quiz_count = 0
        st.session_state.notes_count = 0
        st.session_state.chat_count = 0
        st.session_state.last_pdf_name = ""
        st.session_state.last_pdf_pages = 0
        st.success("Session activity and saved results have been cleared.")
        st.rerun()
