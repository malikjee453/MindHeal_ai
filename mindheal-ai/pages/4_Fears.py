import streamlit as st
from agents.orchestrator import respond

st.markdown("""
<style>
/* Keep every page heading the same deep green as the MindHeal brand title. */
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
</style>
""", unsafe_allow_html=True)

st.title("🌤️ Fears")
fear=st.selectbox("Choose a fear",["Death","Public speaking","Failure","Rejection / abandonment","Heights","Spiders / insects","Darkness","Losing control","Loneliness / isolation","Unknown / uncertainty"])
situation=st.text_area("Describe what happens when this fear appears",height=160)
if st.button("Work through this fear",type="primary") and situation:
    try:
        answer,_,_=respond(f"My fear is {fear}. {situation}"); st.markdown(answer)
    except Exception as e: st.error(f"{type(e).__name__}: {e}")
