"""Helper utility functions."""
import json
from typing import Dict, Any
from ..database import db_query


def json_or_empty(s: str) -> Dict[str, Any]:
    """Try to parse JSON string, return empty dict on failure."""
    s = (s or "").strip()
    if not s:
        return {}
    try:
        return json.loads(s)
    except Exception:
        return {}


def device_context_for_testbed(testbed_id: int, role_bindings: Dict[str, str] | None = None) -> Dict[str, Any]:
    """
    Build a context dict for use in actions with device info indexed by role.
    e.g., {ap_ip: "192.168.1.2", sta_name: "STA-1", devices: [...]}
    """
    devices = db_query("SELECT * FROM devices WHERE testbed_id=? ORDER BY id", (testbed_id,))
    ctx: Dict[str, Any] = {"devices": []}
    
    # Index first device by role
    for d in devices:
        role = (d["role"] or "").lower()
        ip_key = f"{role}_ip" if role else None
        name_key = f"{role}_name" if role else None
        if ip_key and ip_key not in ctx:
            ctx[ip_key] = d["mgmt_ip"]
        if name_key and name_key not in ctx:
            ctx[name_key] = d["name"]
        ctx["devices"].append(dict(d))
    
    # Apply explicit role bindings (override defaults)
    if role_bindings:
        for r, dev_name in role_bindings.items():
            r_l = (r or "").lower()
            row = db_query("SELECT * FROM devices WHERE testbed_id=? AND name=?", (testbed_id, dev_name), one=True)
            if row:
                ctx[f"{r_l}_ip"] = row["mgmt_ip"]
                ctx[f"{r_l}_name"] = row["name"]
    
    return ctx


def validate_json(s: str) -> bool:
    """Check if a string is valid JSON."""
    try:
        json.loads(s or "{}")
        return True
    except Exception:
        return False
