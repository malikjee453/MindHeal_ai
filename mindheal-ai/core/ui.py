import streamlit as st


def render_header(name, tagline, builder):
    st.markdown(f"# {name}")
    st.caption(tagline)
    st.caption(f"Built by: {builder}")


def render_disclaimer():
    with st.expander("Important wellbeing note"):
        st.write(
            "MindHeal AI provides general emotional-support and "
            "educational information. It is not a replacement for "
            "a qualified professional or emergency service."
        )
