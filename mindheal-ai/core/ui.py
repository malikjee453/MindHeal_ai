import streamlit as st


def render_header(name, tagline, builder):
    st.markdown(f"# {name}")
    st.caption(tagline)
    st.caption(f"Built by: {builder}")


def render_disclaimer():
    # Compact one-word label, centered within the sidebar content column.
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] [data-testid="stExpander"] {
            margin-left: 0 !important;
            width: 100% !important;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] details summary {
            display: flex !important;
            justify-content: center !important;
            padding: 0.25rem 0.35rem !important;
            min-height: 1.9rem !important;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] details summary p {
            text-align: center !important;
            font-size: 0.82rem !important;
            margin: 0 !important;
        }
        [data-testid="stSidebar"] [data-testid="stExpander"] details summary svg {
            width: 0.8rem !important;
            height: 0.8rem !important;
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
