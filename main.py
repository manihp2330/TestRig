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
    """Dashboard page."""
    st.subheader("Dashboard")
    st.info("📊 Dashboard page - Shows testbed, testcase, testplan, and run statistics.")
    
    from database import db_query
    try:
        beds_n = db_query("SELECT COUNT(*) as n FROM testbeds", one=True)["n"]
        devs_n = db_query("SELECT COUNT(*) as n FROM devices", one=True)["n"]
        tcs_n = db_query("SELECT COUNT(*) as n FROM testcases", one=True)["n"]
        tps_n = db_query("SELECT COUNT(*) as n FROM testplans", one=True)["n"]
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Testbeds", beds_n)
        c2.metric("Devices", devs_n)
        c3.metric("Testcases", tcs_n)
        c4.metric("Testplans", tps_n)
    except Exception as e:
        st.error(f"Error loading statistics: {e}")


def render_testbeds():
    """Testbeds management page."""
    st.subheader("Testbeds")
    st.info("🏢 Testbeds management - Create, manage, and configure testbeds with devices.")
    
    from database import db_query
    beds = db_query("SELECT id, name FROM testbeds ORDER BY name")
    
    if not beds:
        st.info("No testbeds yet. Use the form below to create one.")
    else:
        st.write("**Existing Testbeds:**")
        for b in beds:
            st.write(f"  • {b['name']}")
    
    st.divider()
    with st.form("form_create_testbed"):
        name = st.text_input("Testbed Name", placeholder="e.g., Lab-A")
        desc = st.text_area("Description", placeholder="Brief description of this testbed")
        submitted = st.form_submit_button("Create Testbed")
    
    if submitted and name.strip():
        from database import db_exec
        try:
            db_exec("INSERT INTO testbeds (name, description) VALUES (?, ?)", (name.strip(), desc.strip()))
            st.success(f"✅ Created testbed: {name}")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {e}")


def render_testcases():
    """Testcases page."""
    st.subheader("Testcases")
    st.info("🧪 Testcases - Define test scenarios with builtin or custom actions.")
    
    from database import db_query
    tcs = db_query("SELECT id, name, action_type FROM testcases ORDER BY name")
    
    if tcs:
        import pandas as pd
        df = pd.DataFrame([{"Name": t["name"], "Type": t["action_type"]} for t in tcs])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No testcases yet.")


def render_testplans():
    """Testplans page."""
    st.subheader("Testplans")
    st.info("📋 Testplans - Organize testcases into executable plans.")
    
    from database import db_query
    plans = db_query("SELECT id, name FROM testplans ORDER BY name")
    
    if plans:
        import pandas as pd
        df = pd.DataFrame([{"Name": p["name"]} for p in plans])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No testplans yet.")


def render_runner():
    """Test execution page."""
    st.subheader("Runner")
    st.info("▶️ Runner - Execute testplans on selected testbeds with live progress.")


def render_results():
    """Results page."""
    st.subheader("Results")
    st.info("📈 Results - View execution results, logs, and metrics from completed runs.")


def render_settings():
    """Settings page."""
    st.subheader("Settings")
    st.info("⚙️ Settings - Configure preferences and database settings.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Database Status**")
        try:
            from database import db_query
            count = db_query("SELECT COUNT(*) as n FROM testbeds", one=True)
            st.success(f"✅ Database connected ({count['n']} testbeds)")
        except Exception as e:
            st.error(f"❌ Database error: {e}")
    
    with col2:
        st.write("**Python Version**")
        import sys
        st.info(f"Python {sys.version.split()[0]}")


if __name__ == "__main__":
    main()
