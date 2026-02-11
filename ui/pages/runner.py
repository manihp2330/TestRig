"""Runner page (basic runner UI)."""
import streamlit as st
from database import db_query


def render():
    st.subheader("Runner")
    st.info("▶️ Runner - Execute testplans on selected testbeds with live progress.")

    plans = db_query("SELECT id, name FROM testplans ORDER BY name")
    beds = db_query("SELECT id, name FROM testbeds ORDER BY name")

    if not plans or not beds:
        st.info("Create at least one testplan and one testbed to run.")
        return

    plan_sel = st.selectbox("Select testplan", [p["name"] for p in plans], key="runner_plan")
    bed_sel = st.selectbox("Select testbed", [b["name"] for b in beds], key="runner_bed")

    if st.button("Start run"):
        st.info("Run execution is not yet wired to the backend runner in this lightweight UI.")
