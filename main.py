"""
TestRig Automator - Main Entry Point

A professional WLAN testbed automation tool with multi-folder architecture.
Run with: streamlit run main.py
"""

import streamlit as st
from database import init_db, seed_examples_if_empty
from ui.styles import apply_page_styles, inject_css_once


def init_streamlit():
    """Initialize Streamlit configuration."""
    st.set_page_config(
        page_title="TestRig Automator",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state defaults
    st.session_state.setdefault("_export_retention_days", 2)
    st.session_state.setdefault("_tb_preview_open", False)
    st.session_state.setdefault("_import_stage", "idle")
    st.session_state.setdefault("_import_payload", None)
    st.session_state.setdefault("_dupe_inline_open", False)
    st.session_state.setdefault("_enable_live_logs", False)
    st.session_state.setdefault("_skip_reach_dev_table", False)


def main():
    """Main application entry point."""
    init_streamlit()
    apply_page_styles()
    inject_css_once()
    
    # Initialize database
    init_db()
    seed_examples_if_empty()
    
    # Render header
    st.title("TestRig Automator")
    st.caption("Testbed • Testcase • Testplan • Runner")
    st.divider()
    
    # Multi-page navigation
    page = st.sidebar.radio(
        "Navigate",
        [
            "Dashboard",
            "Testbeds",
            "Testcases",
            "Testplans",
            "Runner",
            "Results",
            "Settings",
        ],
        label_visibility="collapsed"
    )
    
    # Route to appropriate page
    if page == "Dashboard":
        render_dashboard()
    elif page == "Testbeds":
        render_testbeds()
    elif page == "Testcases":
        render_testcases()
    elif page == "Testplans":
        render_testplans()
    elif page == "Runner":
        render_runner()
    elif page == "Results":
        render_results()
    elif page == "Settings":
        render_settings()


def render_dashboard():
    from ui.pages import dashboard
    dashboard.render()


def render_testbeds():
    from ui.pages import testbeds
    testbeds.render()


def render_testcases():
    from ui.pages import testcases
    testcases.render()


def render_testplans():
    from ui.pages import testplans
    testplans.render()


def render_runner():
    from ui.pages import runner
    runner.render()


def render_results():
    from ui.pages import results
    results.render()


def render_settings():
    from ui.pages import settings
    settings.render()


if __name__ == "__main__":
    main()
