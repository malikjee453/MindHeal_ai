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

st.title("🔄 Habits & Addictions")
category=st.selectbox("Area",["Alcohol","Nicotine / tobacco","Opioids","Stimulants","Caffeine","Gambling","Internet / smartphone","Social media","Gaming","Pornography / sexual behavior"])
intensity=st.slider("Current urge intensity",0,10,5); trigger=st.text_input("Main trigger"); details=st.text_area("What tends to happen before and after?",height=160)
if st.button("Build a coping plan",type="primary"):
    try:
        answer,_,_=respond(f"I want help with {category}. Urge intensity: {intensity}/10. Trigger: {trigger}. Details: {details}"); st.markdown(answer)
    except Exception as e: st.error(f"{type(e).__name__}: {e}")
