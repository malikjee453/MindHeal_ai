import streamlit as st

from agents.orchestrator import respond
from core.session import init_session, VOICE_COMPONENT, VOICE_COMPONENT_READY, VOICE_COMPONENT_ERROR
from core.ui import render_header
from core import personal_memory as memory
from core.groq_client import chat as llm_chat, transcribe_audio



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

    /* Single full-width custom chat composer. */
    [data-testid="stChatInput"] { display: none !important; }
    div[data-testid="stCustomComponent"] {
        position: fixed !important;
        left: max(17.5rem, calc((100vw - 48rem) / 2 + 1.5rem)) !important;
        bottom: 4.45rem !important;
        width: min(48rem, calc(100vw - 20rem)) !important;
        height: 62px !important; overflow: visible !important;
        z-index: 1002 !important; background: transparent !important;
    }
    div[data-testid="stCustomComponent"] iframe {
        width: 100% !important; height: 62px !important;
        border: 0 !important; background: transparent !important;
    }
    @media (max-width: 640px) {
        div[data-testid="stCustomComponent"] {
            left: 0.75rem !important; bottom: 4.2rem !important;
            width: calc(100vw - 1.5rem) !important; height: 62px !important;
        }
        div[data-testid="stCustomComponent"] iframe { width: 100% !important; height: 62px !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Keep answer controls left-aligned with the main page title.
answer_length = st.segmented_control(
    "Answer length",
    options=["Short Answer", "Detailed Answer", "Blunt Answer"],
    default="Short Answer",
    label_visibility="collapsed",
    key="answer_length",
    help="Choose concise, detailed, or direct reality-based answers with practical remedies.",
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
# Flexible answer rendering and interactive quiz/editor controls
# ---------------------------------------------------------
import re
import html

def _requested_editable(user_text):
    request = str(user_text or "").lower()
    return any(term in request for term in (
        "editable", "let me edit", "edit this answer", "edit the response",
        "make changes to this", "editable format",
    ))

def _requested_quiz(user_text):
    request = str(user_text or "").lower()
    return any(term in request for term in (
        "mcq", "multiple choice", "multiple-choice", "quiz", "gk questions",
        "gk mcqs", "test me with questions",
    ))

def _parse_mcqs(content):
    """Parse MCQs whether options are on separate lines or run together."""
    text = html.unescape(str(content or "")).replace("\r", "")
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = text.replace("\\\n", "\n").replace("&#x20;", " ").replace("&nbsp;", " ")
    questions = []
    current = None

    def add_options(question, fragment):
        # Split A) / B) / C) / D) markers even when the model puts them on one line.
        matches = list(re.finditer(r"(?<![A-Za-z])([A-Da-d])[).、:-]\s*", fragment))
        if len(matches) < 2:
            return question, fragment
        question_text = fragment[:matches[0].start()].strip(" :-—")
        if question_text and not question["question"]:
            question["question"] = question_text
        for idx, match in enumerate(matches):
            label = match.group(1).upper()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(fragment)
            option_text = fragment[match.end():end].strip().rstrip("\\").strip()
            if option_text:
                question["options"].append((label, option_text))
        return question, ""

    for raw_line in text.splitlines():
        line = re.sub(r"<[^>]+>", "", raw_line).strip()
        line = re.sub(r"^\s*(?:[-*]\s*)", "", line)
        qmatch = re.match(r"^(?:#{1,6}\s*)?(?:Q(?:uestion)?\s*)?(\d{1,2})[.)、:-]\s*(.+)$", line, re.I)
        if qmatch:
            if current and len(current["options"]) >= 2:
                questions.append(current)
            current = {"question": "", "options": []}
            fragment = qmatch.group(2).strip().strip("*")
            current, remainder = add_options(current, fragment)
            if remainder:
                current["question"] = remainder
            continue

        if current:
            current, remainder = add_options(current, line)
            if remainder:
                omatch = re.match(r"^([A-Da-d])[).、:-]\s*(.+)$", remainder)
                if omatch:
                    current["options"].append((omatch.group(1).upper(), omatch.group(2).strip().rstrip("\\").strip()))
                elif len(current["options"]) >= 2:
                    questions.append(current)
                    current = None
                elif not current["question"]:
                    current["question"] = remainder

    if current and len(current["options"]) >= 2:
        questions.append(current)

    unique, seen = [], set()
    for question in questions:
        question["options"] = question["options"][:4]
        key = question["question"].lower()
        if len(question["options"]) >= 2 and key not in seen:
            seen.add(key)
            unique.append(question)
    return unique

def render_chat_answer(content, user_text="", key_suffix="answer"):
    text = str(content or "")
    if _requested_editable(user_text):
        st.caption("Edit this response directly. Preview the formatting or download your edited version.")
        edited = st.text_area("Editable response", value=text, height=300, key="mh_edit_" + key_suffix)
        with st.expander("Preview formatted response", expanded=True):
            st.markdown(edited)
        st.download_button("Download edited response", data=edited, file_name="mindheal_response.md", mime="text/markdown", key="mh_download_" + key_suffix)
        return

    if contains_urdu(text):
        st.markdown(f'<div class="urdu-response">{text}</div>', unsafe_allow_html=True)
    else:
        st.markdown(text)

    # Render interactive controls whenever this response contains MCQs, not only
    # when the user's wording matches a trigger. This also handles Urdu requests.
    questions = _parse_mcqs(text)
    if questions and (_requested_quiz(user_text) or len(questions) > 0):
        st.markdown("#### Select your answers")
        chosen = {}
        for number, question in enumerate(questions, 1):
            options = [f"{letter}. {label}" for letter, label in question["options"]]
            chosen[number] = st.radio(
                question["question"],
                options,
                index=None,
                key=f"mh_mcq_{key_suffix}_{number}",
            )
        if st.button("Submit answers", key=f"mh_submit_quiz_{key_suffix}"):
            answers = {str(n): (v.split(".", 1)[0] if v else None) for n, v in chosen.items()}
            st.session_state[f"mh_quiz_submitted_{key_suffix}"] = answers
            st.success("Your selections are recorded. Ask MindHeal to check your answers and explain them.")
    elif _requested_quiz(user_text):
        st.info("I couldn't detect options in this response. Ask for each option on a separate line labelled A), B), C), and D).")

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
            render_chat_answer(content, key_suffix="history_" + str(len(st.session_state.messages)))


# ---------------------------------------------------------
# Unified chat composer: microphone and text input stay together.
# Voice automatically submits after the browser detects the end of speech.
# ---------------------------------------------------------

# Keep a real Streamlit chat input as a reliable typed-message fallback.
# The browser component remains responsible for microphone capture and speech playback.
prompt = st.chat_input("Message MindHeal AI…")
if VOICE_COMPONENT_READY:
    _speak_latest = bool(st.session_state.get("_mindheal_speak_latest", False))
    _latest_answer = ""
    if _speak_latest and st.session_state.messages:
        _last_message = st.session_state.messages[-1]
        if _last_message.get("role") == "assistant":
            _latest_answer = str(_last_message.get("content", ""))
    composer_result = VOICE_COMPONENT(
        language="ur-PK" if str(st.session_state.get("language", "English")).lower().startswith("urdu") else "en-US",
        clearToken=len(st.session_state.messages),
        speakText=_latest_answer,
        speakId=str(len(st.session_state.messages)) if _latest_answer else "",
        speakLanguage="ur-PK" if str(st.session_state.get("language", "English")).lower().startswith("urdu") else "en-US",
        # Recreate the component after each completed turn so stale component values cannot block later sends.
        key=f"mindheal_browser_voice_{len(st.session_state.messages)}",
        default=None,
    )
    if _speak_latest:
        st.session_state["_mindheal_speak_latest"] = False
    if isinstance(composer_result, dict):
        composer_id = str(composer_result.get("id", ""))
        composer_text = str(composer_result.get("text", "")).strip()
        is_new_chat = (
            composer_result.get("action") == "new_chat"
            or composer_text.lower() == "/newchat"
            or composer_id.startswith("new-")
        )
        if is_new_chat and composer_id != st.session_state.get("_mindheal_last_new_chat_id"):
            # Clear the current UI session first; persistent memory cleanup is best-effort.
            st.session_state["_mindheal_last_new_chat_id"] = composer_id
            st.session_state.messages = []
            st.session_state["_mindheal_speak_latest"] = False
            st.session_state.pop("_mindheal_last_composer_id", None)
            st.session_state.pop("_mindheal_last_voice_transcript", None)
            if memory.logged_in():
                try:
                    memory.clear_memory()
                except Exception:
                    pass
            st.rerun()
        if composer_text and composer_text.lower() != "/newchat" and composer_id and composer_id != st.session_state.get("_mindheal_last_composer_id"):
            st.session_state["_mindheal_last_composer_id"] = composer_id
            # Prefer an explicitly typed chat message; otherwise accept the component transcript.
            if not prompt:
                prompt = composer_text
    elif isinstance(composer_result, str) and composer_result.strip():
        # Backward compatibility with an older version of the voice component.
        if composer_result != st.session_state.get("_mindheal_last_voice_transcript"):
            st.session_state["_mindheal_last_voice_transcript"] = composer_result
            if not prompt:
                prompt = composer_result
else:
    st.caption("Voice composer is temporarily unavailable. You can type a message below.")

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
                # Include recent turns from this browser session so follow-up
                # questions such as "why?" or "what about the first option?" make sense.
                # The current prompt is already appended to messages, so exclude it here.
                prior_messages = st.session_state.messages[:-1][-10:]
                conversation_context = "\n".join(
                    f"{item['role']}: {item['content']}"
                    for item in prior_messages
                    if item.get("role") in ("user", "assistant")
                )

                answer, sources, route = respond(
                    prompt,
                    memory_context=background_memory,
                    conversation_context=conversation_context,
                    response_style=(
                        "detailed"
                        if answer_length == "Detailed Answer"
                        else "blunt"
                        if answer_length == "Blunt Answer"
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

        render_chat_answer(answer, user_text=prompt, key_suffix="turn_" + str(len(st.session_state.messages)))

        # -------------------------------------------------
        # RAG sources
        # -------------------------------------------------

        if sources:

            with st.expander("Knowledge sources"):

                for source in sources:
                    if source.get("type") == "web":
                        title = source.get("title", "Web result")
                        url = source.get("url", "")
                        snippet = source.get("snippet", "")
                        if url:
                            st.markdown(f"- [{title}]({url})")
                        else:
                            st.markdown(f"- {title}")
                        if snippet:
                            st.caption(snippet)
                    else:
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

    # Save turns only after the reply is complete. Avoid a second LLM call here:
    # that extra summarization request could make the third exchange appear stuck.
    if memory.logged_in() and st.session_state.get("mindheal_memory_enabled"):
        try:
            memory.save_turn("user", prompt)
            memory.save_turn("assistant", answer)
        except Exception:
            # Chat should remain usable even if optional persistent memory is unavailable.
            pass

    # Trigger a fresh component render so the latest reply is spoken once.
    st.session_state["_mindheal_speak_latest"] = True
    st.rerun()
