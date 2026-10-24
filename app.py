import streamlit as st
from groq import Groq
from pypdf import PdfReader
from io import BytesIO

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_client():
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        api_key = ""

    if not api_key:
        return None

    return Groq(api_key=api_key)

def ask_ai(prompt, system_message="You are a helpful study assistant. Explain in simple English with clear headings and examples."):
    client = get_client()

    if client is None:
        return "Please add GROQ_API_KEY in Streamlit Secrets before using AI features."

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Unable to get a response. Check your API key and connection. Details: {e}"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = ""

if "notes_result" not in st.session_state:
    st.session_state.notes_result = ""

if "total_questions" not in st.session_state:
    st.session_state.total_questions = 0

if "correct_answers" not in st.session_state:
    st.session_state.correct_answers = 0

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b1020 0%, #11172b 55%, #17132e 100%);
    color: #f4f6ff;
}
[data-testid="stSidebar"] {
    background: #101629;
    border-right: 1px solid #29324b;
}
h1, h2, h3 {
    color: #f4f6ff;
}
p, label, span {
    color: #d5dced;
}
div.stButton > button {
    background: linear-gradient(90deg, #7757ff, #4d8dff);
    color: white;
    border: 0;
    border-radius: 10px;
    padding: 0.65rem 1rem;
    font-weight: 600;
    width: 100%;
}
div.stButton > button:hover {
    border: 1px solid #a8a0ff;
    color: white;
}
[data-testid="stMetric"] {
    background: #171f35;
    padding: 18px;
    border: 1px solid #2c3857;
    border-radius: 14px;
}
[data-testid="stChatMessage"] {
    background: #171f35;
    border: 1px solid #2c3857;
    border-radius: 12px;
}
.stTextInput input, .stTextArea textarea {
    background: #151d32;
    color: white;
}
hr {
    border-color: #2c3857;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 📚 Study Buddy AI")
    st.caption("Your personal learning space")
    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "AI Quiz",
            "PDF Notes",
            "AI Study Chat",
            "Performance",
            "Settings"
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.caption("Learn • Practice • Improve")

st.markdown("""
<div style="padding:8px 0 20px 0;">
    <div style="font-size:14px;color:#9da9c8;">STUDY WORKSPACE</div>
    <h1 style="margin:0;">Study Buddy AI</h1>
    <p style="color:#aeb9d3;">A simple place to learn, revise and practise.</p>
</div>
""", unsafe_allow_html=True)

if page == "Dashboard":
    st.markdown("## Welcome to your study space")
    st.write("Choose a tool below to get started with your learning.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📝 AI Quiz")
        st.write("Create practice questions from any topic.")
        if st.button("Open AI Quiz"):
            st.session_state["open_page"] = "AI Quiz"
            st.rerun()

    with col2:
        st.markdown("### 📄 PDF Notes")
        st.write("Upload a PDF and create revision notes.")
        if st.button("Open PDF Notes"):
            st.session_state["open_page"] = "PDF Notes"
            st.rerun()

    with col3:
        st.markdown("### 💬 AI Study Chat")
        st.write("Ask questions and understand difficult concepts.")
        if st.button("Open Study Chat"):
            st.session_state["open_page"] = "AI Study Chat"
            st.rerun()

    st.markdown("---")
    st.markdown("## Your learning overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("Questions attempted", st.session_state.total_questions)
    c2.metric("Correct answers", st.session_state.correct_answers)

    accuracy = 0
    if st.session_state.total_questions > 0:
        accuracy = round(
            st.session_state.correct_answers /
            st.session_state.total_questions * 100
        )

    c3.metric("Accuracy", f"{accuracy}%")

    st.info("Tip: Pick one topic, practise it, and review your mistakes.")

elif page == "AI Quiz":
    st.markdown("## 📝 AI Quiz")
    st.write("Generate practice questions for your chosen subject.")

    topic = st.text_input("Enter subject or topic", placeholder="Example: C programming loops")
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    number = st.number_input("Number of questions", min_value=1, max_value=30, value=5)

    if st.button("Generate Quiz"):
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            with st.spinner("Preparing your quiz..."):
                prompt = f"""
Create {number} multiple-choice practice questions on {topic}.
Difficulty: {difficulty}.

For every question:
1. Give four options labelled A, B, C and D.
2. Clearly show the correct answer.
3. Give a short explanation.
4. Use simple language.

Number every question. Keep the questions relevant to the topic.
"""
                st.session_state.quiz_result = ask_ai(prompt)

    if st.session_state.quiz_result:
        st.markdown("### Your practice quiz")
        st.markdown(st.session_state.quiz_result)
        st.download_button(
            "Download quiz as text",
            data=st.session_state.quiz_result,
            file_name="study_buddy_quiz.txt",
            mime="text/plain"
        )

elif page == "PDF Notes":
    st.markdown("## 📄 PDF Notes")
    st.write("Upload your study PDF to create revision notes.")

    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    note_style = st.selectbox(
        "Choose note style",
        ["Short revision notes", "Detailed notes", "Important questions", "Simple explanation"]
    )

    if st.button("Create Notes"):
        if uploaded_file is None:
            st.warning("Please upload a PDF file first.")
        else:
            try:
                reader = PdfReader(BytesIO(uploaded_file.getvalue()))
                extracted_text = ""

                for pdf_page in reader.pages:
                    extracted_text += (pdf_page.extract_text() or "") + "\n"

                if not extracted_text.strip():
                    st.error("No readable text found. The PDF may contain scanned pages.")
                else:
                    with st.spinner("Creating your notes..."):
                        prompt = f"""
Make {note_style.lower()} from the following study material.
Use simple English, headings and bullet points.
Keep the information faithful to the provided material.
If it is suitable, include definitions and examples.

Study material:
{extracted_text[:24000]}
"""
                        st.session_state.notes_result = ask_ai(prompt)

            except Exception as e:
                st.error(f"Could not read this PDF: {e}")

    if st.session_state.notes_result:
        st.markdown("### Your notes")
        st.markdown(st.session_state.notes_result)
        st.download_button(
            "Download notes",
            data=st.session_state.notes_result,
            file_name="study_buddy_notes.txt",
            mime="text/plain"
        )

elif page == "AI Study Chat":
    st.markdown("## 💬 AI Study Chat")
    st.write("Ask about a topic, formula, program or concept.")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Type your study question...")

    if user_prompt:
        st.session_state.chat_history.append(
            {"role": "user", "content": user_prompt}
        )

        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Preparing an explanation..."):
                answer = ask_ai(
                    user_prompt,
                    "You are Study Buddy AI. Help a college student learn. Explain step by step in simple language. Use examples when useful."
                )
                st.markdown(answer)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer}
        )

    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

elif page == "Performance":
    st.markdown("## 📊 Performance")
    st.write("Your practice statistics for this session.")

    total = st.session_state.total_questions
    correct = st.session_state.correct_answers
    incorrect = total - correct if total >= correct else 0
    accuracy = round(correct / total * 100) if total else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Attempted", total)
    c2.metric("Correct", correct)
    c3.metric("Accuracy", f"{accuracy}%")

    if total:
        st.progress(accuracy / 100)
        st.write(f"Incorrect answers: {incorrect}")
    else:
        st.info("Your statistics will appear here when quiz scoring is added.")

    st.caption("These statistics are session-based and may reset when the app restarts.")

elif page == "Settings":
    st.markdown("## ⚙️ Settings")
    st.write("Check your AI connection and app setup.")

    client = get_client()

    if client is None:
        st.warning("AI is not connected yet.")
        st.write("Add your API key in Streamlit Cloud → App → Settings → Secrets.")
        st.code('GROQ_API_KEY = "your_groq_api_key"')
    else:
        st.success("An API key is configured.")

    st.markdown("### About")
    st.write("Study Buddy AI helps with practice quizzes, PDF revision notes and study questions.")
    st.caption("Built with Python and Streamlit.")
