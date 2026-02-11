"""Testbeds page implementation: list, create, import/export, and device table."""
import json
import streamlit as st
from database import db_query, db_exec


def _export_testbed_json(testbed_id: int) -> str:
    row = db_query("SELECT id, name, COALESCE(description,'') AS description FROM testbeds WHERE id=?", (testbed_id,), one=True)
    if not row:
        return json.dumps({"error": "testbed not found"})
    devs = db_query("SELECT role, name, mgmt_ip, COALESCE(username,'') AS username, COALESCE(password,'') AS password, COALESCE(extra_json,'{}') AS extra_json FROM devices WHERE testbed_id=? ORDER BY id", (testbed_id,)) or []
    payload = {"testbed": {"name": row["name"], "description": row.get("description", "")}, "devices": devs}
    return json.dumps(payload, indent=2)


def _import_testbed_from_json(data: dict):
    try:
        tb = data.get("testbed") or {}
        devs = data.get("devices") or []
        if not isinstance(tb, dict):
            return False, "testbed must be an object"
        name = (tb.get("name") or "").strip()
        if not name:
            return False, "testbed.name must be non-empty"
        desc = tb.get("description", "") or ""
        if not isinstance(desc, str):
            return False, "testbed.description must be a string"
        if not isinstance(devs, list):
            return False, "devices must be a list"
        base = name
        k = 1
        while db_query("SELECT 1 FROM testbeds WHERE name= ?", (name,)):
            k += 1
            name = f"{base} ({k})"
        db_exec("INSERT INTO testbeds (name, description) VALUES (?, ?)", (name, desc))
        trow = db_query("SELECT id FROM testbeds WHERE name=?", (name,), one=True)
        tbid = trow["id"] if trow else None
        if not tbid:
            return False, "failed to create testbed"
        for d in devs:
            role = (d.get("role") or "Other").strip() if isinstance(d, dict) else "Other"
            dname = (d.get("name") or "").strip() if isinstance(d, dict) else ""
            mgmt_ip = (d.get("mgmt_ip") or "").strip() if isinstance(d, dict) else ""
            username = (d.get("username") or "").strip() if isinstance(d, dict) else ""
            password = (d.get("password") or "").strip() if isinstance(d, dict) else ""
            extra_json = d.get("extra_json") if isinstance(d, dict) else "{}"
            if not isinstance(extra_json, str):
                try:
                    extra_json = json.dumps(extra_json)
                except Exception:
                    extra_json = "{}"
            if not dname:
                dname = f"{role}-{tbid}"
            db_exec("INSERT INTO devices (testbed_id, role, name, mgmt_ip, username, password, extra_json) VALUES (?,?,?,?,?,?,?)",
                    (tbid, role, dname, mgmt_ip, username, password, extra_json))
        return True, name
    except Exception as e:
        return False, f"import error: {e}"


def _ui_devices_for_selected_testbed(testbed_id: int):
    devices = db_query("SELECT * FROM devices WHERE testbed_id=? ORDER BY id", (testbed_id,))
    if not devices:
        st.info("No devices in this testbed yet.")
        return

    cols = st.columns([0.8,1.2,2.0,1.6,1.2,1.2,2.6,0.8,0.8])
    cols[0].markdown("**ID**")
    cols[1].markdown("**Role**")
    cols[2].markdown("**Name**")
    cols[3].markdown("**Mgmt IP**")
    cols[4].markdown("**COM**")
    cols[5].markdown("**ADB**")
    cols[6].markdown("**Status (reason)**")
    cols[7].markdown("**↻**")
    cols[8].markdown("**Delete**")

    cache = st.session_state.setdefault("_dev_status", {})
    for d in devices:
        try:
            ej = json.loads(d.get("extra_json") or "{}")
        except Exception:
            ej = {}
        com = ej.get("com_port", "")
        adb = ej.get("adb_serial") or ej.get("adb_id") or ""
        row_cols = st.columns([0.8,1.2,2.0,1.6,1.2,1.2,2.6,0.8,0.8])
        row_cols[0].write(str(d["id"]))
        row_cols[1].write(str(d.get("role", "")))
        row_cols[2].write(str(d.get("name", "")))
        row_cols[3].write(str(d.get("mgmt_ip", "")))
        row_cols[4].write(str(com))
        row_cols[5].write(str(adb))

        if row_cols[7].button("🔄", key=f"dev_recheck_{d['id']}"):
            st.info("Recheck not implemented in lightweight UI")

        if row_cols[8].button("🗑️", key=f"dev_delete_{d['id']}"):
            db_exec("DELETE FROM devices WHERE id=?", (d["id"],))
            st.success(f"Deleted device {d['name']}")
            _safe_rerun()


def render():
    st.subheader("Testbeds")
    st.info("🏢 Testbeds management - Create, manage, and configure testbeds with devices.")

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
        try:
            db_exec("INSERT INTO testbeds (name, description) VALUES (?, ?)", (name.strip(), desc.strip()))
            st.success(f"✅ Created testbed: {name}")
            # Use compatible rerun API
            _safe_rerun()
        except Exception as e:
            st.error(f"❌ Error: {e}")

    st.divider()
    # Export / Import
    if beds:
        tb_ids = [b["id"] for b in beds]
        tb_names = [b["name"] for b in beds]
        sel = st.selectbox("Select testbed for export", tb_names, key="tb_export_sel")
        if st.button("Export selected testbed as JSON"):
            idx = tb_names.index(sel)
            tbid = tb_ids[idx]
            payload = _export_testbed_json(tbid)
            st.download_button("Download JSON", data=payload, file_name=f"testbed_{sel}.json", mime="application/json")

    with st.expander("Import testbed from JSON"):
        uploaded = st.file_uploader("Upload testbed JSON file", type=["json"], key="tb_import_file")
        if uploaded is not None:
            try:
                data = json.load(uploaded)
                ok, msg = _import_testbed_from_json(data)
                if ok:
                    st.success(f"Imported testbed: {msg}")
                    _safe_rerun()
                else:
                    st.error(f"Import failed: {msg}")
            except Exception as e:
                st.error(f"Invalid JSON: {e}")

    st.divider()
    # Show devices for a selected testbed
    selected = None
    if beds:
        sel2 = st.selectbox("Show devices for testbed", [b["name"] for b in beds], key="tb_show_devices")
        for b in beds:
            if b["name"] == sel2:
                selected = b["id"]
                break
    if selected:
        _ui_devices_for_selected_testbed(selected)

        st.divider()
        st.subheader("Add Device to Selected Testbed")
        with st.form("form_add_device"):
            role = st.selectbox("Role", ["AP", "STA", "Controller", "Ixia", "Attenuator", "Switch", "Server", "Sniffer", "Backbone", "Other"], index=9)
            dev_name = st.text_input("Device Name")
            mgmt_ip = st.text_input("Mgmt IP")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            com_port = st.text_input("COM Port")
            adb_id = st.text_input("ADB ID")
            add_sub = st.form_submit_button("Add Device")

        if add_sub:
            if not dev_name.strip():
                st.error("Device name is required")
            else:
                extra = {}
                if com_port.strip():
                    extra["com_port"] = com_port.strip()
                if adb_id.strip():
                    extra["adb_serial"] = adb_id.strip()
                try:
                    db_exec(
                        "INSERT INTO devices (testbed_id, role, name, mgmt_ip, username, password, extra_json) VALUES (?,?,?,?,?,?,?)",
                        (selected, role, dev_name.strip(), mgmt_ip.strip(), username.strip(), password.strip(), json.dumps(extra)),
                    )
                    st.success(f"Added device: {dev_name.strip()}")
                    _safe_rerun()
                except Exception as e:
                    st.error(f"Error adding device: {e}")


# Helper: safe rerun compatible with multiple Streamlit versions
def _safe_rerun():
    fn = getattr(st, "rerun", None)
    if fn is None:
        fn = getattr(st, "experimental_rerun", None)
    if fn:
        try:
            fn()
        except Exception:
            pass
