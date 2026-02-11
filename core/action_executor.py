"""Action execution: builtin and external commands."""
import json
import subprocess
import os
import time
import platform
import queue
from typing import Tuple, Dict, Any

try:
    import paramiko
except ImportError:
    paramiko = None

from ..utils import json_or_empty


def execute_builtin_action(
    action_name: str,
    params: Dict[str, Any],
    tb_ctx: Dict[str, Any],
    log_q: queue.Queue
) -> Tuple[str, Dict[str, Any]]:
    """
    Execute a builtin action (sleep, ping, iperf3, tshark_capture, ssh_exec).
    Returns (status, metrics_dict). Status in {PASSED, FAILED}.
    """
    action = (action_name or "").lower()
    
    if action == "sleep":
        dur = int(params.get("duration_s", 1))
        log_q.put(f"Sleeping for {dur}s...")
        for i in range(dur):
            time.sleep(1)
            log_q.put(f"  ... {i+1}/{dur}s")
        return "PASSED", {"duration_s": dur}
    
    if action == "ping":
        target = params.get("target_ip") or tb_ctx.get("ap_ip") or "127.0.0.1"
        count = int(params.get("count", 3))
        log_q.put(f"Pinging {target} ({count} packets)...")
        is_windows = platform.system().lower().startswith("win")
        cmd = ["ping", "-n" if is_windows else "-c", str(count), target]
        
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            log_q.put(proc.stdout)
            if proc.returncode == 0:
                return "PASSED", {"target": target, "count": count}
            else:
                log_q.put(proc.stderr)
                return "FAILED", {"target": target, "count": count, "rc": proc.returncode}
        except Exception as e:
            log_q.put(f"Ping failed: {e}")
            return "FAILED", {"error": str(e)}
    
    if action == "iperf3":
        target = (
            params.get("target_ip") or
            params.get("server_ip") or
            tb_ctx.get("server_ip") or
            tb_ctx.get("ap_ip")
        )
        if not target:
            log_q.put("iperf3: 'target_ip' or 'server_ip' required")
            return "FAILED", {"error": "missing target_ip"}
        
        duration = int(params.get("duration_s", 10))
        proto = str(params.get("protocol", "tcp")).lower()
        reverse = bool(params.get("reverse", False))
        parallel = int(params.get("parallel", 1))
        bandwidth = params.get("bandwidth")
        extra = params.get("extra_args", "")
        
        cmd = ["iperf3", "-c", str(target), "-t", str(duration), "-P", str(parallel), "-J"]
        if proto == "udp":
            cmd.append("-u")
            if bandwidth:
                cmd += ["-b", str(bandwidth)]
        if reverse:
            cmd.append("-R")
        if extra:
            if isinstance(extra, list):
                cmd += [str(x) for x in extra]
            elif isinstance(extra, str):
                cmd += extra.split()
        
        log_q.put("Executing iperf3: " + " ".join(cmd))
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 60)
            log_q.put(proc.stdout)
            if proc.returncode != 0:
                log_q.put(proc.stderr)
                return "FAILED", {"rc": proc.returncode}
            
            # Parse JSON summary
            try:
                data = json.loads(proc.stdout)
                end = data.get("end", {})
                if proto == "udp":
                    summ = end.get("sum", {})
                    return "PASSED", {
                        "bps": summ.get("bits_per_second"),
                        "jitter_ms": summ.get("jitter_ms"),
                        "loss_pct": summ.get("lost_percent"),
                    }
                else:
                    bps = (
                        (end.get("sum_received", {}) or {}).get("bits_per_second") or
                        (end.get("sum_sent", {}) or {}).get("bits_per_second")
                    )
                    streams = end.get("streams", [])
                    retrans = None
                    if streams and isinstance(streams, list):
                        sender = streams[0].get("sender", {})
                        retrans = sender.get("retransmits")
                    return "PASSED", {"bps": bps, "retransmits": retrans}
            except Exception:
                return "PASSED", {}
        except Exception as e:
            log_q.put(f"iperf3 failed: {e}")
            return "FAILED", {"error": str(e)}
    
    if action == "tshark_capture":
        iface = params.get("iface") or params.get("interface") or "Wi-Fi"
        duration = int(params.get("duration_s", 10))
        outfile = params.get("outfile") or f"capture_{int(time.time())}.pcapng"
        cap_filter = params.get("capture_filter")
        
        cmd = ["tshark", "-i", str(iface), "-a", f"duration:{duration}", "-w", outfile]
        if cap_filter:
            cmd += ["-f", cap_filter]
        
        log_q.put("Executing tshark: " + " ".join([str(x) for x in cmd]))
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            log_q.put(proc.stdout)
            if proc.returncode != 0:
                log_q.put(proc.stderr)
                return "FAILED", {"rc": proc.returncode}
            
            ok = os.path.exists(outfile)
            size = os.path.getsize(outfile) if ok else 0
            return ("PASSED" if ok and size > 0 else "FAILED"), {"outfile": outfile, "size": size}
        except Exception as e:
            log_q.put(f"tshark failed: {e}")
            return "FAILED", {"error": str(e)}
    
    if action == "ssh_exec":
        if paramiko is None:
            log_q.put("Paramiko not installed. Run: pip install paramiko")
            return "FAILED", {"error": "paramiko_not_installed"}
        
        host = params.get("host") or tb_ctx.get("ap_ip") or tb_ctx.get("sta_ip")
        username = params.get("username") or "root"
        password = params.get("password")
        port = int(params.get("port", 22))
        command = params.get("command")
        
        if not host or not command:
            log_q.put("ssh_exec requires 'host' and 'command'")
            return "FAILED", {"error": "missing host/command"}
        
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=host, port=port, username=username, password=password, timeout=20)
            stdin, stdout, stderr = client.exec_command(command)
            out = stdout.read().decode("utf-8", errors="ignore")
            err = stderr.read().decode("utf-8", errors="ignore")
            rc = stdout.channel.recv_exit_status()
            if out:
                log_q.put(out)
            if err:
                log_q.put(err)
            client.close()
            return ("PASSED" if rc == 0 else "FAILED"), {"rc": rc}
        except Exception as e:
            log_q.put(f"ssh_exec failed: {e}")
            return "FAILED", {"error": str(e)}
    
    log_q.put(f"Unknown builtin action: {action_name}")
    return "FAILED", {"error": f"unknown action {action_name}"}


def execute_external_command(
    template: str,
    params: Dict[str, Any],
    tb_ctx: Dict[str, Any],
    log_q: queue.Queue
) -> Tuple[str, Dict[str, Any]]:
    """
    Run a shell command from template with {param} substitution.
    WARNING: Executes local shell commands; review for safety.
    """
    context = {}
    context.update(tb_ctx)
    context.update(params or {})
    
    try:
        cmd_str = template.format(**context)
    except KeyError as e:
        log_q.put(f"Missing template variable: {e}")
        return "FAILED", {"error": f"missing var {e}"}
    
    log_q.put(f"Executing: {cmd_str}")
    try:
        proc = subprocess.run(cmd_str, shell=True, capture_output=True, text=True)
        log_q.put(proc.stdout)
        if proc.returncode != 0:
            log_q.put(proc.stderr)
            return "FAILED", {"rc": proc.returncode}
        return "PASSED", {"rc": 0}
    except Exception as e:
        log_q.put(f"Command failed: {e}")
        return "FAILED", {"error": str(e)}
