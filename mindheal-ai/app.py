import streamlit as st

from core.world_clock import render_world_clock

# Friendly page names, with discussion and specialist tools grouped under HEALER.
st.set_page_config(page_title="MindHeal AI", page_icon=None, layout="wide")

pages = {
    "": [
        st.Page("pages/0_Mind_Heal.py", title="Mind Heal", default=True),
        st.Page("pages/5_Music_and_Relaxation.py", title="Relax Music"),
        st.Page("pages/5_Upload_PDF.py", title="Upload PDF"),
        st.Page("pages/8_Settings.py", title="Settings"),
    ],
    "HEALER": [
        st.Page("pages/1_Chat.py", title="General Discussion"),
        st.Page("pages/2_Mental_Discomforts.py", title="Mental Discomforts"),
        st.Page("pages/3_Addictions.py", title="Addictions"),
        st.Page("pages/4_Fears.py", title="Fears"),
    ],
}

selected_page = st.navigation(pages, position="sidebar")

# Render the local IP-based clock globally so it appears on every page.
with st.sidebar:
    render_world_clock()

selected_page.run()
