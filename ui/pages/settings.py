"""Settings page."""
import streamlit as st
from database import db_query
import sys


def render():
    st.subheader("Settings")
    st.info("⚙️ Settings - Configure preferences and database settings.")

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Database Status**")
        try:
            count = db_query("SELECT COUNT(*) as n FROM testbeds", one=True)
            st.success(f"✅ Database connected ({count['n']} testbeds)")
        except Exception as e:
            st.error(f"❌ Database error: {e}")

    with col2:
        st.write("**Python Version**")
        st.info(f"Python {sys.version.split()[0]}")
