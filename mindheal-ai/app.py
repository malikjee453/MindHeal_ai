import streamlit as st

# Friendly navigation labels and a single HEALER dropdown for focused support.
st.set_page_config(page_title="MindHeal AI", page_icon=None, layout="wide")

home = st.Page("pages/0_Mind_Heal.py", title="Mind Heal", default=True)
chat = st.Page("pages/1_Chat.py", title="Let's Talk")
discomforts = st.Page("pages/2_Mental_Discomforts.py", title="Mental Discomforts")
addictions = st.Page("pages/3_Addictions.py", title="Addictions")
fears = st.Page("pages/4_Fears.py", title="Fears")
music = st.Page("pages/5_Music_and_Relaxation.py", title="Relax Music")
pdf = st.Page("pages/5_Upload_PDF.py", title="Upload PDF")
settings = st.Page("pages/8_Settings.py", title="Settings")

# Keep the three specialist pages registered with Streamlit, but visually
# group them under HEALER using a compact sidebar dropdown below.
pages = [home, chat, discomforts, addictions, fears, music, pdf, settings]
selected_page = st.navigation(pages, position="sidebar")

healer_routes = {
    "General Discussion": chat,
    "Mental Discomforts": discomforts,
    "Addictions": addictions,
    "Fears": fears,
}
current_healer_choice = {
    "Let's Talk": "General Discussion",
    "Mental Discomforts": "Mental Discomforts",
    "Addictions": "Addictions",
    "Fears": "Fears",
}.get(selected_page.title, "General Discussion")

with st.sidebar:
    st.markdown(
        "<div style='font-weight:750;letter-spacing:.06em;color:#173B2D;"
        "font-size:.78rem;margin:8px 0 4px 2px'>HEALER</div>",
        unsafe_allow_html=True,
    )
    healer_choice = st.selectbox(
        "Choose a support area",
        options=list(healer_routes.keys()),
        index=list(healer_routes.keys()).index(current_healer_choice),
        label_visibility="collapsed",
        key="healer_support_menu",
    )
    if healer_routes[healer_choice].title != selected_page.title:
        st.switch_page(healer_routes[healer_choice])

selected_page.run()
