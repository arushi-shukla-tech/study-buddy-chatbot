import base64
from pathlib import Path
from io import BytesIO

import streamlit as st
from groq import Groq
from pypdf import PdfReader

st.set_page_config(
    page_title="Study Buddy AI | Intelligent Learning Assistant",
    page_icon="S",
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

def ask_ai(prompt, system_message=None):
    client = get_client()

    if client is None:
        return "AI connection is not configured. Add GROQ_API_KEY in Streamlit Secrets."

    if system_message is None:
        system_message = (
            "You are Study Buddy AI, a helpful academic tutor. "
            "Explain topics in simple English with clear headings and examples."
        )

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
    except Exception as error:
        return f"Unable to get a response. Check your API key and connection. Details: {error}"

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

if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Dashboard"

st.markdown("""
<style>
.stApp {
    background: #071224;
    color: #f4f6ff;
}
[data-testid="stSidebar"] {
    background: #0c172c;
    border-right: 1px solid #243653;
}
h1, h2, h3 {
    color: #f4f6ff;
}
p, label {
    color: #c7d2e8;
}
hr {
    border-color: #273956;
}
div.stButton > button {
    background: #6557dc;
    color: white;
    border: 1px solid #8276ed;
    border-radius: 9px;
    min-height: 42px;
    font-weight: 600;
}
div.stButton > button:hover {
    background: #7869ec;
    color: white;
}
[data-testid="stMetric"] {
    background: #121f36;
    border: 1px solid #2b3c5c;
    padding: 16px;
    border-radius: 12px;
}
[data-testid="stChatMessage"] {
    background: #121f36;
    border: 1px solid #2b3c5c;
    border-radius: 10px;
}
.stTextInput input, .stTextArea textarea {
    background: #101b30;
    color: white;
}
[data-testid="stFileUploader"] {
    background: #101b30;
    border: 1px dashed #405577;
    border-radius: 10px;
    padding: 12px;
}
.hero-title {
    font-size: 36px;
    font-weight: 750;
    line-height: 1.2;
    color: #ffffff;
}
.hero-subtitle {
    color: #d0dbef;
    font-size: 16px;
    line-height: 1.7;
}
.tool-card {
    background: #111f38;
    border: 1px solid #2b3c5c;
    border-radius: 14px;
    padding: 20px;
    min-height: 175px;
    margin-bottom: 12px;
}
.tool-card h3 {
    font-size: 20px;
    margin-bottom: 10px;
}
.tool-card p {
    font-size: 14px;
    line-height: 1.6;
}
.small-label {
    color: #9badd0;
    font-size: 12px;
    letter-spacing: 2px;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="padding:12px 0 10px 0;">
        <div style="font-size:12px;letter-spacing:2px;color:#91a9d4;">
            LEARNING PLATFORM
        </div>
        <div style="font-size:26px;font-weight:750;color:white;margin-top:8px;">
            Study Buddy AI
        </div>
        <div style="font-size:12px;color:#b5c3df;margin-top:5px;">
            Intelligent Learning Assistant
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    pages = [
        "Dashboard",
        "AI Quiz",
        "PDF Notes",
        "Study Chat",
        "Performance",
        "Settings"
    ]

    selected_index = pages.index(st.session_state.selected_page)

    page = st.radio(
        "Workspace",
        pages,
        index=selected_index
    )

    st.session_state.selected_page = page

    st.divider()

    st.caption("Study Buddy AI")
    st.caption("Your personal learning workspace")

st.markdown("""
<div style="margin-bottom:22px;">
    <div class="small-label">INTELLIGENT LEARNING ASSISTANT</div>
    <h1 style="font-size:34px;margin:8px 0 4px 0;">
        Study Buddy AI
    </h1>
    <div style="color:#aebdd8;">
        Learn smarter. Practise better. Build confidence.
    </div>
</div>
""", unsafe_allow_html=True)

if page == "Dashboard":
    image_path = Path(__file__).parent / "dashboard.png"

    if image_path.exists():
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode()

        st.markdown(
            f"""
            <div style="width:100%;margin-bottom:24px;">
                <img src="data:image/png;base64,{image_data}"
                style="width:100%;max-height:380px;object-fit:cover;
                border-radius:16px;border:1px solid #293d60;">
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.info(
            "Upload dashboard.png to the same GitHub folder as app.py "
            "to display your dashboard banner."
        )

    st.markdown("## Welcome to your study space")
    st.write("Choose a tool to begin your learning session.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="tool-card">
            <h3>AI Quiz</h3>
            <p>Generate topic-based questions and practise important concepts.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open AI Quiz", key="open_quiz"):
            st.session_state.selected_page = "AI Quiz"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="tool-card">
            <h3>PDF Notes</h3>
            <p>Turn your study material into clear revision notes and summaries.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open PDF Notes", key="open_pdf"):
            st.session_state.selected_page = "PDF Notes"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="tool-card">
            <h3>Study Chat</h3>
            <p>Ask academic questions and get step-by-step explanations.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Study Chat", key="open_chat"):
            st.session_state.selected_page = "Study Chat"
            st.rerun()

    st.markdown("---")
    st.markdown("## Learning Overview")

    total = st.session_state.total_questions
    correct = st.session_state.correct_answers
    accuracy = round(correct / total * 100) if total else 0

    a, b, c = st.columns(3)
    a.metric("Questions Attempted", total)
    b.metric("Correct Answers", correct)
    c.metric("Accuracy", f"{accuracy}%")

    st.markdown("""
    <div style="background:#111f38;border:1px solid #293d60;
    border-radius:12px;padding:18px;margin-top:15px;">
        <div style="font-size:18px;font-weight:650;color:#ffffff;">
            Ready to start?
        </div>
        <div style="color:#b7c6df;margin-top:6px;">
            Select a tool and make progress towards your learning goals.
        </div>
    </div>
    """, unsafe_allow_html=True)

elif page == "AI Quiz":
    st.markdown("## AI Quiz")
    st.write("Create practice questions from your chosen topic.")

    topic = st.text_input(
        "Subject or topic",
        placeholder="Example: C programming functions"
    )
    difficulty = st.selectbox(
        "Difficulty level",
        ["Easy", "Medium", "Hard"]
    )
    number = st.number_input(
        "Number of questions",
        min_value=1,
        max_value=30,
        value=5
    )

    if st.button("Generate Questions"):
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            with st.spinner("Preparing your questions..."):
                prompt = f"""
Create {number} multiple-choice practice questions on {topic}.
Difficulty: {difficulty}.
Give four options labelled A, B, C and D for each question.
Show the correct answer and a short explanation.
Use simple English and number every question.
"""
                st.session_state.quiz_result = ask_ai(prompt)

    if st.session_state.quiz_result:
        st.markdown("---")
        st.markdown("### Generated Questions")
        st.markdown(st.session_state.quiz_result)

        st.download_button(
            "Download Questions",
            st.session_state.quiz_result,
            file_name="study_buddy_quiz.txt",
            mime="text/plain"
        )

elif page == "PDF Notes":
    st.markdown("## PDF Notes")
    st.write("Upload a PDF to create revision notes from its text.")

    uploaded_file = st.file_uploader(
        "Upload study PDF",
        type=["pdf"]
    )

    note_style = st.selectbox(
        "Notes format",
        [
            "Short revision notes",
            "Detailed notes",
            "Important questions",
            "Simple explanation"
        ]
    )

    if st.button("Create Notes"):
        if uploaded_file is None:
            st.warning("Please upload a PDF first.")
        else:
            try:
                reader = PdfReader(BytesIO(uploaded_file.getvalue()))
                extracted_text = "\n".join(
                    pdf_page.extract_text() or ""
                    for pdf_page in reader.pages
                )

                if not extracted_text.strip():
                    st.error("No readable text found in this PDF.")
                else:
                    with st.spinner("Preparing your notes..."):
                        prompt = f"""
Create {note_style.lower()} from the study material below.
Use simple English, headings and bullet points.
Keep the notes faithful to the source material.

Study material:
{extracted_text[:24000]}
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
            file_name="study_buddy_notes.txt",
            mime="text/plain"
        )

elif page == "Study Chat":
    st.markdown("## Study Chat")
    st.write("Ask questions about your subjects, formulas or programming.")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Enter your study question")

    if prompt:
        st.session_state.chat_history.append(
            {"role": "user", "content": prompt}
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Preparing your answer..."):
                answer = ask_ai(
                    prompt,
                    "You are Study Buddy AI, a patient academic tutor. "
                    "Explain step by step in simple English with examples."
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
    st.write("Review the statistics recorded during this session.")

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
        st.info(
            "Your statistics will appear here when scored quiz attempts are added."
        )

    st.caption(
        "Statistics are session-based and may reset when the app restarts."
    )

elif page == "Settings":
    st.markdown("## Settings")
    st.write("Check the AI connection and project information.")

    if get_client() is None:
        st.warning("AI connection is not configured.")
        st.write(
            "Open Streamlit Cloud, go to app settings, and add the secret below."
        )
        st.code('GROQ_API_KEY = "your_api_key"')
    else:
        st.success("An API key is configured.")

    st.markdown("---")
    st.markdown("### Project Information")
    st.write("Project Name: Study Buddy AI")
    st.write("Project Category: Intelligent Learning Assistant")
    st.write("Technology: Python, Streamlit and Groq API")
