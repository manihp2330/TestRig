"""Custom logger for streaming logs to Streamlit UI."""
import queue
import streamlit as st
from config import SESSION_KEYS


class TeeLogger:
    """
    Wrap a queue and also push lines into session live buffer.
    Allows Live Logs page to display execution logs in real-time.
    """
    
    def __init__(self, inner_q: queue.Queue):
        self.inner = inner_q
        try:
            st.session_state.setdefault(SESSION_KEYS["live_logs"], [])
        except Exception:
            pass
    
    def put(self, msg):
        """Push message to queue and session buffer."""
        s = str(msg)
        
        # Forward to inner queue
        try:
            self.inner.put(s)
        except Exception:
            pass
        
        # Mirror into session buffer (line-by-line)
        try:
            buf = st.session_state.setdefault(SESSION_KEYS["live_logs"], [])
            buf.append(s)
            # Trim to last 2000 lines to avoid memory bloat
            if len(buf) > 2000:
                del buf[: len(buf) - 2000]
        except Exception:
            pass
    
    def empty(self) -> bool:
        """Check if queue is empty."""
        try:
            return self.inner.empty()
        except Exception:
            return True
    
    def get(self) -> str:
        """Get next message from queue."""
        try:
            return self.inner.get()
        except Exception:
            return ""
