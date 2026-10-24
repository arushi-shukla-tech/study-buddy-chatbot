import streamlit as st
from groq import Groq
from pypdf import PdfReader
from io import BytesIO

st.set_page_config(
    page_title="Study Buddy AI | Intelligent Learning Assistant",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_client():
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        key = ""

    if not key:
        return None

    return Groq(api_key=key)

def ask_ai(prompt, system="You are a helpful study assistant. Explain topics in simple English with clear headings and examples."):
    client = get_client()

    if client is None:
        return "AI connection is not configured. Add GROQ_API_KEY in Streamlit Secrets."

    try:
        result = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return result.choices[0].message.content
    except Exception as error:
        return f"Unable to get a response. Please check your API key and connection. {error}"

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
    background: #0b1020;
    color: #edf1ff;
}
[data-testid="stSidebar"] {
    background: #10172a;
    border-right: 1px solid #27334d;
}
[data-testid="stSidebar"] .stRadio label {
    padding-top: 5px;
    padding-bottom: 5px;
}
h1, h2, h3 {
    color: #f4f6ff;
    letter-spacing: -0.4px;
}
p, label {
    color: #c4cde0;
}
hr {
    border-color: #293650;
}
div.stButton > button {
    background: #6657d9;
    color: white;
    border: 1px solid #8175ed;
    border-radius: 8px;
    min-height: 42px;
    font-weight: 600;
}
div.stButton > button:hover {
    background: #7868eb;
    color: white;
    border-color: #a69cff;
}
[data-testid="stMetric"] {
    background: #141e33;
    border: 1px solid #2a3855;
    padding: 18px;
    border-radius: 12px;
}
[data-testid="stChatMessage"] {
    background: #141e33;
    border: 1px solid #2a3855;
    border-radius: 10px;
}
.stTextInput input, .stTextArea textarea {
    background: #121a2c;
    color: #ffffff;
    border-color: #35415d;
}
.stSelectbox div[data-baseweb="select"] > div {
    background: #121a2c;
    border-color: #35415d;
}
[data-testid="stFileUploader"] {
    background: #121a2c;
    border: 1px dashed #465574;
    border-radius: 10px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(
        "<div style='padding:10px 0 6px 0;'>"
        "<div style='font-size:12px;letter-spacing:2px;color:#9aa9ca;'>LEARNING PLATFORM</div>"
        "<div style='font-size:25px;font-weight:700;color:#ffffff;margin-top:8px;'>Study Buddy AI</div>"
        "<div style='font-size:12px;color:#aebbd5;margin-top:5px;'>Intelligent Learning Assistant</div>"
        "</div>",
        unsafe_allow_html=True
    )

    st.divider()

    page = st.radio(
        "Workspace",
        [
            "Dashboard",
            "AI Quiz",
            "PDF Notes",
            "Study Chat",
            "Performance",
            "Settings"
        ],
        label_visibility="visible"
    )

    st.divider()
    st.caption("Study Buddy AI")
    st.caption("Personal learning workspace")

st.markdown(
    "<div style='padding:8px 0 22px 0;border-bottom:1px solid #293650;margin-bottom:25px;'>"
    "<div style='font-size:12px;letter-spacing:2px;color:#9aa9ca;'>INTELLIGENT LEARNING ASSISTANT</div>"
    "<h1 style='font-size:36px;margin:8px 0 4px 0;'>Study Buddy AI</h1>"
    "<div style='font-size:15px;color:#aebbd5;'>Learn smarter. Practise better. Build confidence.</div>"
    "</div>",
    unsafe_allow_html=True
)

if page == "Dashboard":
    st.markdown("## Dashboard")
    st.write("Manage your study activities from one place.")

    a, b, c = st.columns(3)

    with a:
        st.markdown("### AI Quiz")
        st.write("Generate topic-based questions for practice.")
        if st.button("Open AI Quiz", key="dash_quiz"):
            st.session_state["selected_page"] = "AI Quiz"
            st.rerun()

    with b:
        st.markdown("### PDF Notes")
        st.write("Convert study material into revision notes.")
        if st.button("Open PDF Notes", key="dash_pdf"):
            st.session_state["selected_page"] = "PDF Notes"
            st.rerun()

    with c:
        st.markdown("### Study Chat")
        st.write("Ask questions and understand concepts.")
        if st.button("Open Study Chat", key="dash_chat"):
            st.session_state["selected_page"] = "Study Chat"
            st.rerun()

    st.markdown("---")
    st.markdown("## Learning Overview")

    total = st.session_state.total_questions
    correct = st.session_state.correct_answers
    accuracy = round(correct / total * 100) if total else 0

    x, y, z = st.columns(3)
    x.metric("Questions Attempted", total)
    y.metric("Correct Answers", correct)
    z.metric("Accuracy", f"{accuracy}%")

    st.markdown("### Quick Start")
    st.info("Select a tool from the sidebar to begin your study session.")

elif page == "AI Quiz":
    st.markdown("## AI Quiz")
    st.write("Create practice questions from your syllabus or any topic.")

    topic = st.text_input("Subject or topic", placeholder="Example: C programming functions")
    difficulty = st.selectbox("Difficulty level", ["Easy", "Medium", "Hard"])
    number = st.number_input("Number of questions", min_value=1, max_value=30, value=5)

    if st.button("Generate Questions"):
        if not topic.strip():
            st.warning("Enter a topic first.")
        else:
            with st.spinner("Preparing questions..."):
                prompt = f"""
Create {number} multiple-choice questions about {topic}.
Difficulty: {difficulty}.
For every question provide four options labelled A, B, C and D.
Show the correct answer and a short explanation after each question.
Use clear, simple English and number the questions.
"""
                st.session_state.quiz_result = ask_ai(prompt)

    if st.session_state.quiz_result:
        st.markdown("---")
        st.markdown("### Generated Questions")
        st.markdown(st.session_state.quiz_result)
        st.download_button(
            "Download Questions",
            st.session_state.quiz_result,
            file_name="study_quiz.txt",
            mime="text/plain"
        )

elif page == "PDF Notes":
    st.markdown("## PDF Notes")
    st.write("Upload a PDF to prepare study notes from its text.")

    uploaded = st.file_uploader("Upload study PDF", type=["pdf"])
    style = st.selectbox(
        "Notes format",
        ["Short revision notes", "Detailed notes", "Important questions", "Simple explanation"]
    )

    if st.button("Create Notes"):
        if uploaded is None:
            st.warning("Upload a PDF first.")
        else:
            try:
                reader = PdfReader(BytesIO(uploaded.getvalue()))
                content = "\n".join(
                    page.extract_text() or "" for page in reader.pages
                )

                if not content.strip():
                    st.error("No readable text was found in this PDF.")
                else:
                    with st.spinner("Preparing notes..."):
                        prompt = f"""
Create {style.lower()} using the study material below.
Use clear headings, bullet points and simple English.
Do not add unsupported facts.
Study material:
{content[:24000]}
"""
                        st.session_state.notes_result = ask_ai(prompt)

            except Exception as error:
                st.error(f"Unable to read the PDF: {error}")

    if st.session_state.notes_result:
        st.markdown("---")
        st.markdown("### Your Notes")
        st.markdown(st.session_state.notes_result)
        st.download_button(
            "Download Notes",
            st.session_state.notes_result,
            file_name="study_notes.txt",
            mime="text/plain"
        )

elif page == "Study Chat":
    st.markdown("## Study Chat")
    st.write("Ask academic questions and get step-by-step explanations.")

    for item in st.session_state.chat_history:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])

    prompt = st.chat_input("Enter your question")

    if prompt:
        st.session_state.chat_history.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Preparing an explanation..."):
                answer = ask_ai(
                    prompt,
                    "You are Study Buddy AI, a patient academic tutor. Explain in simple English, step by step, with examples when helpful."
                )
                st.markdown(answer)

        st.session_state.chat_history.append(
            {"role": "assistant", "content": answer}
        )

    if st.button("Clear Conversation"):
        st.session_state.chat_history = []
        st.rerun()

elif page == "Performance":
    st.markdown("## Performance")
    st.write("Review the practice statistics recorded during this session.")

    total = st.session_state.total_questions
    correct = st.session_state.correct_answers
    accuracy = round(correct / total * 100) if total else 0

    a, b, c = st.columns(3)
    a.metric("Questions Attempted", total)
    b.metric("Correct Answers", correct)
    c.metric("Accuracy", f"{accuracy}%")

    if total:
        st.progress(accuracy / 100)
    else:
        st.info("Practice statistics will appear here when scored quiz attempts are added.")

    st.caption("These statistics are session-based and may reset when the app restarts.")

elif page == "Settings":
    st.markdown("## Settings")
    st.write("Manage the AI connection for your learning workspace.")

    client = get_client()

    if client is None:
        st.warning("AI connection is not configured.")
        st.write("Open Streamlit Cloud, go to your app settings, and add this secret:")
        st.code('GROQ_API_KEY = "your_api_key"')
    else:
        st.success("An API key is configured.")

    st.markdown("---")
    st.markdown("### Project Information")
    st.write("Project Name: Study Buddy AI")
    st.write("Project Type: Intelligent Learning Assistant")
    st.write("Technology: Python, Streamlit and Groq API")
