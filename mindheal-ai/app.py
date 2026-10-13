import streamlit as st

# Explicit navigation lets us use friendly labels instead of filenames.
st.set_page_config(page_title="MindHeal AI", page_icon=None, layout="wide")

pages = [
    st.Page("pages/0_Mind_Heal.py", title="Mind Heal", default=True),
    st.Page("pages/1_Chat.py", title="Let's Talk"),
    st.Page("pages/2_Mental_Discomforts.py", title="Mental Discomforts"),
    st.Page("pages/3_Addictions.py", title="Addictions"),
    st.Page("pages/4_Fears.py", title="Fears"),
    st.Page("pages/5_Music_and_Relaxation.py", title="Relax Music"),
    st.Page("pages/5_Upload_PDF.py", title="Upload PDF"),
    st.Page("pages/8_Settings.py", title="Settings"),
]

selected_page = st.navigation(pages, position="sidebar")
selected_page.run()
