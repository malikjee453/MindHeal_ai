import streamlit as st


def render_header(name, tagline, builder):
    st.markdown(f"# {name}")
    st.caption(tagline)
    st.caption(f"Built by: {builder}")


def render_disclaimer():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] [data-testid="stExpander"] summary {
            justify-content: center !important;
            text-align: center !important;
            padding: 0.35rem 0.5rem !important;
            min-height: 2.2rem !important;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] summary p {
            width: 100%;
            text-align: center !important;
            font-size: 0.85rem !important;
            margin: 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.sidebar.expander("Wellbeing"):
        st.write(
            "MindHeal AI provides general emotional-support and "
            "educational information. It is not a replacement for "
            "a qualified professional or emergency service."
        )
