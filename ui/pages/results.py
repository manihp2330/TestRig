"""Results page."""
import streamlit as st
from database import db_query
import pandas as pd


def render():
    st.subheader("Results")
    st.info("📈 Results - View execution results, logs, and metrics from completed runs.")

    rows = db_query(
        "SELECT r.id, r.plan_id, r.testbed_id, r.status, r.start_ts, r.end_ts, p.name AS plan_name, t.name AS testbed_name "
        "FROM runs r LEFT JOIN testplans p ON r.plan_id=p.id LEFT JOIN testbeds t ON r.testbed_id=t.id ORDER BY r.id DESC"
    )
    if rows:
        df = pd.DataFrame([
            {
                "ID": r["id"],
                "Testplan": r.get("plan_name") or r.get("plan_id"),
                "Testbed": r.get("testbed_name") or r.get("testbed_id"),
                "Status": r.get("status"),
                "Started": r.get("start_ts"),
                "Finished": r.get("end_ts"),
            }
            for r in rows
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No run results yet.")
