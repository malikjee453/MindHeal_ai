import streamlit as st
import pandas as pd
from core.session import init_session
from core import personal_memory as memory

st.markdown("""
<style>
h1, h2, h3, h4, h5, h6,
[data-testid="stHeading"] h1, [data-testid="stHeading"] h2,
[data-testid="stHeading"] h3, [data-testid="stHeading"] h4,
[data-testid="stHeading"] h5, [data-testid="stHeading"] h6,
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
.stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
    color: #173B2D !important;
    -webkit-text-fill-color: #173B2D !important;
}
</style>
""", unsafe_allow_html=True)

init_session()
st.title("⚙️ Settings")
st.session_state.tone = st.selectbox(
    "Conversation tone",
    ["Warm and practical", "Gentle", "Direct and structured"],
    index=["Warm and practical", "Gentle", "Direct and structured"].index(
        st.session_state.get("tone", "Warm and practical")
    ) if st.session_state.get("tone", "Warm and practical") in ["Warm and practical", "Gentle", "Direct and structured"] else 0,
)

st.divider()
st.subheader("Private account & background memory")
st.caption("Memory is optional. Your saved conversations and progress are tied to your account. MindHeal does not train a new model on them.")

if not memory.configured():
    st.warning("Account storage is not configured yet. Add SUPABASE_URL and SUPABASE_ANON_KEY to Streamlit Cloud Secrets, then run the SQL in supabase_mindheal_memory.sql in your Supabase SQL Editor.")
elif not memory.logged_in():
    st.info("Sign in or create an account from the Chat page to manage private memory.")
else:
    profile = memory.load_profile() or {}
    with st.form("profile_form"):
        display_name = st.text_input("What should MindHeal call you?", value=profile.get("display_name", ""))
        memory_enabled = st.checkbox(
            "Enable background memory",
            value=bool(profile.get("memory_enabled", False)),
            help="When enabled, MindHeal saves conversation turns and a short summary for future chats. When disabled, new conversation turns are not saved.",
        )
        consent = st.form_submit_button("Save memory settings")
    if consent:
        memory.save_profile(display_name=display_name.strip()[:80], memory_enabled=memory_enabled)
        st.session_state.mindheal_memory_enabled = memory_enabled
        st.success("Your preferences have been saved.")
        st.rerun()

    st.caption("You can turn memory off at any time. Turning it off stops future conversation saving; it does not delete history already stored.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Delete saved conversation memory", use_container_width=True):
            memory.clear_memory()
            st.success("Saved conversation turns and summary deleted.")
    with c2:
        if st.button("Sign out", use_container_width=True):
            for key in ("mindheal_access_token", "mindheal_refresh_token", "mindheal_user_id", "mindheal_email", "mindheal_memory_enabled"):
                st.session_state.pop(key, None)
            st.success("You have been signed out.")
            st.rerun()

st.divider()
st.subheader("Optional progress check-in")
st.write("Record how you feel today. This is self-reported reflection, not a diagnosis.")
if memory.logged_in():
    with st.form("progress_form"):
        mood = st.slider("Mood today", 1, 10, 5, help="1 = very low, 10 = very good")
        stress = st.slider("Stress today", 1, 10, 5, help="1 = very low, 10 = very high")
        note = st.text_input("Optional note", placeholder="Anything you want to remember")
        save_checkin = st.form_submit_button("Save check-in")
    if save_checkin:
        if memory.save_progress(mood, stress, note):
            st.success("Check-in saved to your private account.")
            st.rerun()
        else:
            st.error("Could not save the check-in. Check your Supabase setup and policies.")

    progress = memory.get_progress(limit=60)
    if progress:
        df = pd.DataFrame(progress)
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
        st.line_chart(df.set_index("created_at")[["mood", "stress"]])
        st.caption("Mood and stress are your own ratings over time. Higher mood ratings mean better mood; higher stress ratings mean more stress.")
        if len(df) >= 2:
            first, latest = df.iloc[0], df.iloc[-1]
            mood_delta = int(latest["mood"]) - int(first["mood"])
            stress_delta = int(latest["stress"]) - int(first["stress"])
            st.write(f"Since your first saved check-in: mood {mood_delta:+d} points; stress {stress_delta:+d} points.")
    else:
        st.caption("Your progress chart will appear after you save at least one check-in.")
else:
    st.caption("Sign in on the Chat page to save private check-ins and compare them over time.")

if st.button("Clear current chat"):
    st.session_state.messages = []
    st.success("Current chat cleared.")
