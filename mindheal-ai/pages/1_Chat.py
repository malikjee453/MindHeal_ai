import streamlit as st
from pathlib import Path
import streamlit.components.v1 as components

from agents.orchestrator import respond
from core.session import init_session
from core.ui import render_header
from core import personal_memory as memory
from core.groq_client import chat as llm_chat, transcribe_audio

# Register the browser voice widget defensively so a component-path or
# registry issue cannot crash the entire Chat page.
try:
    VOICE_COMPONENT = components.declare_component(
        "mindheal_browser_voice",
        path=str(Path(__file__).resolve().parents[1] / "voice_component"),
    )
    VOICE_COMPONENT_READY = True
except Exception as voice_component_error:
    VOICE_COMPONENT = None
    VOICE_COMPONENT_READY = False
    VOICE_COMPONENT_ERROR = f"{type(voice_component_error).__name__}: {voice_component_error}"


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
        src:
            url("https://raw.githubusercontent.com/malikjee453/MindHeal_ai/main/mindheal-ai/static/JameelNooriNastaleeq.ttf") format("truetype"),
            url("/app/static/JameelNooriNastaleeq.ttf?v=3") format("truetype");
        font-weight: 400;
        font-style: normal;
        font-display: swap;
    }

    .urdu-response {
        font-family: "JameelNooriNastaleeq", "Jameel Noori Nastaleeq", serif !important;
        direction: rtl !important;
        text-align: right !important;
        font-size: 24px !important;
        line-height: 2.2 !important;
        unicode-bidi: plaintext !important;
    }

    .urdu-response * {
        font-family: "JameelNooriNastaleeq", "Jameel Noori Nastaleeq", serif !important;
    }

    /* Compact private-account sign-in so it takes less vertical space. */
    .st-key-mindheal_login_form {
        padding: 0.65rem 0.8rem !important;
        margin-top: 0.4rem !important;
        margin-bottom: 0.4rem !important;
    }
    .st-key-mindheal_login_form [data-testid="stTextInput"] {
        margin-bottom: 0.15rem !important;
    }
    .st-key-mindheal_login_form [data-testid="stWidgetLabel"] {
        margin-bottom: 0.15rem !important;
    }
    .st-key-mindheal_login_form input {
        min-height: 2.35rem !important;
    }
    .st-key-mindheal_login_form [data-testid="stFormSubmitButton"] button {
        min-height: 2.2rem !important;
        padding: 0.35rem 0.8rem !important;
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

# General chat works without an account. Saving memory is optional.
if not memory.logged_in():
    # Keep account controls collapsed until the visitor chooses Sign in.
    if "mh_show_account_panel" not in st.session_state:
        st.session_state.mh_show_account_panel = False

    if not st.session_state.mh_show_account_panel:
        if st.button("Sign in", key="mh_open_account_panel", type="primary"):
            st.session_state.mh_show_account_panel = True
            st.rerun()
    else:
        st.subheader("Optional private account")
        st.caption(
            "General chat works without an account. Create a nickname and password "
            "only if you want to save memory and progress. No email address is requested."
        )
        if st.button("Close", key="mh_close_account_panel"):
            st.session_state.mh_show_account_panel = False
            st.rerun()

        if not memory.configured():
            st.warning("Private accounts need Supabase credentials. General chat still works without them.")
            st.code(
                'SUPABASE_URL = "https://YOUR_PROJECT_REF.supabase.co"\\n'
                'SUPABASE_ANON_KEY = "YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY"',
                language="toml",
            )
        else:
            login_tab, signup_tab = st.tabs(["Sign in", "Create account"])
            with login_tab:
                with st.form("mindheal_login_form"):
                    login_left, login_right = st.columns(2, gap="small")
                    with login_left:
                        login_nickname = st.text_input("Nickname", key="mh_login_nickname", max_chars=24)
                    with login_right:
                        login_password = st.text_input("Password", type="password", key="mh_login_password")
                    login_submit = st.form_submit_button("Sign in", type="primary")
                if login_submit:
                    ok, data = memory.sign_in(login_nickname, login_password)
                    if ok:
                        auth_session = memory.session_parts(data)
                        st.session_state.mindheal_access_token = auth_session["access_token"]
                        st.session_state.mindheal_refresh_token = auth_session["refresh_token"]
                        st.session_state.mindheal_user_id = auth_session["user_id"]
                        st.session_state.mindheal_nickname = login_nickname.strip()
                        if st.session_state.mindheal_access_token and st.session_state.mindheal_user_id:
                            profile = memory.load_profile() or {}
                            st.session_state.mindheal_memory_enabled = bool(profile.get("memory_enabled", False))
                            st.success("Signed in. Background memory is still off until you enable it in Settings.")
                            st.rerun()
                        else:
                            st.error("Sign-in did not return a session. Check Supabase Auth settings.")
                    else:
                        st.error(str(data))
            with signup_tab:
                with st.form("mindheal_signup_form"):
                    signup_nickname = st.text_input(
                        "Choose a nickname (3–24 letters, numbers, underscores)",
                        key="mh_signup_nickname",
                        max_chars=24,
                    )
                    signup_password = st.text_input(
                        "Create password (at least 8 characters)",
                        type="password",
                        key="mh_signup_password",
                    )
                    signup_confirm = st.text_input(
                        "Confirm password", type="password", key="mh_signup_confirm"
                    )
                    signup_submit = st.form_submit_button("Create account")
                if signup_submit:
                    if signup_password != signup_confirm:
                        st.error("The passwords do not match.")
                    elif len(signup_password) < 8:
                        st.error("Please use a password with at least 8 characters.")
                    elif not signup_nickname.strip():
                        st.error("Please choose a nickname.")
                    else:
                        ok, data = memory.sign_up(signup_nickname, signup_password)
                        if ok:
                            auth_session = memory.session_parts(data)
                            if auth_session["access_token"] and auth_session["user_id"]:
                                st.session_state.mindheal_access_token = auth_session["access_token"]
                                st.session_state.mindheal_refresh_token = auth_session["refresh_token"]
                                st.session_state.mindheal_user_id = auth_session["user_id"]
                                st.session_state.mindheal_nickname = signup_nickname.strip()
                                st.session_state.mindheal_memory_enabled = False
                                memory.save_profile(
                                    display_name=signup_nickname.strip(),
                                    memory_enabled=False,
                                    memory_summary="",
                                )
                                st.success("Account created. Memory is off by default; enable it in Settings when ready.")
                                st.rerun()
                            else:
                                st.error(
                                    "Supabase did not return a session. In Supabase Auth settings, "
                                    "disable email confirmations because no real email is collected."
                                )
                        else:
                            st.error(str(data))
elif memory.logged_in():
    account_profile = memory.load_profile() or {}
    account_nickname = st.session_state.get("mindheal_nickname") or account_profile.get("display_name", "")
    memory_status = "on" if account_profile.get("memory_enabled") else "off"
    st.caption(f"Private account · {account_nickname or 'signed in'} · background memory {memory_status}")


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

    /* Overlay the microphone inside the left end of the bottom-docked chat composer. */
    [data-testid="stChatInput"] textarea {
        padding-left: 3.6rem !important;
        padding-right: 3.5rem !important;
    }
    div[data-testid="stCustomComponent"] {
        position: fixed !important;
        left: max(17.5rem, calc((100vw - 48rem) / 2 + 1.5rem)) !important;
        bottom: 4.45rem !important;
        width: 2.8rem !important;
        height: 2.8rem !important;
        overflow: visible !important;
        z-index: 1002 !important;
        background: transparent !important;
    }
    div[data-testid="stCustomComponent"] iframe {
        width: 2.8rem !important;
        height: 2.8rem !important;
        border: 0 !important;
        background: transparent !important;
    }
    @media (max-width: 640px) {
        [data-testid="stChatInput"] textarea {
            padding-left: 3.3rem !important;
            padding-right: 3.5rem !important;
        }
        div[data-testid="stCustomComponent"] {
            left: 1.35rem !important;
            bottom: 4.2rem !important;
            width: 2.6rem !important;
            height: 2.6rem !important;
        }
        div[data-testid="stCustomComponent"] iframe {
            width: 2.6rem !important;
            height: 2.6rem !important;
        }
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
# Chat composer with microphone button
# ---------------------------------------------------------

# Browser speech recognition listens after one tap and automatically finishes after silence.
prompt = st.chat_input("What's on your mind?")
if VOICE_COMPONENT_READY:
    voice_text = VOICE_COMPONENT(
        language="ur-PK" if str(st.session_state.get("language", "English")).lower().startswith("urdu") else "en-US",
        key="mindheal_browser_voice",
        default=None,
    )
    if voice_text and voice_text != st.session_state.get("_mindheal_last_voice_transcript"):
        st.session_state["_mindheal_last_voice_transcript"] = voice_text
        st.session_state["_mindheal_voice_prompt_pending"] = voice_text
        st.rerun()
else:
    st.warning("Voice chat could not initialize. Details: " + VOICE_COMPONENT_ERROR)
    st.caption("You can still type a message below while this is fixed.")

if st.session_state.get("_mindheal_voice_prompt_pending"):
    prompt = st.session_state.pop("_mindheal_voice_prompt_pending")

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
