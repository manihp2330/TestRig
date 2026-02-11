"""Testcases page."""
import streamlit as st
from database import db_query
import pandas as pd


def render():
    st.subheader("Testcases")
    st.info("🧪 Testcases - Define test scenarios with builtin or custom actions.")

    tcs = db_query("SELECT id, name, action_type FROM testcases ORDER BY name")

    if tcs:
        df = pd.DataFrame([{"Name": t["name"], "Type": t["action_type"]} for t in tcs])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No testcases yet.")
