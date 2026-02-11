"""Testbed management: export, import, validation."""
import json
from typing import Tuple
from ..database import db_query, db_exec


def export_testbed_json(testbed_id: int) -> str:
    """
    Export testbed and its devices as JSON.
    Returns JSON string.
    """
    row = db_query(
        "SELECT id, name, COALESCE(description,'') AS description FROM testbeds WHERE id=?",
        (testbed_id,),
        one=True
    )
    if not row:
        return json.dumps({"error": "testbed not found"})
    
    devs = db_query(
        """SELECT role, name, mgmt_ip, COALESCE(username,'') AS username, 
           COALESCE(password,'') AS password, COALESCE(extra_json,'{}') AS extra_json 
           FROM devices WHERE testbed_id=? ORDER BY id""",
        (testbed_id,)
    ) or []
    
    payload = {
        "testbed": {
            "name": row["name"],
            "description": row.get("description", "")
        },
        "devices": devs
    }
    return json.dumps(payload, indent=2)


def import_testbed_from_json(data: dict) -> Tuple[bool, str]:
    """
    Import testbed from JSON data.
    Returns (success, message).
    """
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
        
        # Ensure unique name
        base = name
        k = 1
        while db_query("SELECT 1 FROM testbeds WHERE name=?", (name,)):
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
            
            db_exec(
                """INSERT INTO devices (testbed_id, role, name, mgmt_ip, username, password, extra_json)
                   VALUES (?,?,?,?,?,?,?)""",
                (tbid, role, dname, mgmt_ip, username, password, extra_json)
            )
        
        return True, name
    except Exception as e:
        return False, f"import error: {e}"
