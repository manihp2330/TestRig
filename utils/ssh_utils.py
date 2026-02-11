"""SSH utilities using paramiko."""
from typing import Tuple
import paramiko
from ..config import UI_DEFAULTS


class SSHClient:
    """Wrapper around paramiko for SSH operations."""
    
    def __init__(self, host: str, username: str = "root", password: str = None, 
                 key_path: str = None, key_passphrase: str = None, port: int = 22):
        self.host = host
        self.username = username
        self.password = password
        self.key_path = key_path
        self.key_passphrase = key_passphrase
        self.port = port
        self.client = None
    
    def connect(self, timeout: int = UI_DEFAULTS["ssh_timeout"]) -> bool:
        """Establish SSH connection."""
        if self.client is not None:
            return True
        
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.key_path:
                pkey = self._load_key()
                self.client.connect(
                    hostname=self.host,
                    username=self.username,
                    pkey=pkey,
                    timeout=timeout,
                    allow_agent=True,
                    look_for_keys=True
                )
            else:
                self.client.connect(
                    hostname=self.host,
                    username=self.username,
                    password=self.password if self.password else None,
                    timeout=timeout,
                    allow_agent=True,
                    look_for_keys=True
                )
            return True
        except Exception as e:
            self.client = None
            raise e
    
    def _load_key(self):
        """Load SSH private key."""
        try:
            return paramiko.RSAKey.from_private_key_file(
                self.key_path, 
                password=self.key_passphrase
            )
        except Exception:
            try:
                return paramiko.Ed25519Key.from_private_key_file(
                    self.key_path,
                    password=self.key_passphrase
                )
            except Exception:
                return None
    
    def exec_command(self, command: str, timeout: int = UI_DEFAULTS["command_timeout"]) -> Tuple[int, str, str]:
        """Execute command and return (rc, stdout, stderr)."""
        if self.client is None:
            self.connect()
        
        stdin, stdout, stderr = self.client.exec_command(command, timeout=timeout)
        out = stdout.read().decode("utf-8", errors="ignore")
        err = stderr.read().decode("utf-8", errors="ignore")
        rc = stdout.channel.recv_exit_status()
        return rc, out, err
    
    def close(self):
        """Close SSH connection."""
        if self.client:
            self.client.close()
            self.client = None
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
