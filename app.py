import os
import json
import re
import html
import streamlit as st
from groq import Groq
from pypdf import PdfReader

# ============================================================
# STUDY BUDDY AI â€” original learning workspace
# Built with Streamlit + Groq + pypdf
# ============================================================

st.set_page_config(
    page_title="Study Buddy AI",
    page_icon="ðŸŽ“",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------- STATE ----------------------------

DEFAULTS = {
    "page": "Dashboard",
    "chat_messages": [],
    "pdf_text": "",
    "pdf_name": "",
    "pdf_summary": "",
    "quiz_questions": [],
    "quiz_topic": "",
    "quiz_source": "",
    "quiz_answers": {},
    "quiz_submitted": False,
    "quiz_history": [],
    "weekly_goal": 5,
    "last_summary": "",
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------------- DESIGN ---------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
      --bg: #080D1B;
      --panel: #10182B;
      --panel2: #141F36;
      --line: #263552;
      --muted: #9BAAC8;
      --white: #F4F7FF;
      --violet: #9B87FF;
      --cyan: #62E5D0;
    }

    html, body, [class*="css"] {
      font-family: 'DM Sans', sans-serif;
    }
    .stApp {
      background:
        radial-gradient(ellipse at 70% 0%, rgba(77, 68, 180, .17), transparent 32%),
        radial-gradient(ellipse at 5% 80%, rgba(20, 120, 145, .08), transparent 30%),
        var(--bg);
      color: var(--white);
    }
    [data-testid="stHeader"] { background: rgba(8,13,27,.78); }
    [data-testid="stSidebar"] {
      background: linear-gradient(180deg, #0B1223 0%, #0A1020 100%);
      border-right: 1px solid #202C45;
    }
    [data-testid="stSidebar"] > div { padding-top: 1.3rem; }
    h1, h2, h3, h4 {
      font-family: 'Space Grotesk', sans-serif !important;
      color: var(--white) !important;
      letter-spacing: -.45px;
    }
    p, label, .stMarkdown { color: #D5DEF1; }
    [data-testid="stCaptionContainer"] { color: var(--muted); }

    .brand {
      display:flex; align-items:center; gap:12px; padding: 4px 4px 20px 4px;
    }
    .brand-mark {
      width:48px; height:48px; border-radius:16px;
      display:flex; align-items:center; justify-content:center;
      font-size:25px; color:white;
      background:linear-gradient(145deg,#A18BFF,#5B4CE2 60%,#20B8C5);
      box-shadow:0 8px 28px rgba(110,91,255,.25);
    }
    .brand-name {font:700 20px 'Space Grotesk',sans-serif;color:#F7F8FF;}
    .brand-sub {font-size:11px;color:#9EADCC;margin-top:3px;letter-spacing:.7px;}
    .topline {color:#A89AFF;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;}
    .hero {
      position:relative; overflow:hidden; padding:31px 30px 27px;
      border-radius:24px; margin:2px 0 22px;
      border:1px solid rgba(163,145,255,.42);
      background:
        radial-gradient(circle at 78% 45%, rgba(87,177,255,.25), transparent 24%),
        radial-gradient(circle at 100% 0%, rgba(125,83,255,.50), transparent 42%),
        linear-gradient(120deg,#171345 0%,#172B68 53%,#123D62 100%);
      box-shadow:0 18px 48px rgba(16,23,70,.25);
    }
    .hero:after {
      content:"âœ¦   Â·   âœ§"; position:absolute; right:6%; top:18%;
      font-size:31px; letter-spacing:17px; color:#A9F5FF; opacity:.65;
    }
    .hero h1 {font-size:35px !important;line-height:1.13;margin:10px 0 10px;}
    .hero p {max-width:570px;color:#D8E2FF;font-size:14px;line-height:1.7;margin-bottom:0;}
    .hero-bubble {
      display:inline-block; background:rgba(255,255,255,.10);
      border:1px solid rgba(255,255,255,.18); padding:6px 10px;
      border-radius:999px; color:#E7E3FF; font-size:11px; font-weight:700;
    }
    .stat-card {
      border:1px solid #293958; border-radius:18px; padding:18px 18px 16px;
      background:linear-gradient(145deg,rgba(22,33,57,.98),rgba(13,22,40,.98));
      min-height:137px; box-shadow:0 8px 22px rgba(0,0,0,.08);
    }
    .stat-icon {font-size:21px;margin-bottom:10px;}
    .stat-label {font-size:12px;color:#AEBBD5;margin-bottom:7px;}
    .stat-value {font:700 27px 'Space Grotesk',sans-serif;color:#F7F8FF;}
    .stat-foot {font-size:11px;color:#61E5BD;margin-top:7px;}
    .section-kicker {font-size:11px;color:#A89AFF;letter-spacing:1.7px;font-weight:700;text-transform:uppercase;margin-bottom:5px;}
    .tool-card {
      border:1px solid #2A3857; border-radius:19px; padding:18px;
      min-height:178px; background:linear-gradient(145deg,#151F36,#10182A);
      margin-bottom:8px;
    }
    .tool-symbol {
      width:44px;height:44px;border-radius:14px;display:flex;
      align-items:center;justify-content:center;font-size:22px;margin-bottom:13px;
    }
    .tool-card h3 {font-size:17px !important;margin:0 0 7px;}
    .tool-card p {font-size:12px;color:#AEBBD5;line-height:1.6;min-height:38px;}
    .side-panel {
      border:1px solid #293958;border-radius:18px;padding:18px;
      background:linear-gradient(145deg,#121D33,#0D1628);
      margin-bottom:15px;
    }
    .activity-row {display:flex;gap:11px;align-items:center;padding:12px 0;border-bottom:1px solid #25324B;}
    .activity-row:last-child {border-bottom:0;}
    .activity-icon {width:37px;height:37px;display:flex;align-items:center;justify-content:center;border-radius:12px;font-size:17px;flex-shrink:0;}
    .activity-title {font-size:12px;color:#F3F6FF;font-weight:600;}
    .activity-sub {font-size:11px;color:#9EADCC;margin-top:3px;}
    .quote-panel {
      border:1px solid #3D3B77;border-radius:18px;padding:21px;
      background:radial-gradient(circle at 90% 0%,rgba(142,97,255,.30),transparent 45%),linear-gradient(130deg,#171843,#172C59);
    }
    .quote-panel .big {font:600 21px 'Space Grotesk',sans-serif;color:white;line-height:1.35;}
    .mini-label {font-size:11px;color:#A9B7D2;letter-spacing:.7px;text-transform:uppercase;}
    .soft-divider {height:1px;background:#25334F;margin:18px 0;}
    div.stButton > button {
      border-radius:11px; border:1px solid #7668F5;
      background:linear-gradient(100deg,#755CF4,#5A50D9);
      color:#fff; font-weight:700; min-height:42px;
      transition:all .18s ease;
    }
    div.stButton > button:hover {
      border-color:#B2A8FF;color:#fff;transform:translateY(-1px);
      box-shadow:0 7px 22px rgba(117,92,244,.19);
    }
    div.stButton > button[kind="secondary"] {
      background:#151F36;border:1px solid #334260;color:#E8EDFC;
    }
    .stTextInput input,.stTextArea textarea,.stNumberInput input,
    [data-baseweb="select"] > div {
      background:#10192D !important;color:#F5F7FF !important;
      border-color:#344361 !important;border-radius:11px !important;
    }
    [data-testid="stFileUploader"] {
      background:#10192D;border:1px dashed #655AD0;border-radius:16px;padding:13px;
    }
    [data-testid="stMetric"] {
      background:#121D33;border:1px solid #293958;border-radius:15px;padding:14px;
    }
    [data-testid="stMetricValue"] {color:#F7F8FF;}
    [data-testid="stProgressBar"] > div > div {background:linear-gradient(90deg,#8A73FF,#48DCCF);}
    .stRadio label,.stCheckbox label {color:#E5EBFA !important;}
    div[data-testid="stExpander"] {border:1px solid #2A3857;border-radius:13px;background:#10192D;}
    .stAlert {border-radius:13px;}
    footer {visibility:hidden;}
    #MainMenu {visibility:hidden;}
    @media(max-width:800px) {
      .hero {padding:24px 20px;}
      .hero h1 {font-size:28px !important;}
      .stat-card {padding:14px;min-height:120px;}
      .stat-value {font-size:23px;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------- AI HELPERS -----------------------

def get_client():
    key = ""
    try:
        key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass
    key = key or os.environ.get("GROQ_API_KEY", "")
    return Groq(api_key=key) if key else None


def ask_ai(prompt, system="You are Study Buddy AI, a helpful and accurate study assistant. Explain clearly in simple language."):
    client = get_client()
    if client is None:
        raise ValueError("API key missing. Add GROQ_API_KEY in Streamlit Cloud â†’ App settings â†’ Secrets.")
    result = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.35,
    )
    return result.choices[0].message.content.strip()


def parse_json_object(raw):
    cleaned = re.sub(r"```(?:json)?", "", raw, flags=re.I).replace("```", "").strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end < start:
        raise ValueError("AI returned an unexpected format. Please try again.")
    return json.loads(cleaned[start:end + 1])


def generate_questions(topic, count, source_text=""):
    questions = []
    batch_size = 10
    for start in range(0, count, batch_size):
        batch_count = min(batch_size, count - start)
        context = source_text[:14000] if source_text else "Use general, reliable educational knowledge."
        prompt = f"""
Create exactly {batch_count} distinct multiple-choice questions for a student.
Topic: {topic}
Source notes (if supplied; prioritize these notes):
{context}

Return ONLY valid JSON in this exact structure:
{{
 "questions": [
  {{
   "question": "Question text",
   "options": ["Option A", "Option B", "Option C", "Option D"],
   "answer": 0,
   "explanation": "Short explanation of why the answer is correct"
  }}
 ]
}}
Rules:
- answer must be an integer 0, 1, 2, or 3 matching the correct option.
- Four plausible options, only one correct answer.
- Avoid repeated questions.
- Use clear, student-friendly language.
- Do not include markdown or text outside JSON.
- This is batch {start // batch_size + 1}; make questions distinct from each other.
"""
        raw = ask_ai(prompt, "You are an expert question setter. Output only valid JSON.")
        data = parse_json_object(raw)
        batch = data.get("questions", [])
        for q in batch:
            if (
                isinstance(q, dict)
                and isinstance(q.get("question"), str)
                and isinstance(q.get("options"), list)
                and len(q["options"]) == 4
                and isinstance(q.get("answer"), int)
                and q["answer"] in range(4)
            ):
                q["explanation"] = str(q.get("explanation", ""))
                questions.append(q)
    if len(questions) < count:
        raise ValueError(f"AI created only {len(questions)} valid questions. Try a smaller number.")
    return questions[:count]


def safe_text(value):
    return html.escape(str(value))


def go_to(page):
    st.session_state.page = page
    st.rerun()


def record_quiz(score, total, topic):
    st.session_state.quiz_history.append({
        "score": score,
        "total": total,
        "topic": topic,
    })


# -------------------------- SIDEBAR --------------------------

with st.sidebar:
    st.markdown(
        """
        <div class="brand">
          <div class="brand-mark">âœ¦</div>
          <div>
            <div class="brand-name">Study Buddy <span style="color:#A99AFF">AI</span></div>
            <div class="brand-sub">LEARN Â· PRACTICE Â· GROW</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="mini-label" style="padding:4px 4px 10px">YOUR WORKSPACE</div>', unsafe_allow_html=True)

    nav_items = [
        ("âŒ‚", "Dashboard"),
        ("âœ§", "AI Quiz"),
        ("â–¤", "PDF Notes"),
        ("â—‰", "AI Study Chat"),
        ("â†—", "Performance"),
        ("âš™", "Settings"),
    ]
    for symbol, name in nav_items:
        selected = st.session_state.page == name
        if st.button(
            f"{symbol}    {name}",
            key=f"nav_{name}",
            use_container_width=True,
            type="primary" if selected else "secondary",
        ):
            st.session_state.page = name
            st.rerun()

    st.markdown("<div class='soft-divider'></div>", unsafe_allow_html=True)
    done = len(st.session_state.quiz_history)
    goal = max(1, int(st.session_state.weekly_goal))
    st.markdown(
        f"""
        <div class="side-panel">
          <div style="font-size:23px">ðŸŒ±</div>
          <div style="font-weight:700;color:white;margin:8px 0 5px">Your weekly rhythm</div>
          <div style="font-size:12px;color:#AEBBD5;line-height:1.6">
            Every practice session is progress. Keep building your learning habit.
          </div>
          <div style="height:6px;background:#293654;border-radius:10px;margin-top:13px;overflow:hidden">
            <div style="height:100%;width:{min(100, done / goal * 100):.0f}%;background:linear-gradient(90deg,#8A73FF,#56E1D0);border-radius:10px"></div>
          </div>
          <div style="font-size:11px;color:#AEBBD5;margin-top:7px">{done} of {goal} quizzes logged</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Study Buddy AI Â· Independent student project")


# -------------------------- TOP BAR --------------------------

top_left, top_right = st.columns([5, 1.6])
with top_left:
    st.markdown(
        f"<div class='mini-label' style='padding-top:10px'>STUDY WORKSPACE&nbsp;&nbsp; / &nbsp;&nbsp;{safe_text(st.session_state.page.upper())}</div>",
        unsafe_allow_html=True,
    )
with top_right:
    st.markdown(
        "<div style='text-align:right;padding-top:5px;color:#B8C5DF;font-size:12px'>âœ¦ Your learning space</div>",
        unsafe_allow_html=True,
    )
st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)


# -------------------------- DASHBOARD ------------------------

if st.session_state.page == "Dashboard":
    st.markdown(
        """
        <div class="hero">
          <span class="hero-bubble">âœ¦ YOUR PERSONAL LEARNING INTELLIGENCE</span>
          <h1>Make room for a<br>little more understanding.</h1>
          <p>
            Turn difficult topics into clear explanations, transform your notes
            into practice, and see your learning grow â€” one session at a time.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    history = st.session_state.quiz_history
    quiz_count = len(history)
    attempted = sum(x["total"] for x in history)
    correct = sum(x["score"] for x in history)
    accuracy = round(correct / attempted * 100) if attempted else 0
    study_time = "â€”"

    stats = [
        ("âœ§", "Quizzes completed", str(quiz_count), "Your practice sessions", "#A58BFF"),
        ("â–¤", "Questions practised", str(attempted), "Across your quiz history", "#62B7FF"),
        ("â—Ž", "Overall accuracy", f"{accuracy}%", "Based on submitted quizzes", "#62E5C4"),
        ("â—·", "Study streak", "Keep going", "Build your own rhythm", "#FFC078"),
    ]
    cols = st.columns(4)
    for col, item in zip(cols, stats):
        icon, label, value, foot, color = item
        with col:
            st.markdown(
                f"""
                <div class="stat-card">
                  <div class="stat-icon" style="color:{color}">{icon}</div>
                  <div class="stat-label">{label}</div>
                  <div class="stat-value" style="font-size:{'22px' if len(value)>8 else '27px'}">{value}</div>
                  <div class="stat-foot" style="color:#9EADCC">â†— {foot}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    st.markdown('<div class="section-kicker">CHOOSE YOUR NEXT STEP</div>', unsafe_allow_html=True)
    st.subheader("What would you like to work on?")
    st.caption("Four tools. One workspace designed around the way you learn.")

    tool_cols = st.columns(4)
    tools = [
        ("ðŸ§ ", "Concept Lab", "Create MCQs from any topic and learn from each explanation.", "#342767", "AI Quiz", "Build a quiz"),
        ("ðŸ“š", "Knowledge Vault", "Upload PDF notes and turn long chapters into clear summaries.", "#123E4A", "PDF Notes", "Open notes"),
        ("âœ¦", "Study Companion", "Ask questions, explore ideas and get simple explanations.", "#47301E", "AI Study Chat", "Ask a question"),
        ("â†—", "Growth Map", "Review completed quizzes and see your accuracy over time.", "#48203F", "Performance", "View progress"),
    ]
    for col, tool in zip(tool_cols, tools):
        icon, title, desc, bg, page, button = tool
        with col:
            st.markdown(
                f"""
                <div class="tool-card">
                  <div class="tool-symbol" style="background:{bg};">{icon}</div>
                  <h3>{title}</h3>
                  <p>{desc}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(button + " â†’", key="open_" + page, use_container_width=True):
                go_to(page)

    st.write("")
    left, right = st.columns([1.55, 1])
    with left:
        st.markdown('<div class="side-panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-kicker">YOUR LEARNING JOURNEY</div>', unsafe_allow_html=True)
        st.markdown("### Progress is built one session at a time")
        if history:
            recent = history[-7:]
            for item in recent:
                percent = round(item["score"] / item["total"] * 100) if item["total"] else 0
                st.markdown(
                    f"**{safe_text(item['topic'])}** Â· {item['score']}/{item['total']} correct"
                )
                st.progress(percent / 100, text=f"{percent}% accuracy")
        else:
            st.markdown(
                "<div style='padding:18px 0;color:#AEBBD5'>"
                "Your first quiz will appear here. Start with a topic you want to understand better."
                "</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown(
            """
            <div class="quote-panel">
              <div class="mini-label">A NOTE TO YOUR FUTURE SELF</div>
              <div class="big" style="margin-top:13px">Progress, not perfection.</div>
              <p style="font-size:13px;line-height:1.7;color:#D4D9FF;margin-top:12px">
                You don't have to know everything today. Just understand one more thing than yesterday.
              </p>
              <div style="font-size:26px;margin-top:15px">âœ¦ã€€ðŸŒ±ã€€âœ¦</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# -------------------------- AI QUIZ --------------------------

elif st.session_state.page == "AI Quiz":
    st.markdown('<div class="section-kicker">CONCEPT LAB</div>', unsafe_allow_html=True)
    st.title("Build a quiz around your curiosity.")
    st.caption("Create practice questions from a topic, or use the PDF you uploaded in Knowledge Vault.")

    with st.container(border=True):
        topic = st.text_input("What topic are you studying?", placeholder="e.g. C programming functions, matrices, semiconductor diodes")
        count = st.select_slider("Number of questions", options=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100], value=10)
        use_pdf = st.checkbox("Use my uploaded PDF notes as the main source", value=bool(st.session_state.pdf_text))
        if use_pdf and not st.session_state.pdf_text:
            st.info("Upload a PDF first in the PDF Notes section.")
        generate = st.button("âœ¦ Generate my quiz", type="primary", use_container_width=True)

    if generate:
        if not topic.strip() and not (use_pdf and st.session_state.pdf_text):
            st.warning("Enter a topic or upload a PDF and choose to use it.")
        elif use_pdf and not st.session_state.pdf_text and not topic.strip():
            st.warning("Please upload notes first.")
        else:
            final_topic = topic.strip() or st.session_state.pdf_name or "Uploaded study notes"
            source = st.session_state.pdf_text if use_pdf else ""
            with st.spinner(f"Building your {count}-question quiz in batches. This may take a little while..."):
                try:
                    questions = generate_questions(final_topic, int(count), source)
                    st.session_state.quiz_questions = questions
                    st.session_state.quiz_topic = final_topic
                    st.session_state.quiz_source = "PDF notes" if use_pdf else "Topic"
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_submitted = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Quiz generation failed: {e}")

    if st.session_state.quiz_questions:
        st.markdown("<div class='soft-divider'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-kicker">YOUR PRACTICE SESSION</div>', unsafe_allow_html=True)
        st.subheader(st.session_state.quiz_topic)
        st.caption(f"{len(st.session_state.quiz_questions)} questions Â· Source: {st.session_state.quiz_source}")

        if not st.session_state.quiz_submitted:
            with st.form("quiz_form"):
                chosen = {}
                for i, q in enumerate(st.session_state.quiz_questions):
                    st.markdown(f"**{i+1}. {q['question']}**")
                    chosen[str(i)] = st.radio(
                        "Choose one answer",
                        options=list(range(4)),
                        format_func=lambda idx, opts=q["options"]: f"{chr(65+idx)}. {opts[idx]}",
                        key=f"q_{i}",
                        index=None,
                        label_visibility="collapsed",
                    )
                    st.markdown("<div class='soft-divider'></div>", unsafe_allow_html=True)
                submit = st.form_submit_button("Submit answers & see results", use_container_width=True)
                if submit:
                    st.session_state.quiz_answers = chosen
                    st.session_state.quiz_submitted = True
                    score = sum(
                        1 for i, q in enumerate(st.session_state.quiz_questions)
                        if chosen.get(str(i)) == q["answer"]
                    )
                    record_quiz(score, len(st.session_state.quiz_questions), st.session_state.quiz_topic)
                    st.rerun()
        else:
            score = sum(
                1 for i, q in enumerate(st.session_state.quiz_questions)
                if st.session_state.quiz_answers.get(str(i)) == q["answer"]
            )
            total = len(st.session_state.quiz_questions)
            pct = round(score / total * 100) if total else 0
            a, b, c = st.columns(3)
            a.metric("Your score", f"{score}/{total}")
            b.metric("Accuracy", f"{pct}%")
            c.metric("Not answered", sum(1 for i in range(total) if st.session_state.quiz_answers.get(str(i)) is None))
            st.progress(pct / 100, text="Your quiz performance")
            st.markdown("### Answer review")
            for i, q in enumerate(st.session_state.quiz_questions):
                selected = st.session_state.quiz_answers.get(str(i))
                correct_idx = q["answer"]
                with st.expander(f"{'âœ…' if selected == correct_idx else 'âŒ'} {i+1}. {q['question']}"):
                    if selected is None:
                        st.write("Your answer: Not answered")
                    else:
                        st.write(f"Your answer: {q['options'][selected]}")
                    st.write(f"Correct answer: {q['options'][correct_idx]}")
                    st.write(f"Explanation: {q.get('explanation', 'Review this concept in your notes.')}")
            if st.button("Create another quiz", use_container_width=True):
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False
                st.rerun()


# -------------------------- PDF NOTES ------------------------

elif st.session_state.page == "PDF Notes":
    st.markdown('<div class="section-kicker">KNOWLEDGE VAULT</div>', unsafe_allow_html=True)
    st.title("Your notes, made easier to understand.")
    st.caption("Upload a PDF, create a summary, and use the same notes to generate practice questions.")

    uploaded = st.file_uploader("Choose your PDF notes", type=["pdf"], help="Text-based PDFs work best.")
    if uploaded is not None:
        try:
            reader = PdfReader(uploaded)
            pages_text = [page.extract_text() or "" for page in reader.pages]
            extracted = "\n".join(pages_text).strip()
            if not extracted:
                st.warning("No readable text was found. This may be a scanned PDF.")
            else:
                st.session_state.pdf_text = extracted[:60000]
                st.session_state.pdf_name = uploaded.name
                st.success(f"Loaded {uploaded.name} Â· {len(reader.pages)} pages Â· {len(extracted):,} characters")
        except Exception as e:
            st.error(f"Could not read this PDF: {e}")

    if st.session_state.pdf_text:
        st.markdown("<div class='soft-divider'></div>", unsafe_allow_html=True)
        left, right = st.columns([1.4, 1])
        with left:
            st.markdown("### ðŸ“„ Current document")
            st.markdown(f"**{safe_text(st.session_state.pdf_name)}**")
            st.caption(f"{len(st.session_state.pdf_text):,} characters available for AI study tools.")
            with st.expander("Preview extracted text"):
                st.text(st.session_state.pdf_text[:3500])
        with right:
            st.markdown("### What should we make?")
            if st.button("âœ¦ Create a smart summary", use_container_width=True):
                with st.spinner("Reading your notes and preparing a summary..."):
                    try:
                        summary = ask_ai(
                            "Summarize the following student notes in simple English. Include: "
                            "1. Short overview, 2. Important concepts, 3. Key definitions/formulas, "
                            "4. Quick revision points. Do not invent information not in the notes.\n\n"
                            + st.session_state.pdf_text[:14000]
                        )
                        st.session_state.pdf_summary = summary
                    except Exception as e:
                        st.error(str(e))
            if st.button("ðŸ§  Make a quiz from these notes", use_container_width=True):
                st.session_state.page = "AI Quiz"
                st.rerun()

        if st.session_state.pdf_summary:
            st.markdown("<div class='soft-divider'></div>", unsafe_allow_html=True)
            st.markdown("### Your smart summary")
            st.markdown(st.session_state.pdf_summary)
            st.download_button(
                "Download summary as TXT",
                data=st.session_state.pdf_summary,
                file_name="study_buddy_summary.txt",
                mime="text/plain",
                use_container_width=True,
            )
    else:
        st.markdown(
            """
            <div class="side-panel">
              <div style="font-size:28px">ðŸ“˜</div>
              <h3 style="margin-top:10px">A calmer way to revise</h3>
              <p style="font-size:13px;line-height:1.7;color:#AEBBD5">
                Once you upload notes, you can preview extracted text, generate a clear summary,
                and create a quiz based on the document.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# -------------------------- AI CHAT --------------------------

elif st.session_state.page == "AI Study Chat":
    st.markdown('<div class="section-kicker">STUDY COMPANION</div>', unsafe_allow_html=True)
    st.title("Ask the question on your mind.")
    st.caption("Get clear, student-friendly explanations. You can ask in English or Hinglish.")

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"], avatar="âœ¦" if msg["role"] == "assistant" else "ðŸ™‚"):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask about a topic, formula, code or concept...")
    if prompt:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="ðŸ™‚"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="âœ¦"):
            with st.spinner("Thinking through your question..."):
                try:
                    context = ""
                    if st.session_state.pdf_text:
                        context = "\nThe user has uploaded study notes. Use these notes when relevant:\n" + st.session_state.pdf_text[:8000]
                    answer = ask_ai(
                        prompt + context,
                        "You are Study Buddy AI, a patient tutor for a college student. "
                        "Explain step by step in simple language. If the user asks for code, "
                        "provide complete runnable beginner-friendly code and explain it briefly. "
                        "Do not pretend to know facts you are unsure about."
                    )
                    st.markdown(answer)
                    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    error_msg = str(e)
                    st.error(error_msg)
                    st.session_state.chat_messages.append({"role": "assistant", "content": "I couldn't answer because the AI service is not configured or returned an error. Check the app's API key and try again."})

    if st.session_state.chat_messages and st.button("Clear chat history", type="secondary"):
        st.session_state.chat_messages = []
        st.rerun()


# -------------------------- PERFORMANCE ----------------------

elif st.session_state.page == "Performance":
    st.markdown('<div class="section-kicker">GROWTH MAP</div>', unsafe_allow_html=True)
    st.title("Your learning, at a glance.")
    st.caption("A record of quizzes you have submitted in this app.")

    history = st.session_state.quiz_history
    total_quizzes = len(history)
    total_questions = sum(item["total"] for item in history)
    total_correct = sum(item["score"] for item in history)
    accuracy = round(total_correct / total_questions * 100) if total_questions else 0

    a, b, c = st.columns(3)
    a.metric("Quizzes completed", total_quizzes)
    b.metric("Questions answered", total_questions)
    c.metric("Overall accuracy", f"{accuracy}%")

    st.markdown("<div class='soft-divider'></div>", unsafe_allow_html=True)
    st.subheader("Quiz history")
    if history:
        for index, item in enumerate(reversed(history), start=1):
            pct = round(item["score"] / item["total"] * 100) if item["total"] else 0
            with st.container(border=True):
                left, mid, right = st.columns([3, 1, 1])
                left.markdown(f"**{safe_text(item['topic'])}**")
                left.caption(f"{item['total']} questions")
                mid.metric("Score", f"{item['score']}/{item['total']}")
                right.metric("Accuracy", f"{pct}%")
                st.progress(pct / 100)
    else:
        st.info("No quiz history yet. Complete a quiz in Concept Lab and your results will appear here.")

    st.caption("Note: this version keeps progress in the current app session. Permanent history across visits needs a database or storage integration.")


# -------------------------- SETTINGS -------------------------

elif st.session_state.page == "Settings":
    st.markdown('<div class="section-kicker">WORKSPACE PREFERENCES</div>', unsafe_allow_html=True)
    st.title("Make this space yours.")
    st.caption("Manage your learning goal and check whether the AI connection is configured.")

    st.markdown("### Weekly learning goal")
    goal = st.number_input("Target quizzes per week", min_value=1, max_value=50, value=int(st.session_state.weekly_goal), step=1)
    if st.button("Save weekly goal", use_container_width=True):
        st.session_state.weekly_goal = int(goal)
        st.success("Weekly goal updated for this session.")

    st.markdown("<div class='soft-divider'></div>", unsafe_allow_html=True)
    st.markdown("### AI connection")
    if get_client():
        st.success("Groq API key detected. AI features can connect.")
    else:
        st.warning("Groq API key not found. Add GROQ_API_KEY in Streamlit Cloud â†’ App settings â†’ Secrets.")
    st.code('GROQ_API_KEY = "your_actual_key_here"', language="toml")
    st.caption("Keep your real API key private. Never paste it into public GitHub code.")

    st.markdown("<div class='soft-divider'></div>", unsafe_allow_html=True)
    st.markdown("### About this project")
    st.markdown(
        """
        **Study Buddy AI** is an independently assembled student learning workspace.
        It combines AI-powered question generation, PDF text extraction, summaries,
        chat-based explanations and quiz-result tracking.
        """
    )
    if st.button("Reset quiz in progress", type="secondary"):
        st.session_state.quiz_questions = []
        st.session_state.quiz_answers = {}
        st.session_state.quiz_submitted = False
        st.success("Current quiz cleared.")
