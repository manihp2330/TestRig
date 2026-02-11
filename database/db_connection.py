"""SQLite database connection management."""
import sqlite3
import streamlit as st
from config import DB_PATH


def get_conn() -> sqlite3.Connection:
    """
    Get or create SQLite connection (cached in Streamlit session state).
    Streamlit re-runs script, so keep a single connection in session_state.
    """
    if "_db_conn" not in st.session_state:
        st.write(f"Using DB: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        st.session_state["_db_conn"] = conn
    return st.session_state["_db_conn"]
