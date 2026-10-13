
import json
import uuid
from pathlib import Path
from datetime import datetime

import streamlit as st
from agent.core import answer_question


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="SmartDesk AI | Intelligent Workspace",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CHAT HISTORY STORAGE
# =========================================================

HISTORY_FILE = Path(__file__).parent / "chat_history.json"


def load_chats():
    """Load saved conversations from local JSON storage."""
    try:
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, list):
                return data

    except (json.JSONDecodeError, OSError):
        pass

    return []


def save_chats(chats):
    """Save all conversations to local JSON storage."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(
                chats,
                file,
                ensure_ascii=False,
                indent=2
            )
    except OSError as exc:
        st.error(f"Could not save chat history: {exc}")


def save_current_chat():
    """Save or update the active conversation."""
    messages = st.session_state.messages

    if not messages:
        return

    chat_id = st.session_state.active_chat_id

    if not chat_id:
        chat_id = str(uuid.uuid4())
        st.session_state.active_chat_id = chat_id

    chats = st.session_state.chats

    existing = next(
        (
            chat for chat in chats
            if chat.get("id") == chat_id
        ),
        None
    )

    first_user_message = next(
        (
            message.get("content", "")
            for message in messages
            if message.get("role") == "user"
        ),
        "New conversation"
    )

    now = datetime.now().isoformat()

    chat_data = {
        "id": chat_id,
        "title": first_user_message.strip()[:45]
                 or "New conversation",
        "messages": messages.copy(),
        "updated_at": now,
    }

    if existing:
        existing.update(chat_data)
    else:
        chats.append(chat_data)

    chats.sort(
        key=lambda chat: chat.get("updated_at", ""),
        reverse=True
    )

    st.session_state.chats = chats
    save_chats(chats)


def start_new_chat():
    """Start a fresh conversation without deleting saved chats."""
    st.session_state.messages = []
    st.session_state.active_chat_id = None
    st.session_state.pending_question = None


def open_chat(chat):
    """Open a saved conversation."""
    st.session_state.active_chat_id = chat.get("id")
    st.session_state.messages = [
        dict(message)
        for message in chat.get("messages", [])
    ]
    st.session_state.pending_question = None


# =========================================================
# SESSION STATE
# =========================================================

if "chats" not in st.session_state:
    st.session_state.chats = load_chats()

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# =========================================================
# CUSTOM CSS — SMARTDESK PREMIUM DARK DASHBOARD
# =========================================================

st.markdown("""
<style>
@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap'
);

:root {
    --bg: #090909;
    --panel: #171717;
    --panel2: #202020;
    --border: #2d2d2d;
    --text: #f5f5f5;
    --muted: #a3a3a3;
    --lime: #d0ff32;
}

.stApp {
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stMain"] {
    background: var(--bg);
}

.block-container {
    max-width: 1500px;
    padding: 1.5rem 2rem 3rem;
}

/* Sidebar */

[data-testid="stSidebar"] {
    background: #0c0c0c;
    border-right: 1px solid #252525;
}

[data-testid="stSidebar"] > div {
    padding-top: 1.2rem;
}

[data-testid="stSidebar"] * {
    font-family: 'Inter', sans-serif;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 0 18px;
}

.brand-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    min-width: 43px;
    height: 43px;
    border-radius: 13px;
    background: var(--lime);
    color: #080808;
    font-size: 24px;
    font-weight: 900;
}

.brand-name {
    color: #ffffff;
    font-size: 19px;
    font-weight: 800;
    letter-spacing: -0.6px;
}

.brand-sub {
    margin-top: 4px;
    color: #999999;
    font-size: 9px;
    letter-spacing: 1.5px;
}

.side-label {
    margin: 18px 0 10px;
    color: #a0a0a0;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.4px;
    text-transform: uppercase;
}

.side-card {
    padding: 14px;
    border: 1px solid var(--border);
    border-radius: 14px;
    background: var(--panel);
}

.side-muted {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.8;
}

/* Hero */

.hero {
    position: relative;
    isolation: isolate;
    overflow: hidden;
    padding: clamp(25px, 4vw, 46px);
    margin-bottom: 22px;
    border: none;
    border-radius: 23px;
    background: var(--lime);
    color: #080808;
    animation: enter .5s ease both;
}

.hero::before {
    content: "";
    position: absolute;
    z-index: -1;
    right: -65px;
    top: -125px;
    width: 310px;
    height: 310px;
    border: 1px solid #08080830;
    border-radius: 50%;
    box-shadow:
        0 0 0 25px #08080808,
        0 0 0 55px #08080808,
        0 0 0 85px #08080808;
}

.hero-tag {
    display: inline-block;
    padding: 8px 12px;
    border: 1px solid #08080840;
    border-radius: 30px;
    color: #080808;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
}

.hero h1 {
    margin: 22px 0 12px;
    color: #080808;
    font-size: clamp(35px, 4vw, 55px);
    font-weight: 900;
    letter-spacing: -2px;
    line-height: 1.1;
}

.hero p {
    max-width: 650px;
    color: #202b0a;
    font-size: 14px;
    line-height: 1.8;
}

.hero-footer {
    margin-top: 22px;
    color: #202b0a;
    font-size: 11px;
    font-weight: 600;
}

/* Cards */

.metric {
    height: 100%;
    min-height: 135px;
    padding: 20px;
    border: 1px solid var(--border);
    border-radius: 17px;
    background: linear-gradient(145deg, #191919, #121212);
    transition: transform .2s ease, border-color .2s ease;
}

.metric:hover {
    transform: translateY(-3px);
    border-color: #d0ff3270;
}

.metric-icon {
    margin-bottom: 13px;
    color: var(--lime);
    font-size: 22px;
}

.metric-label {
    color: #a5a5a5;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
}

.metric-value {
    margin-top: 9px;
    color: #f5f5f5;
    font-size: 14px;
    font-weight: 700;
}

.workflow {
    padding: 22px;
    margin-top: 22px;
    border: 1px solid var(--border);
    border-radius: 18px;
    background: #141414;
}

.workflow-title {
    color: #f5f5f5;
    font-size: 16px;
    font-weight: 800;
}

.workflow-subtitle {
    margin-top: 5px;
    margin-bottom: 18px;
    color: var(--muted);
    font-size: 12px;
}

.flow-grid {
    display: grid;
    grid-template-columns: 1fr auto 1fr auto 1fr;
    align-items: center;
    gap: 12px;
}

.flow-step {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 10px;
    min-height: 95px;
    padding: 12px 5px;
    border: 1px solid #303030;
    border-radius: 13px;
    background: #1c1c1c;
    text-align: center;
}

.flow-icon {
    color: var(--lime);
    font-size: 23px;
}

.flow-label {
    color: #e5e5e5;
    font-size: 11px;
    font-weight: 700;
}

.flow-arrow {
    color: var(--lime);
    font-size: 20px;
}

/* Buttons */

div.stButton > button {
    min-height: 42px;
    border: 1px solid #303030;
    border-radius: 11px;
    background: #191919;
    color: #f5f5f5;
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 600;
    transition: all .2s ease;
}

div.stButton > button:hover {
    border-color: var(--lime);
    background: var(--lime);
    color: #080808;
}

/* Primary buttons */

div.stButton > button[kind="primary"] {
    border-color: var(--lime);
    background: var(--lime);
    color: #080808;
}

/* Chat */

[data-testid="stChatMessage"] {
    padding: 15px 17px;
    margin-bottom: 12px;
    border: 1px solid #2d2d2d;
    border-radius: 16px;
    background: #171717;
}

[data-testid="stChatMessage"] p {
    font-size: 13px;
    line-height: 1.85;
}

[data-testid="stChatInput"] {
    border: 1px solid #383838;
    border-radius: 15px;
    background: #171717;
}

[data-testid="stChatInput"]:focus-within {
    border-color: var(--lime);
    box-shadow: 0 0 0 1px #d0ff3230;
}

[data-testid="stChatInput"] textarea {
    color: #f5f5f5 !important;
}

[data-testid="stChatInput"] button {
    color: var(--lime);
}

/* Welcome */

.welcome-card {
    padding: 28px 18px;
    margin: 15px 0;
    border: 1px dashed #383838;
    border-radius: 18px;
    background: #141414;
    text-align: center;
}

.welcome-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 54px;
    height: 54px;
    margin-bottom: 13px;
    border-radius: 16px;
    background: var(--lime);
    color: #080808;
    font-size: 26px;
}

.welcome-title {
    margin-bottom: 8px;
    color: #f5f5f5;
    font-size: 19px;
    font-weight: 800;
}

.welcome-text {
    color: var(--muted);
    font-size: 12px;
    line-height: 1.8;
}

.section-heading {
    margin: 28px 0 5px;
    color: #f5f5f5;
    font-size: 22px;
    font-weight: 800;
}

.section-sub {
    margin-bottom: 16px;
    color: var(--muted);
    font-size: 12px;
}

.suggestion-label {
    margin: 18px 0 12px;
    color: var(--lime);
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1.4px;
}

hr {
    border-color: #292929;
}

footer, #MainMenu {
    visibility: hidden;
}

@keyframes enter {
    from { opacity: 0; transform: translateY(7px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 700px) {
    .block-container {
        padding: 1rem 1rem 2rem;
    }

    .hero {
        padding: 24px 20px;
        border-radius: 18px;
    }

    .hero h1 {
        font-size: 34px;
        letter-spacing: -1px;
    }

    .flow-grid {
        grid-template-columns: 1fr;
    }

    .flow-arrow {
        transform: rotate(90deg);
        text-align: center;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: .01ms !important;
    }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("""
    <div class="brand">
        <div class="brand-icon">✳</div>
        <div>
            <div class="brand-name">SmartDesk AI</div>
            <div class="brand-sub">INTELLIGENT WORKSPACE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown(
        '<div class="side-label">Workspace</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="side-muted">◈ &nbsp; Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="side-label">Your conversations</div>',
        unsafe_allow_html=True
    )

    if st.button(
        "＋  New conversation",
        key="new_conversation",
        use_container_width=True
    ):
        start_new_chat()
        st.rerun()

    if not st.session_state.chats:
        st.markdown(
            '<div class="side-muted">'
            'Your saved conversations will appear here.'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        for chat in st.session_state.chats:
            chat_id = chat.get("id")
            chat_title = chat.get("title", "New conversation")

            button_label = "◷  " + chat_title[:35]

            if st.button(
                button_label,
                key=f"history_{chat_id}",
                use_container_width=True,
                type=(
                    "primary"
                    if chat_id == st.session_state.active_chat_id
                    else "secondary"
                )
            ):
                open_chat(chat)
                st.rerun()

    st.divider()

    st.markdown(
        '<div class="side-label">Assistant status</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="side-card">
        <div style="font-weight:700;font-size:13px;">
            <span style="color:#d0ff32;">●</span>
            &nbsp; SmartDesk Assistant
        </div>
        <div class="side-muted" style="margin-top:8px;">
            Ready to help with questions, ideas and business tasks.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="side-label">Capabilities</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="side-muted">
        ◈ &nbsp; Website development<br><br>
        ✳ &nbsp; AI solutions and integration<br><br>
        ↗ &nbsp; Workflow automation<br><br>
        ⌘ &nbsp; Technical support<br><br>
        ◉ &nbsp; Business ideas and planning
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("""
    <div class="side-muted">
        <b style="color:#d0ff32;">SMARTDESK AI</b><br>
        Your intelligent business companion.<br><br>
        <span style="color:#777777;">
            Python · Streamlit · Groq AI
        </span>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# MAIN DASHBOARD HERO
# =========================================================

st.markdown("""
<div class="hero">
    <span class="hero-tag">✳ &nbsp; YOUR AI BUSINESS ASSISTANT</span>
    <h1>Ideas into action.<br>
    Powered by AI.</h1>
    <p>
        Explore smarter ways to build websites, improve workflows,
        discover AI solutions and move your business ideas forward.
        One workspace. One conversation. More possibilities.
    </p>
    <div class="hero-footer">
        Ask questions &nbsp; · &nbsp;
        Explore ideas &nbsp; · &nbsp;
        Build something better
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# FEATURE CARDS
# =========================================================

col1, col2, col3 = st.columns(3)

features = [
    ("◈", "KNOWLEDGE", "Business assistance"),
    ("✳", "AI ENGINE", "Connected assistant"),
    ("⌁", "CHAT HISTORY", "Saved conversations"),
]

for col, (icon, label, value) in zip(
    [col1, col2, col3],
    features
):
    with col:
        st.markdown(f"""
        <div class="metric">
            <div class="metric-icon">{icon}</div>
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """, unsafe_allow_html=True)


# =========================================================
# WORKFLOW OVERVIEW
# =========================================================

st.markdown("""
<div class="workflow">
    <div class="workflow-title">A smarter way to work</div>
    <div class="workflow-subtitle">
        From your question to a useful next step.
    </div>
    <div class="flow-grid">
        <div class="flow-step">
            <div class="flow-icon">⌕</div>
            <div class="flow-label">Ask a question</div>
        </div>
        <div class="flow-arrow">→</div>
        <div class="flow-step">
            <div class="flow-icon">✳</div>
            <div class="flow-label">AI processes it</div>
        </div>
        <div class="flow-arrow">→</div>
        <div class="flow-step">
            <div class="flow-icon">↗</div>
            <div class="flow-label">Get your answer</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# CHAT HEADER
# =========================================================

st.markdown(
    '<div class="section-heading">Your conversation</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="section-sub">'
    'Ask a question, choose a suggestion, or continue a saved chat.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# SUGGESTED PROMPTS
# =========================================================

if not st.session_state.messages:

    st.markdown("""
    <div class="welcome-card">
        <div class="welcome-icon">✳</div>
        <div class="welcome-title">
            What are we working on today?
        </div>
        <div class="welcome-text">
            Your next idea starts here.<br>
            Choose a prompt below or type your own question.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="suggestion-label">'
        '✳ &nbsp; TRY THESE PROMPTS'
        '</div>',
        unsafe_allow_html=True
    )

    suggestions = [
        "What services do you offer?",
        "What AI solutions can you help with?",
        "How does a website project work?",
        "How can AI help a small business?",
    ]

    left, right = st.columns(2)

    for index, question in enumerate(suggestions):
        with [left, right][index % 2]:
            if st.button(
                question,
                key=f"suggestion_{index}",
                use_container_width=True
            ):
                st.session_state.pending_question = question
                st.rerun()


# =========================================================
# DISPLAY EXISTING MESSAGES
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(message.get("role", "assistant")):
        st.markdown(message.get("content", ""))

        if message.get("mode"):
            st.caption(message["mode"])


# =========================================================
# CHAT INPUT
# =========================================================

prompt = st.chat_input(
    "Message SmartDesk AI...",
    key="smartdesk_chat_input"
)

if st.session_state.pending_question:
    prompt = st.session_state.pending_question
    st.session_state.pending_question = None


# =========================================================
# AI RESPONSE — EXISTING CORE INTEGRATION
# =========================================================

if prompt and prompt.strip():

    prompt = prompt.strip()

    # Capture the previous conversation before appending
    # the new user message, matching the existing core call.
    conversation_history = [
        dict(message)
        for message in st.session_state.messages
    ]

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    response = ""
    mode = "AI Assistant"

    with st.chat_message("assistant"):

        with st.spinner("SmartDesk is thinking..."):

            try:
                result = answer_question(
                    prompt,
                    use_web=False,
                    conversation_history=conversation_history
                )

                response = result[0]

                mode = (
                    result[2]
                    if len(result) > 2
                    else "AI Assistant"
                )

            except Exception as exc:

                response = (
                    "I couldn't prepare a response right now. "
                    "Please check your AI configuration and try again."
                )

                mode = "Response error"

                st.error(str(exc))

        st.markdown(response)
        st.caption(mode)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "mode": mode
    })

    # Persist the conversation after every completed response.
    save_current_chat()
