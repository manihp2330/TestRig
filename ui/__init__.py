"""UI module for TestRig Automator."""
import streamlit as st

__all__ = ['apply_styles']


def apply_styles():
    """Apply global CSS styles."""
    st.markdown("""
<style>
/* --- UI polish --- */
.block-container { padding-top: 1rem; padding-bottom: 2rem; }
h1, h2, h3, h4 { margin-top: .6rem; margin-bottom: .4rem; }
.stButton>button { padding: .35rem .8rem; border-radius: 10px; }
.stTextInput>div>div>input, .stSelectbox>div>div>select, .stTextArea textarea { font-size: .95rem; }
table td, .dataframe td { padding: 6px 8px; }
.small-note { color: #5f6368; font-size: .85rem; }
</style>
""", unsafe_allow_html=True)
