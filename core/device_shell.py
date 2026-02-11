"""Device shell access: SSH, ADB, Serial."""
import subprocess
import shutil
import time
import random
import os
import base64
import queue
from typing import Tuple, Dict, Any, List

try:
    import paramiko
except ImportError:
    paramiko = None

try:
    import serial
except ImportError:
    serial = None

from ..utils import json_or_empty


def run_shell_on_device(
    device: Dict[str, Any],
    command: str,
    access: str | None,
    log_q: queue.Queue,
    timeout: int = 60
) -> Tuple[int, str, str]:
    """
    Run shell command on device via SSH/ADB/Serial/Auto.
    Returns (rc, stdout, stderr).
    """
    access = (access or "").lower() or "auto"
    extra = json_or_empty(device.get("extra_json") or "{}")
    
    def use_ssh() -> bool:
        return bool(
            device.get("mgmt_ip") and
            (device.get("username") or extra.get("username") or extra.get("ssh_key_path")) and
            paramiko is not None
        )
    
    def use_adb() -> bool:
        return bool(extra.get("adb_serial") or extra.get("adb_id"))
    
    def use_serial() -> bool:
        return bool(extra.get("com_port")) and serial is not None
    
    # Resolve access method
    chosen = None
    if access in ("ssh", "adb", "serial"):
        chosen = access
    else:
        if use_ssh():
            chosen = "ssh"
        elif use_adb():
            chosen = "adb"
        elif use_serial():
            chosen = "serial"
        else:
            chosen = "ssh"
    
    if chosen == "ssh":
        if paramiko is None:
            return 127, "", "Paramiko not installed"
        
        host = device.get("mgmt_ip")
        username = device.get("username") or extra.get("username") or "root"
        password = device.get("password") or extra.get("password")
        key_path = extra.get("ssh_key_path")
        passphrase = extra.get("ssh_key_passphrase")
        
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if key_path:
                pkey = _load_ssh_key(key_path, passphrase)
                client.connect(hostname=host, username=username, pkey=pkey, timeout=20, allow_agent=True, look_for_keys=True)
            else:
                client.connect(hostname=host, username=username, password=password or None, timeout=20, allow_agent=True, look_for_keys=True)
            
            stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
            out = stdout.read().decode("utf-8", errors="ignore")
            err = stderr.read().decode("utf-8", errors="ignore")
            rc = stdout.channel.recv_exit_status()
            client.close()
            return rc, out, err
        except Exception as e:
            return 127, "", f"ssh error: {e}"
    
    if chosen == "adb":
        serial_id = extra.get("adb_serial") or extra.get("adb_id")
        if not shutil.which("adb"):
            return 127, "", "adb not found in PATH"
        
        cmd = ["adb"]
        if serial_id:
            cmd += ["-s", str(serial_id)]
        cmd += ["shell", command]
        
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return proc.returncode, proc.stdout, proc.stderr
        except Exception as e:
            return 127, "", f"adb error: {e}"
    
    if chosen == "serial":
        port = extra.get("com_port")
        baud = int(extra.get("baud", 115200))
        if serial is None:
            return 127, "", "pyserial not installed"
        
        try:
            ser = serial.Serial(port=port, baudrate=baud, timeout=1)
            ser.write((command + "\n").encode("utf-8"))
            ser.flush()
            
            t0 = time.time()
            chunks = []
            while time.time() - t0 < min(timeout, 5):
                data = ser.read(4096)
                if data:
                    chunks.append(data)
            
            out = (b"".join(chunks)).decode("utf-8", errors="ignore")
            ser.close()
            rc = 0 if ("not found" not in out.lower()) else 127
            return rc, out, ""
        except Exception as e:
            return 127, "", f"serial error: {e}"
    
    return 127, "", f"unknown access method {chosen}"


def _load_ssh_key(key_path: str, passphrase: str = None):
    """Load SSH private key (RSA or Ed25519)."""
    try:
        return paramiko.RSAKey.from_private_key_file(key_path, password=passphrase)
    except Exception:
        try:
            return paramiko.Ed25519Key.from_private_key_file(key_path, password=passphrase)
        except Exception:
            return None


def run_streaming_shell_on_device(
    device: Dict[str, Any],
    command: str,
    access: str | None,
    log_q: queue.Queue,
    duration: int = 20
) -> int:
    """Stream command output line-by-line (SSH preferred). Returns rc."""
    access = (access or "").lower() or "auto"
    extra = json_or_empty(device.get("extra_json") or "{}")
    
    if (access in ("auto", "ssh")) and paramiko is not None and device.get("mgmt_ip"):
        try:
            host = device.get("mgmt_ip")
            username = device.get("username") or extra.get("username") or "root"
            password = device.get("password") or extra.get("password")
            key_path = extra.get("ssh_key_path")
            passphrase = extra.get("ssh_key_passphrase")
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if key_path:
                pkey = _load_ssh_key(key_path, passphrase)
                client.connect(hostname=host, username=username, pkey=pkey, timeout=20, allow_agent=True, look_for_keys=True)
            else:
                client.connect(hostname=host, username=username, password=password or None, timeout=20, allow_agent=True, look_for_keys=True)
            
            chan = client.get_transport().open_session()
            chan.exec_command(command)
            
            t0 = time.time()
            buf = b""
            
            while True:
                if chan.recv_ready():
                    data = chan.recv(4096)
                    if not data:
                        break
                    buf += data
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        try:
                            log_q.put(line.decode("utf-8", errors="ignore"))
                        except Exception:
                            pass
                
                if chan.exit_status_ready():
                    break
                
                if time.time() - t0 > duration:
                    try:
                        chan.close()
                    except Exception:
                        pass
                    break
                
                time.sleep(0.1)
            
            if buf:
                try:
                    log_q.put(buf.decode("utf-8", errors="ignore"))
                except Exception:
                    pass
            
            rc = chan.recv_exit_status() if chan.exit_status_ready() else 0
            client.close()
            return rc
        except Exception as e:
            try:
                log_q.put(f"stream error: {e}")
            except Exception:
                pass
            return 127
    
    # Fallback: run normally and dump
    rc, out, err = run_shell_on_device(device, command, access, log_q, timeout=duration + 5)
    if out:
        for ln in out.splitlines():
            log_q.put(ln)
    if err:
        for ln in err.splitlines():
            log_q.put(ln)
    return rc


def write_text_file_on_device(
    device: Dict[str, Any],
    path: str,
    content: str,
    access: str | None,
    log_q: queue.Queue
) -> Tuple[int, str]:
    """
    Write file to device using chunked base64 encoding.
    Avoids shell/argv limits for large payloads.
    Returns (rc, message).
    """
    def _log(msg):
        try:
            log_q.put(msg)
        except Exception:
            pass
    
    dirn = os.path.dirname(path) or "/tmp"
    rc, out, err = run_shell_on_device(device, f"sh -lc 'mkdir -p {dirn}'", access, log_q, timeout=20)
    if rc != 0:
        _log(f"[config_write] mkdir failed for {dirn}: {err or out}")
        return rc, (err or out or "mkdir failed")
    
    tmp = f"/tmp/trig_{int(time.time())}_{random.randint(1000,9999)}.tmp"
    raw = content.encode("utf-8")
    CHUNK = 500
    
    rc, out, err = run_shell_on_device(device, f"sh -lc ': > {tmp}'", access, log_q, timeout=20)
    if rc != 0:
        _log(f"[config_write] init tmp failed: {err or out}")
        return rc, (err or out or "init tmp failed")
    
    total = len(raw)
    pos = 0
    idx = 0
    while pos < total:
        part = raw[pos:pos+CHUNK]
        pos += len(part)
        idx += 1
        b64 = base64.b64encode(part).decode("ascii")
        cmd = f"sh -lc \"printf %s '{b64}' | base64 -d >> {tmp}\""
        rc, out, err = run_shell_on_device(device, cmd, access, log_q, timeout=60)
        if rc != 0:
            _log(f"[config_write] chunk {idx} failed ({len(part)}B): {err or out}")
            run_shell_on_device(device, f"sh -lc 'rm -f {tmp}'", access, log_q, timeout=10)
            return rc, (err or out or f"chunk {idx} failed")
    
    cmd_mv = f"sh -lc 'mv -f {tmp} {path} && chmod 0644 {path} || (rc=$?; rm -f {tmp}; exit $rc)'"
    rc, out, err = run_shell_on_device(device, cmd_mv, access, log_q, timeout=20)
    if rc == 0:
        _log("[config_write] write OK (chunked)")
        return 0, (out or "")
    else:
        _log(f"[config_write] finalize failed: {err or out}")
        return rc, (err or out or "finalize failed")


def fetch_file_from_device(
    device: Dict[str, Any],
    remote_path: str,
    local_dir: str,
    access: str | None,
    log_q: queue.Queue
) -> Tuple[bool, str]:
    """Fetch file from device to local directory."""
    os.makedirs(local_dir, exist_ok=True)
    dev_name = device.get("name") or "device"
    base = os.path.basename(remote_path) or f"capture_{int(time.time())}.pcap"
    local_path = os.path.join(local_dir, f"{dev_name}_{base}")
    
    extra = json_or_empty(device.get("extra_json") or "{}")
    chosen = (access or "auto").lower()
    
    if chosen in ("auto", "ssh") and paramiko is not None and device.get("mgmt_ip"):
        try:
            host = device.get("mgmt_ip")
            username = device.get("username") or extra.get("username") or "root"
            password = device.get("password") or extra.get("password")
            key_path = extra.get("ssh_key_path")
            passphrase = extra.get("ssh_key_passphrase")
            
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if key_path:
                pkey = _load_ssh_key(key_path, passphrase)
                client.connect(hostname=host, username=username, pkey=pkey, timeout=20, allow_agent=True, look_for_keys=True)
            else:
                client.connect(hostname=host, username=username, password=password or None, timeout=20, allow_agent=True, look_for_keys=True)
            
            sftp = client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            client.close()
            return True, local_path
        except Exception as e:
            log_q.put(f"SFTP get failed: {e}")
            if chosen != "auto":
                return False, str(e)
    
    if chosen in ("auto", "adb"):
        serial_id = extra.get("adb_serial") or extra.get("adb_id")
        if shutil.which("adb"):
            cmd = ["adb"] + (["-s", str(serial_id)] if serial_id else []) + ["pull", remote_path, local_path]
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                if proc.returncode == 0 and os.path.exists(local_path):
                    return True, local_path
                else:
                    log_q.put(proc.stdout + "" + proc.stderr)
            except Exception as e:
                return False, str(e)
        else:
            log_q.put("adb not found in PATH")
    
    return False, "unsupported method or failure"
