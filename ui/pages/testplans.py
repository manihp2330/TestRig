"""Testplans page."""
import streamlit as st
from database import db_query
import pandas as pd


def render():
    st.subheader("Testplans")
    st.info("📋 Testplans - Organize testcases into executable plans.")

    plans = db_query("SELECT id, name FROM testplans ORDER BY name")

    if plans:
        df = pd.DataFrame([{"Name": p["name"]} for p in plans])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No testplans yet.")
