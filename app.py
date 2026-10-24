import os
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
  
:root {  
    --bg:#06142a;  
    --panel:#0b2040;  
    --line:#1b4776;  
    --blue:#1976f5;  
    --cyan:#32d8f5;  
    --text:#f2f7ff;  
    --muted:#a9bfdf;  
}  
  
.stApp {  
    background:radial-gradient(ellipse at 35% 0%,#102b51 0%,#06142a 65%);  
    color:var(--text);  
    font-family:'Inter',sans-serif;  
}  
  
[data-testid="stHeader"] {  
    background:#06142a;  
}  
  
[data-testid="stSidebar"] {  
    background:#07172e;  
    border-right:1px solid #183a61;  
}  
  
[data-testid="stSidebar"] > div:first-child {  
    padding-top:1rem;  
}  
  
.block-container {  
    max-width:1550px;  
    padding-top:1.2rem;  
    padding-bottom:2rem;  
}  
  
h1,h2,h3,p,label {  
    color:var(--text);  
}  
  
h1 {  
    font-weight:800;  
    letter-spacing:-1px;  
}  
  
.brand {  
    padding:10px 5px 22px;  
    border-bottom:1px solid #193657;  
    margin-bottom:22px;  
}  
  
.brand-name {  
    font-size:22px;  
    font-weight:800;  
    letter-spacing:-1px;  
}  
  
.brand-name span {  
    color:#38d9f6;  
}  
  
.brand-sub {  
    font-size:10px;  
    color:#91b7e8;  
    margin-left:43px;  
    letter-spacing:1px;  
}  
  
.side-note {  
    background:#0c2443;  
    border:1px solid #1c426b;  
    padding:16px;  
    border-radius:15px;  
    margin-top:25px;  
}  
  
.hero {  
    position:relative;  
    overflow:hidden;  
    min-height:260px;  
    border:1px solid #1761a5;  
    border-radius:18px;  
    padding:27px;  
    margin-bottom:18px;  
    background:  
        radial-gradient(ellipse at 83% 45%,rgba(42,143,247,.35),transparent 38%),  
        linear-gradient(115deg,#0b2b55 0%,#0a2042 60%,#123b69 100%);  
}  
  
.hero:after {  
    content:"📚  🪴  💻";  
    position:absolute;  
    right:4%;  
    top:42%;  
    font-size:clamp(35px,4vw,65px);  
    opacity:.95;  
    filter:drop-shadow(0 8px 15px #020b18);  
}  
  
.hero:before {  
    content:"✦  ✧  ✦";  
    position:absolute;  
    right:8%;  
    top:15%;  
    font-size:26px;  
    color:#4ad8f8;  
    letter-spacing:18px;  
}  
  
.hero-content {  
    position:relative;  
    z-index:1;  
    max-width:65%;  
}  
  
.eyebrow {  
    color:#69dffb;  
    text-transform:uppercase;  
    letter-spacing:2px;  
    font-size:10px;  
    font-weight:700;  
}  
  
.hero h1 {  
    font-size:clamp(28px,3vw,42px);  
    line-height:1.12;  
    margin:12px 0;  
}  
  
.hero h1 span {  
    color:#35d7f4;  
}  
  
.hero p {  
    color:#ccddf5;  
    font-size:13px;  
    line-height:1.8;  
}  
  
.hero-tag {  
    display:inline-block;  
    background:#102e55;  
    border:1px solid #315d8c;  
    border-radius:9px;  
    padding:8px 11px;  
    font-size:11px;  
    color:#dcecff;  
}  
  
.section-head {  
    display:flex;  
    justify-content:space-between;  
    align-items:center;  
    margin:20px 0 12px;  
}  
  
.section-head h3 {  
    font-size:17px;  
    margin:0;  
}  
  
.section-head span {  
    font-size:10px;  
    color:#9bb8dc;  
}  
  
.metric {  
    background:linear-gradient(145deg,#102a4c,#081a33);  
    border:1px solid #1a4776;  
    border-radius:14px;  
    padding:15px;  
    min-height:112px;  
}  
  
.metric-icon {  
    width:38px;  
    height:38px;  
    display:flex;  
    align-items:center;  
    justify-content:center;  
    border-radius:12px;  
    font-size:20px;  
    background:#173c76;  
}  
  
.metric-label {  
    font-size:11px;  
    color:#b6c9e3;  
    margin-top:10px;  
}  
  
.metric-value {  
    font-size:25px;  
    font-weight:800;  
    margin-top:2px;  
}  
  
.metric-foot {  
    font-size:10px;  
    color:#42d9c1;  
    margin-top:3px;  
}  
  
.panel {  
    background:linear-gradient(145deg,#0c2342,#081a32);  
    border:1px solid #194674;  
    border-radius:15px;  
    padding:17px;  
    margin-bottom:12px;  
}  
  
.panel h3 {  
    font-size:15px;  
    margin:0 0 12px;  
}  
  
.panel p {  
    color:#b1c6e2;  
    font-size:12px;  
    line-height:1.7;  
}  
  
.feature {  
    border-radius:15px;  
    padding:17px;  
    min-height:180px;  
    border:1px solid #3268d2;  
    background:linear-gradient(135deg,#1746a6,#253cbb);  
}  
  
.feature.green {  
    border-color:#0d9488;  
    background:linear-gradient(135deg,#075b67,#087f83);  
}  
  
.feature.purple {  
    border-color:#7355df;  
    background:linear-gradient(135deg,#4b2ab6,#542fc7);  
}  
  
.feature .icon {  
    font-size:27px;  
    margin-bottom:8px;  
}  
  
.feature h3 {  
    font-size:14px;  
    margin:0 0 7px;  
}  
  
.feature p {  
    font-size:10px;  
    line-height:1.7;  
    min-height:34px;  
    color:#e0eaff;  
}  
  
.action {  
    background:#0c284c;  
    border:1px solid #20568b;  
    border-radius:12px;  
    padding:13px;  
    margin:10px 0;  
}  
  
.action strong {  
    font-size:12px;  
}  
  
.action small {  
    color:#adc6e6;  
    font-size:10px;  
}  
  
.tip {  
    background:#102b4b;  
    border-left:3px solid #35d5f2;  
    padding:13px;  
    border-radius:5px 10px 10px 5px;  
    color:#c9dcf4;  
    font-size:11px;  
    line-height:1.7;  
}  
  
.stButton>button {  
    width:100%;  
    background:linear-gradient(100deg,#1976f5,#168fff);  
    color:white;  
    border:1px solid #338ef9;  
    border-radius:9px;  
    min-height:39px;  
    font-weight:600;  
}  
  
.stButton>button:hover {  
    background:#318fff;  
    color:white;  
    border-color:#6cc5ff;  
}  
  
.stTextInput input,.stTextArea textarea {  
    background:#071a31;  
    color:white;  
    border:1px solid #284a70;  
    border-radius:9px;  
}  
  
[data-testid="stFileUploader"] {  
    background:#0a1c34;  
    border:1px dashed #2b5b8a;  
    border-radius:12px;  
    padding:10px;  
}  
  
.stProgress>div>div {  
    background:#35d5f2;  
}  
  
.app-footer {  
    border-top:1px solid #183657;  
    margin-top:25px;  
    padding-top:13px;  
    color:#89a9d1;  
    font-size:10px;  
    display:flex;  
    justify-content:space-between;  
}  
  
@media(max-width:700px) {  
    .hero {  
        padding:20px;  
        min-height:260px;  
    }  
    .hero-content {  
        max-width:100%;  
    }  
    .hero:after {  
        opacity:.25;  
        right:3%;  
        top:5%;  
        font-size:45px;  
    }  
}  
</style>  """, unsafe_allow_html=True)

def get_client():
key = st.secrets.get(
"GROQ_API_KEY",
os.getenv("GROQ_API_KEY", "")
)
if not key:
return None
return Groq(api_key=key)

def ask_ai(prompt, system=None):
client = get_client()

if client is None:  
    raise ValueError(  
        "GROQ_API_KEY is missing. Add it in Streamlit Cloud Secrets."  
    )  

if system is None:  
    system = (  
        "You are Study Buddy AI, a helpful study assistant. "  
        "Explain clearly in simple English with headings and examples."  
    )  

response = client.chat.completions.create(  
    model="openai/gpt-oss-20b",  
    messages=[  
        {"role": "system", "content": system},  
        {"role": "user", "content": prompt}  
    ],  
    temperature=0.6  
)  

return response.choices[0].message.content

def init_state():
defaults = {
"page_choice": "Dashboard",
"quiz_result": "",
"notes_result": "",
"chat_history": [],
"quiz_count": 0,
"notes_count": 0,
"chat_count": 0
}

for key, value in defaults.items():  
    if key not in st.session_state:  
        st.session_state[key] = value

def metric_card(icon, label, value, foot, color):
st.markdown(f"""
<div class="metric">
<div style="display:flex;justify-content:space-between;align-items:center;">
<div class="metric-icon" style="background:{color}30">{icon}</div>
<span style="color:{color}">●</span>
</div>
<div class="metric-label">{label}</div>
<div class="metric-value">{value}</div>
<div class="metric-foot">{foot}</div>
</div>
""", unsafe_allow_html=True)

def feature_card(icon, title, description, style=""):
st.markdown(f"""
<div class="feature {style}">
<div class="icon">{icon}</div>
<h3>{title}</h3>
<p>{description}</p>
</div>
""", unsafe_allow_html=True)

init_state()

with st.sidebar:
st.markdown("""
<div class="brand">
<div style="font-size:26px">📘
<span class="brand-name">Study Buddy <span>AI</span></span></div>
<div class="brand-sub">INTELLIGENT LEARNING ASSISTANT</div>
</div>
""", unsafe_allow_html=True)

st.markdown(  
    '<div style="font-size:10px;color:#799ac3;letter-spacing:2px;margin-bottom:8px">MAIN MENU</div>',  
    unsafe_allow_html=True  
)  

st.radio(  
    "Navigation",  
    [  
        "Dashboard",  
        "AI Quiz",  
        "PDF Notes",  
        "Study Chat",  
        "Performance",  
        "Settings"  
    ],  
    key="page_choice",  
    label_visibility="collapsed"  
)  

st.markdown("""  
<div class="side-note">  
    <div style="font-size:26px">🎯</div>  
    <strong>Keep moving forward</strong>  
    <p style="font-size:11px;color:#a9bfdf;line-height:1.7">  
    Small steps every day can lead to big progress.  
    </p>  
</div>  
<div style="margin-top:30px;color:#7899c2;font-size:10px;letter-spacing:2px">  
STUDY · PRACTICE · GROW  
</div>  
""", unsafe_allow_html=True)

page = st.session_state.page_choice

if page == "Dashboard":

st.markdown("""  
<div class="hero">  
    <div class="hero-content">  
        <div class="eyebrow">YOUR PERSONAL LEARNING SPACE</div>  
        <h1>Hello Student 👋<br>Welcome to<br><span>Study Buddy AI</span></h1>  
        <p>Your personal study assistant for better understanding,  
        stronger practice and more confident learning.</p>  
        <div class="hero-tag">✦ Learn at your pace · Grow every day</div>  
    </div>  
</div>  
""", unsafe_allow_html=True)  

st.markdown("""  
<div class="section-head">  
    <h3>Your Learning Overview</h3>  
    <span>YOUR SESSION ACTIVITY</span>  
</div>  
""", unsafe_allow_html=True)  

a, b, c, d = st.columns(4)  

with a:  
    metric_card(  
        "🧠", "Quiz Sets", st.session_state.quiz_count,  
        "AI practice sessions", "#5578ff"  
    )  

with b:  
    metric_card(  
        "📄", "Notes Created", st.session_state.notes_count,  
        "Study material summaries", "#18d6b5"  
    )  

with c:  
    metric_card(  
        "🔥", "Study Streak",  
        f"{1 if st.session_state.quiz_count + st.session_state.notes_count + st.session_state.chat_count else 0} day",  
        "Keep going!", "#ff826e"  
    )  

with d:  
    total_actions = (  
        st.session_state.quiz_count  
        + st.session_state.notes_count  
        + st.session_state.chat_count  
    )  
    metric_card(  
        "◉", "Learning Activity", total_actions,  
        "Total actions this session", "#368bff"  
    )  

st.markdown("""  
<div class="section-head">  
    <h3>Your Weekly Activity</h3>  
    <span>QUESTIONS · NOTES · CHAT</span>  
</div>  
""", unsafe_allow_html=True)  

left, right = st.columns([1.65, 1])  

with left:  
    chart_data = {  
        "Quiz": [2, 4, 3, 5, 4, st.session_state.quiz_count, 0],  
        "Notes": [3, 5, 4, 6, 7, st.session_state.notes_count, 0],  
        "Chat": [1, 2, 3, 3, 4, st.session_state.chat_count, 0]  
    }  

    st.markdown(  
        '<div class="panel"><h3>📊 Activity at a Glance</h3>',  
        unsafe_allow_html=True  
    )  

    st.bar_chart(  
        chart_data,  
        color=["#32c7f4", "#7a7bff", "#b16aff"]  
    )  

    st.markdown('</div>', unsafe_allow_html=True)  

with right:  
    st.markdown("""  
    <div class="panel" style="min-height:245px;background:  
    radial-gradient(ellipse at 85% 90%,#174a77,transparent 50%),#0a1d37">  
        <div style="font-size:11px;color:#55dcf6;letter-spacing:2px">  
        A LITTLE REMINDER  
        </div>  
        <h3 style="font-size:24px;line-height:1.4;margin-top:20px">  
        Better Learning.<br>Brighter Future.</h3>  
        <div style="font-size:38px;margin-top:12px">📚 🪴 ✏️</div>  
        <p>Keep learning, keep practising, keep growing.</p>  
    </div>  
    """, unsafe_allow_html=True)  

st.markdown("""  
<div class="section-head">  
    <h3>Continue Your Journey</h3>  
    <span>CHOOSE YOUR NEXT STEP →</span>  
</div>  
""", unsafe_allow_html=True)  

x, y, z = st.columns(3)  

with x:  
    feature_card(  
        "🧠", "AI Quiz Generator",  
        "Create topic-based questions and test your knowledge."  
    )  

    if st.button("Start Quiz →", key="dash_quiz"):  
        st.session_state.page_choice = "AI Quiz"  
        st.rerun()  

with y:  
    feature_card(  
        "📄", "PDF Notes Maker",  
        "Upload study material and create clear, structured notes.",  
        "green"  
    )  

    if st.button("Create Notes →", key="dash_notes"):  
        st.session_state.page_choice = "PDF Notes"  
        st.rerun()  

with z:  
    feature_card(  
        "💬", "Study Chat",  
        "Ask questions and get step-by-step explanations.",  
        "purple"  
    )  

    if st.button("Open Chat →", key="dash_chat"):  
        st.session_state.page_choice = "Study Chat"  
        st.rerun()  

st.markdown("""  
<div class="section-head">  
    <h3>Quick Actions</h3>  
    <span>YOUR STUDY TOOLS</span>  
</div>  
""", unsafe_allow_html=True)  

q1, q2, q3 = st.columns(3)  

with q1:  
    st.markdown("""  
    <div class="action">🧠 <strong>Create AI Quiz</strong><br>  
    <small>Practise with topic-based questions</small></div>  
    """, unsafe_allow_html=True)  

    if st.button("Open Quiz", key="quick_quiz"):  
        st.session_state.page_choice = "AI Quiz"  
        st.rerun()  

with q2:  
    st.markdown("""  
    <div class="action">📄 <strong>Generate Notes</strong><br>  
    <small>Turn your PDF into revision notes</small></div>  
    """, unsafe_allow_html=True)  

    if st.button("Open PDF Notes", key="quick_notes"):  
        st.session_state.page_choice = "PDF Notes"  
        st.rerun()  

with q3:  
    st.markdown("""  
    <div class="action">💬 <strong>Ask Study Buddy</strong><br>  
    <small>Get help understanding a concept</small></div>  
    """, unsafe_allow_html=True)  

    if st.button("Open Study Chat", key="quick_chat"):  
        st.session_state.page_choice = "Study Chat"  
        st.rerun()  

st.markdown("""  
<div class="tip">  
Study tip: Choose one topic, review its key points and then test  
yourself with a few questions.  
</div>  
""", unsafe_allow_html=True)

elif page == "AI Quiz":

st.markdown(  
    '<div class="eyebrow">PRACTISE AND IMPROVE</div>',  
    unsafe_allow_html=True  
)  
st.title("🧠 AI Quiz Generator")  
st.write("Build a practice quiz for the topic you are studying.")  

with st.form("quiz_form"):  
    topic = st.text_input(  
        "Topic or subject",  
        placeholder="e.g. C programming, matrices, chemistry"  
    )  

    col1, col2 = st.columns(2)  

    with col1:  
        number = st.selectbox(  
            "Number of questions",  
            [5, 10, 15, 20, 25, 30],  
            index=1  
        )  

    with col2:  
        difficulty = st.selectbox(  
            "Difficulty",  
            ["Easy", "Medium", "Hard", "Mixed"]  
        )  

    kind = st.selectbox(  
        "Question type",  
        [  
            "Multiple choice with answers",  
            "Short-answer questions with answers",  
            "Mixed questions with answers"  
        ]  
    )  

    submitted = st.form_submit_button("Generate My Quiz →")  

if submitted:  
    if not topic.strip():  
        st.warning("Enter a topic first.")  
    else:  
        try:  
            with st.spinner("Creating your quiz..."):  
                prompt = f"""

Create {number} questions about {topic}.
Difficulty: {difficulty}.
Format: {kind}.
Number every question.
For MCQs, include four options A-D.
Give the correct answer and a short explanation for each question.
Use clear student-friendly language and do not skip questions.
"""
st.session_state.quiz_result = ask_ai(prompt)
st.session_state.quiz_count += 1

except Exception as e:  
            st.error(str(e))  

if st.session_state.quiz_result:  
    st.markdown("---")  
    st.subheader("Your Quiz")  
    st.markdown(st.session_state.quiz_result)  

    st.download_button(  
        "⬇ Download Quiz",  
        st.session_state.quiz_result,  
        file_name="study_buddy_quiz.txt",  
        mime="text/plain"  
    )

elif page == "PDF Notes":

st.markdown(  
    '<div class="eyebrow">READ LESS, UNDERSTAND MORE</div>',  
    unsafe_allow_html=True  
)  
st.title("📄 PDF Notes Maker")  
st.write("Turn your PDF study material into useful revision notes.")  

uploaded = st.file_uploader("Upload your PDF", type=["pdf"])  

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

if st.button("Generate Study Notes →"):  

    if uploaded is None:  
        st.warning("Upload a PDF first.")  

    else:  
        try:  
            with st.spinner("Reading your PDF and preparing notes..."):  
                reader = PdfReader(io.BytesIO(uploaded.getvalue()))  

                content = "\n".join(  
                    page.extract_text() or ""  
                    for page in reader.pages  
                )  

                if not content.strip():  
                    st.error(  
                        "No selectable text found. This may be a scanned PDF."  
                    )  

                else:  
                    prompt = f"""

Make {style.lower()} in {language} using the following study material.
Use headings, bullet points, definitions and examples where appropriate.
Keep information faithful to the source and easy to revise.

STUDY MATERIAL:
{content[:500000]}
"""
st.session_state.notes_result = ask_ai(prompt)
st.session_state.notes_count += 1

except Exception as e:  
            st.error(str(e))  

if st.session_state.notes_result:  
    st.markdown("---")  
    st.subheader("Your Study Notes")  
    st.markdown(st.session_state.notes_result)  

    st.download_button(  
        "⬇ Download Notes",  
        st.session_state.notes_result,  
        file_name="study_buddy_notes.txt",  
        mime="text/plain"  
    )

elif page == "Study Chat":

st.markdown(  
    '<div class="eyebrow">YOUR PERSONAL STUDY COMPANION</div>',  
    unsafe_allow_html=True  
)  
st.title("💬 Study Chat")  
st.write("Ask a question and learn step by step.")  

for message in st.session_state.chat_history:  
    with st.chat_message(message["role"]):  
        st.markdown(message["content"])  

prompt = st.chat_input("Ask your study question...")  

if prompt:  
    st.session_state.chat_history.append({  
        "role": "user",  
        "content": prompt  
    })  

    st.session_state.chat_count += 1  

    with st.chat_message("user"):  
        st.markdown(prompt)  

    with st.chat_message("assistant"):  
        try:  
            client = get_client()  

            if client is None:  
                raise ValueError(  
                    "Add GROQ_API_KEY in Streamlit Secrets."  
                )  

            messages = [{  
                "role": "system",  
                "content": (  
                    "You are Study Buddy AI. Explain concepts in "  
                    "simple student-friendly language, with examples "  
                    "and steps. Give complete beginner-friendly code "  
                    "when asked."  
                )  
            }]  

            messages.extend(st.session_state.chat_history[-12:])  

            response = client.chat.completions.create(  
                model="openai/gpt-oss-20b",  
                messages=messages,  
                temperature=0.6  
            )  

            answer = response.choices[0].message.content  
            st.markdown(answer)  

            st.session_state.chat_history.append({  
                "role": "assistant",  
                "content": answer  
            })  

        except Exception as e:  
            st.error(str(e))  

if st.session_state.chat_history:  
    if st.button("Clear Chat"):  
        st.session_state.chat_history = []  
        st.rerun()

elif page == "Performance":

st.markdown(  
    '<div class="eyebrow">YOUR LEARNING ACTIVITY</div>',  
    unsafe_allow_html=True  
)  
st.title("📈 Performance")  
st.write("Your current session activity overview.")  

a, b, c = st.columns(3)  

with a:  
    metric_card(  
        "🧠", "Quizzes", st.session_state.quiz_count,  
        "Generated", "#5578ff"  
    )  

with b:  
    metric_card(  
        "📄", "Notes", st.session_state.notes_count,  
        "Created", "#18d6b5"  
    )  

with c:  
    metric_card(  
        "💬", "Chat", st.session_state.chat_count,  
        "Messages sent", "#b16aff"  
    )  

activity = {  
    "AI Quiz": st.session_state.quiz_count,  
    "PDF Notes": st.session_state.notes_count,  
    "Study Chat": st.session_state.chat_count  
}  

total = sum(activity.values())  

st.markdown(  
    '<div class="panel"><h3>Activity Breakdown</h3>',  
    unsafe_allow_html=True  
)  

if total:  
    st.bar_chart(activity)  

    for name, count in activity.items():  
        st.write(f"**{name}:** {count}")  
        st.progress(count / total)  

else:  
    st.info(  
        "Your activity will appear here after you use the study tools."  
    )  

st.markdown('</div>', unsafe_allow_html=True)  

st.caption(  
    "These statistics are session-only and may reset when the app restarts."  
)

elif page == "Settings":

st.markdown(  
    '<div class="eyebrow">APP CONFIGURATION</div>',  
    unsafe_allow_html=True  
)  
st.title("⚙️ Settings")  

api_key = st.secrets.get(  
    "GROQ_API_KEY",  
    os.getenv("GROQ_API_KEY", "")  
)  

st.markdown(  
    '<div class="panel"><h3>🔐 Groq AI Connection</h3>',  
    unsafe_allow_html=True  
)  

if api_key:  
    st.success("API key configured")  
else:  
    st.warning(  
        "API key not found. Add GROQ_API_KEY in Streamlit Secrets."  
    )  

st.markdown('</div>', unsafe_allow_html=True)  

st.markdown("""  
<div class="panel">  
    <h3>Application Information</h3>  
    <p>Application: Study Buddy AI</p>  
    <p>Purpose: Intelligent Learning Assistant</p>  
    <p>AI model: openai/gpt-oss-20b</p>  
    <p>Tools: AI Quiz · PDF Notes · Study Chat</p>  
</div>  
""", unsafe_allow_html=True)  

st.subheader("Reset Session")  

confirm = st.checkbox(  
    "I want to clear this session's data."  
)  

if st.button("Reset Session Data"):  

    if confirm:  
        for key_name in [  
            "quiz_result",  
            "notes_result",  
            "chat_history",  
            "quiz_count",  
            "notes_count",  
            "chat_count"  
        ]:  
            if key_name in st.session_state:  
                del st.session_state[key_name]  

        st.success("Session data cleared.")  
        st.rerun()  

    else:  
        st.warning("Confirm the reset first.")

st.markdown("""

<div class="app-footer">  
    <span>Study Buddy AI · Intelligent Learning Assistant</span>  
    <span>Learn · Practise · Grow</span>  
</div>  
""", unsafe_allow_html=True)  