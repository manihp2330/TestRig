"""Database query and execute operations."""
from typing import Tuple, Dict, Any, List
from .db_connection import get_conn


def db_exec(q: str, args: Tuple = ()):
    """Execute a database query without returning results."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(q, args)
    conn.commit()
    return cur


def db_query(q: str, args: Tuple = (), one: bool = False):
    """Execute a SELECT query and return results as list of dicts."""
    cur = get_conn().cursor()
    cur.execute(q, args)
    rows = cur.fetchall()
    # Normalize to list[dict] so callers can use .get(...) safely
    rows = [dict(r) for r in rows]
    return (rows[0] if rows else None) if one else rows
