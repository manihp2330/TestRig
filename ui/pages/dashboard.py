"""Dashboard page for TestRig Automator."""
from database import db_query
import streamlit as st


def render():
    st.subheader("Dashboard")
    st.info("📊 Dashboard page - Shows testbed, testcase, testplan, and run statistics.")

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
