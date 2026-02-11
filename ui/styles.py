"""UI styling for TestRig Automator."""
import streamlit as st


def inject_css_once():
    """Inject CSS once per session."""
    if st.session_state.get('_rig_css_done'):
        return
    st.session_state['_rig_css_done'] = True
    st.markdown(
        '<style> .small-note{font-size:12px;opacity:0.85} </style>',
        unsafe_allow_html=True
    )


def apply_page_styles():
    """Apply page-level CSS."""
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
