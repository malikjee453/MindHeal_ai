import streamlit as st

from agents.orchestrator import respond
from core.session import init_session
from core.ui import render_header
from core import personal_memory as memory
from core.groq_client import chat as llm_chat


# =========================================================
# URDU FONT STYLING
# =========================================================

st.markdown(
    """
    <style>

/* Match the Chat page heading to the main MindHeal title color. */
h1, h2, h3, h4, h5, h6,
[data-testid="stHeading"] h1,
[data-testid="stHeading"] h2,
[data-testid="stHeading"] h3,
[data-testid="stHeading"] h4,
[data-testid="stHeading"] h5,
[data-testid="stHeading"] h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
.stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
    color: #173B2D !important;
    -webkit-text-fill-color: #173B2D !important;
}

    @font-face {
        font-family: "JameelNooriNastaleeq";
        src: url("/app/static/JameelNooriNastaleeq.ttf")
             format("truetype");
        font-weight: normal;
        font-style: normal;
    }

    .urdu-response {
        font-family: "JameelNooriNastaleeq", serif !important;
        direction: rtl !important;
        text-align: right !important;
        font-size: 24px !important;
        line-height: 2.2 !important;
        unicode-bidi: plaintext !important;
    }

    .urdu-response * {
        font-family: "JameelNooriNastaleeq", serif !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# Detect Urdu
# ---------------------------------------------------------

def contains_urdu(text):
    urdu_chars = (
        "اآبپتٹثجچحخدڈذرڑزژسشصضطظعغفقکگلمنںوہھءیے"
    )

    return any(char in text for char in urdu_chars)


# ---------------------------------------------------------
# Initialize app
# ---------------------------------------------------------

init_session()

# Private account sign-in. Chat still works without an account; persistence is opt-in.
if memory.configured() and not memory.logged_in():
    with st.expander("Sign in for private background memory", expanded=False):
        st.caption("Create a private account to keep your name, opt-in conversation memory, and progress across visits.")
        login_tab, signup_tab = st.tabs(["Sign in", "Create account"])
        with login_tab:
            with st.form("mindheal_login_form"):
                login_email = st.text_input("Email", key="mh_login_email")
                login_password = st.text_input("Password", type="password", key="mh_login_password")
                login_submit = st.form_submit_button("Sign in", type="primary")
            if login_submit:
                ok, data = memory.sign_in(login_email, login_password)
                if ok:
                    st.session_state.mindheal_access_token = data.get("access_token")
                    st.session_state.mindheal_refresh_token = data.get("refresh_token")
                    st.session_state.mindheal_user_id = (data.get("user") or {}).get("id")
                    st.session_state.mindheal_email = login_email.strip()
                    if st.session_state.mindheal_access_token and st.session_state.mindheal_user_id:
                        profile = memory.load_profile() or {}
                        st.session_state.mindheal_memory_enabled = bool(profile.get("memory_enabled", False))
                        st.success("Signed in. Background memory remains off until you enable it in Settings.")
                        st.rerun()
                    else:
                        st.error("Sign-in returned no session. Please try again.")
                else:
                    st.error(str(data))
        with signup_tab:
            with st.form("mindheal_signup_form"):
                signup_email = st.text_input("Email address", key="mh_signup_email")
                signup_password = st.text_input("Password (at least 8 characters)", type="password", key="mh_signup_password")
                signup_confirm = st.text_input("Confirm password", type="password", key="mh_signup_confirm")
                signup_submit = st.form_submit_button("Create account")
            if signup_submit:
                if signup_password != signup_confirm:
                    st.error("The passwords do not match.")
                elif len(signup_password) < 8:
                    st.error("Please use a password with at least 8 characters.")
                else:
                    ok, data = memory.sign_up(signup_email, signup_password)
                    if ok:
                        if data.get("access_token") and (data.get("user") or {}).get("id"):
                            st.session_state.mindheal_access_token = data.get("access_token")
                            st.session_state.mindheal_refresh_token = data.get("refresh_token")
                            st.session_state.mindheal_user_id = data["user"]["id"]
                            st.session_state.mindheal_email = signup_email.strip()
                            st.session_state.mindheal_memory_enabled = False
                            memory.save_profile(display_name="", memory_enabled=False, memory_summary="")
                            st.success("Account created. Memory is off by default; enable it in Settings when ready.")
                            st.rerun()
                        else:
                            st.success("Account request received. Check your email to confirm the account, then sign in here.")
                    else:
                        st.error(str(data))
elif memory.logged_in():
    account_profile = memory.load_profile() or {}
    st.caption("Signed in" + (f" as {account_profile.get('display_name')}" if account_profile.get("display_name") else " to your private MindHeal account") + (" · background memory on" if account_profile.get("memory_enabled") else " · background memory off"))

render_header(
    "MindHeal AI",
    "Supportive conversations",
    "Engr. Mubashir Malik",
)


# ---------------------------------------------------------
# Compact answer-length tabs
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    /* Force the answer-length segmented control to use MindHeal green,
       overriding Streamlit's default red primary theme. */
    div[data-testid="stSegmentedControl"] button,
    div[data-testid="stSegmentedControl"] button *,
    div[data-testid="stSegmentedControl"] [role="radio"],
    div[data-testid="stSegmentedControl"] [role="radio"] * {
        color: #2F7655 !important;
        border-color: #2F7655 !important;
        min-height: 30px !important;
        padding-top: 3px !important;
        padding-bottom: 3px !important;
        font-size: 0.82rem !important;
        line-height: 1.1 !important;
        --primary-color: #2F7655 !important;
        --primary-color-light: #E8F1EC !important;
    }
    div[data-testid="stSegmentedControl"] button[aria-pressed="true"],
    div[data-testid="stSegmentedControl"] button[aria-checked="true"],
    div[data-testid="stSegmentedControl"] button[data-checked="true"],
    div[data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"] {
        background: #2F7655 !important;
        color: #FFFFFF !important;
        border-color: #2F7655 !important;
    }
    div[data-testid="stSegmentedControl"] button[aria-pressed="true"] *,
    div[data-testid="stSegmentedControl"] button[aria-checked="true"] *,
    div[data-testid="stSegmentedControl"] button[data-checked="true"] *,
    div[data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"] * {
        color: #FFFFFF !important;
    }
    div[data-testid="stSegmentedControl"] button:hover,
    div[data-testid="stSegmentedControl"] [role="radio"]:hover {
        border-color: #245C42 !important;
        color: #245C42 !important;
    }
    div[data-testid="stSegmentedControl"] [data-testid="stMarkdownContainer"] p {
        font-size: 0.82rem !important;
        margin: 0 !important;
    }

    /* Clearly outline the chat input box. */
    [data-testid="stChatInput"] {
        border: 1.5px solid #2F7655 !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border: 2px solid #2F7655 !important;
        box-shadow: 0 0 0 2px rgba(47, 118, 85, 0.12) !important;
    }
    [data-testid="stChatInput"] textarea {
        border: none !important;
        box-shadow: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Keep answer controls left-aligned with the main page title.
answer_length = st.segmented_control(
    "Answer length",
    options=["Short Answer", "Detailed Answer"],
    default="Short Answer",
    label_visibility="collapsed",
    key="answer_length",
    help="Choose how much detail MindHeal should include in new replies.",
)

if answer_length is None:
    answer_length = "Short Answer"

# Language selector directly below the answer-length tabs, left-aligned.
language_options = ["English", "Urdu"]
current_language = st.session_state.get("language", "English")
if current_language not in language_options:
    current_language = "English"
# Match the language dropdown width to the answer-length buttons.
language_col, _language_spacer = st.columns([2, 5], gap="small")
with language_col:
    st.session_state.language = st.selectbox(
        "Response language",
        options=language_options,
        index=language_options.index(current_language),
        key="chat_response_language",
        label_visibility="visible",
    )

# ---------------------------------------------------------
# Restore recent saved conversation only when the user opted in.
# ---------------------------------------------------------

if memory.logged_in() and st.session_state.get("mindheal_memory_enabled") and not st.session_state.messages:
    saved_turns = memory.recent_turns(limit=12)
    st.session_state.messages = [{"role": row["role"], "content": row["content"]} for row in saved_turns if row.get("role") in ("user", "assistant")]

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        content = message["content"]

        if (
            message["role"] == "assistant"
            and contains_urdu(content)
        ):
            st.markdown(
                f'<div class="urdu-response">{content}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(content)


# ---------------------------------------------------------
# Chat input
# ---------------------------------------------------------

prompt = st.chat_input("What's on your mind?")


if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # -----------------------------------------------------
    # Generate response
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        try:

            with st.spinner("Thinking..."):
                background_memory = ""
                if memory.logged_in() and st.session_state.get("mindheal_memory_enabled"):
                    profile = memory.load_profile() or {}
                    background_memory = profile.get("memory_summary", "")
                    display_name = profile.get("display_name", "").strip()
                    if display_name:
                        background_memory = f"User prefers to be called {display_name}. " + background_memory
                answer, sources, route = respond(
                    prompt,
                    memory_context=background_memory,
                    response_style=(
                        "detailed"
                        if answer_length == "Detailed Answer"
                        else "short"
                    ),
                    response_language=st.session_state.language,
                )

        except Exception as e:

            answer = (
                "⚠️ I couldn't complete that request.\n\n"
                f"`{type(e).__name__}: {e}`"
            )

            sources = []

        # -------------------------------------------------
        # Display response
        # -------------------------------------------------

        if contains_urdu(answer):

            st.markdown(
                f'<div class="urdu-response">{answer}</div>',
                unsafe_allow_html=True,
            )

        else:

            st.markdown(answer)

        # -------------------------------------------------
        # RAG sources
        # -------------------------------------------------

        if sources:

            with st.expander("Knowledge sources"):

                for source in sources:

                    st.caption(
                        f"{source['filename']} — "
                        f"chunk {source['chunk_id']} "
                        f"(similarity {source['score']})"
                    )

    # -----------------------------------------------------
    # Save response
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    # Persistent storage is strictly opt-in. Summarize in the background every few turns.
    if memory.logged_in() and st.session_state.get("mindheal_memory_enabled"):
        memory.save_turn("user", prompt)
        memory.save_turn("assistant", answer)
        saved = memory.recent_turns(limit=120)
        if len(saved) >= 6 and len(saved) % 6 == 0:
            profile = memory.load_profile() or {}
            transcript = "\n".join(f"{row['role']}: {row['content']}" for row in saved[-12:])
            try:
                summary = llm_chat([
                    {"role": "system", "content": "Create a brief, factual private memory summary for continuity in an emotional-support app. Keep only user-stated name/preferences, ongoing goals, recurring themes, helpful strategies, and meaningful changes over time. Do not diagnose or infer sensitive traits. Do not include unnecessary identifying details. Maximum 180 words. If uncertain, say so."},
                    {"role": "user", "content": f"Existing summary:\n{profile.get('memory_summary','')}\n\nRecent conversation:\n{transcript}\n\nWrite an updated concise summary."}
                ], temperature=0.2)
                memory.save_profile(memory_summary=summary[:3000])
            except Exception:
                pass
