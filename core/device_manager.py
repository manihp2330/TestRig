"""Device reachability checking module."""
import subprocess
import platform
import time
from typing import Tuple, Dict, Any

try:
    import paramiko
except ImportError:
    paramiko = None

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    serial = None

import shutil

from ..database import db_query
from ..utils import json_or_empty


def probe_ip_once(ip: str) -> Tuple[bool, str]:
    """
    Ping an IP once with short timeout.
    Windows vs POSIX flags handled.
    """
    ip = (ip or "").strip()
    if not ip:
        return False, "ip not set"
    
    try:
        is_windows = platform.system().lower().startswith("win")
        cmd = ["ping", "-n" if is_windows else "-c", "1"]
        if is_windows:
            cmd += ["-w", "2000"]
        else:
            cmd += ["-W", "2"]
        cmd.append(ip)
        
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        if proc.returncode == 0:
            return True, "ip ok"
        
        reason = (proc.stdout or proc.stderr or "").strip().splitlines()
        reason = ("; ".join(reason[:3])) if reason else f"ip rc={proc.returncode}"
        return False, reason
    except Exception as e:
        return False, f"ip error: {e}"


def probe_com_once(port: str, baud: int | None = None) -> Tuple[bool, str]:
    """Serial reachability: ensure port is enumerated and can open/close."""
    port = (port or "").strip()
    if not port:
        return False, "com not set"
    
    try:
        if serial and hasattr(serial.tools, 'list_ports'):
            ports = [p.device for p in list_ports.comports()]
            if port not in ports:
                return False, "com not present"
    except Exception:
        pass
    
    try:
        if serial is None:
            return False, "pyserial not installed"
        
        s = serial.Serial(port=port, baudrate=int(baud or 115200), timeout=0.2)
        try:
            try:
                s.dtr = True
                s.rts = True
            except Exception:
                pass
            _ = s.read(1)
        finally:
            s.close()
        return True, "com ok"
    except Exception as e:
        return False, f"com error: {e}"


def probe_adb_once(adb_id: str) -> Tuple[bool, str]:
    """ADB reachability: ensure adb exists and device is 'device' state."""
    adb_id = (adb_id or "").strip()
    if not adb_id:
        return False, "adb not set"
    
    try:
        if not shutil.which("adb"):
            return False, "adb not found"
        
        proc = subprocess.run(
            ["adb", "-s", adb_id, "get-state"],
            capture_output=True,
            text=True,
            timeout=8
        )
        out = (proc.stdout or "").strip().lower()
        if proc.returncode == 0 and "device" in out:
            return True, "adb ok"
        
        # Fallback: parse 'adb devices'
        proc2 = subprocess.run(
            ["adb", "devices", "-l"],
            capture_output=True,
            text=True,
            timeout=8
        )
        ok = any(
            (adb_id in ln and "device" in ln.lower() and "offline" not in ln.lower())
            for ln in (proc2.stdout or "").splitlines()
        )
        if ok:
            return True, "adb ok (devices -l)"
        
        reason = out or (proc.stderr or "").strip() or "adb not device"
        return False, f"adb state: {reason} rc={proc.returncode}"
    except Exception as e:
        return False, f"adb error: {e}"


def device_reachability_status(dev_row: dict) -> Tuple[bool, dict]:
    """
    Check device reachability across configured endpoints.
    Returns (overall_ok, {endpoint: (ok, reason)}).
    """
    extra = json_or_empty(dev_row.get("extra_json") or "{}")
    
    ip_mgmt = (dev_row.get("mgmt_ip") or "").strip()
    ip_traffic = (extra.get("traffic_ip") or "").strip()
    com = (extra.get("com_port") or "").strip()
    adb = (extra.get("adb_serial") or extra.get("adb_id") or "").strip()
    baud = extra.get("baud", 115200)
    
    configured = 0
    results: dict[str, Tuple[bool, str]] = {}
    
    if ip_mgmt:
        configured += 1
        ok, msg = probe_ip_once(ip_mgmt)
        results["ip_mgmt"] = (ok, msg)
    else:
        results["ip_mgmt"] = (False, "not set")
    
    if ip_traffic:
        configured += 1
        ok, msg = probe_ip_once(ip_traffic)
        results["ip_traffic"] = (ok, msg)
    else:
        results["ip_traffic"] = (False, "not set")
    
    if com:
        configured += 1
        ok, msg = probe_com_once(com, baud)
        results["com"] = (ok, msg)
    else:
        results["com"] = (False, "not set")
    
    if adb:
        configured += 1
        ok, msg = probe_adb_once(adb)
        results["adb"] = (ok, msg)
    else:
        results["adb"] = (False, "not set")
    
    if configured == 0:
        return False, results
    
    overall_ok = True
    for k, (ok, reason) in results.items():
        if str(reason).lower().strip() != "not set":
            if not ok:
                overall_ok = False
                break
    
    return overall_ok, results


def device_reachability_summary(dev_row: dict) -> Tuple[bool, str]:
    """Get a human-readable reachability summary."""
    try:
        ok, details = device_reachability_status(dev_row)
    except Exception as e:
        return False, f"error: {e}"
    
    def _fmt(label, tup):
        if not tup:
            return None
        sub_ok, reason = tup
        if str(reason).lower().strip() == "not set":
            return None
        return f"{label}:{'ok' if sub_ok else reason}"
    
    parts = []
    for label in ("ip_mgmt", "ip_traffic", "com", "adb"):
        p = _fmt(label, details.get(label))
        if p:
            parts.append(p)
    
    if not parts:
        return ok, "no checks configured"
    if len(parts) > 2:
        summary = "; ".join(parts[:2]) + f"; +{len(parts)-2} more"
    else:
        summary = "; ".join(parts)
    return ok, summary


def check_reachability(dev_row: dict) -> bool:
    """Check if device is reachable."""
    ok, _details = device_reachability_status(dev_row)
    return ok


def reachability_probe_and_cache(dev_row: dict, *, cache: dict) -> dict:
    """Probe reachability and cache result with timestamp."""
    ok, reason = device_reachability_summary(dev_row)
    cache[dev_row['id']] = {
        'status': ('🟢' if ok else '🔴'),
        'reason': reason,
        'ts': time.time()
    }
    return cache[dev_row['id']]
