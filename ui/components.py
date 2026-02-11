"""Reusable UI components for TestRig Automator."""
import streamlit as st
from ..database import db_query


def select_testbed_id(label: str = "Select testbed") -> int | None:
    """Render testbed selector dropdown."""
    beds = db_query("SELECT id, name FROM testbeds ORDER BY name")
    if not beds:
        st.info("No testbeds yet. Create one in the Testbeds tab.")
        return None
    
    options = {b["name"]: b["id"] for b in beds}
    pick = st.selectbox(label, list(options.keys()), index=0)
    return options[pick]


def device_ref_input(lbl: str, key_prefix: str) -> dict:
    """Render device reference input (name or role based)."""
    c1, c2 = st.columns(2)
    with c1:
        by_name = st.checkbox("By name", key=f"{key_prefix}_by_name")
    
    if by_name:
        name = st.text_input("Device name", key=f"{key_prefix}_name")
        return {"name": name.strip() if name else None}
    else:
        role = st.selectbox("Device role", ["AP", "STA", "Controller", "Server", "Other"], key=f"{key_prefix}_role")
        return {"role": role}


def header_title():
    """Render consistent page header."""
    st.title("TestRig Automator")
    st.caption("Testbed • Testcase • Testplan • Runner")
    st.divider()
