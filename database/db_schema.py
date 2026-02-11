"""Database schema initialization and migrations."""
import json
from typing import Tuple
from .db_connection import get_conn
from .operations import db_exec, db_query


def init_db():
    """Initialize database schema with all tables."""
    db_exec(
        """
        CREATE TABLE IF NOT EXISTS testbeds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT ''
        )
        """
    )
    db_exec(
        """
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            testbed_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            mgmt_ip TEXT DEFAULT '',
            username TEXT DEFAULT '',
            password TEXT DEFAULT '',
            extra_json TEXT DEFAULT '{}',
            FOREIGN KEY(testbed_id) REFERENCES testbeds(id) ON DELETE CASCADE
        )
        """
    )
    db_exec(
        """
        CREATE TABLE IF NOT EXISTS testcases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT '',
            category TEXT DEFAULT 'General',
            action_type TEXT NOT NULL,
            action_name TEXT DEFAULT '',
            command_template TEXT DEFAULT '',
            parameters_json TEXT DEFAULT '{}'
        )
        """
    )
    db_exec(
        """
        CREATE TABLE IF NOT EXISTS testplans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT DEFAULT ''
        )
        """
    )
    db_exec(
        """
        CREATE TABLE IF NOT EXISTS testplan_items (
            plan_id INTEGER NOT NULL,
            testcase_id INTEGER NOT NULL,
            seq INTEGER NOT NULL,
            PRIMARY KEY (plan_id, seq),
            FOREIGN KEY(plan_id) REFERENCES testplans(id) ON DELETE CASCADE,
            FOREIGN KEY(testcase_id) REFERENCES testcases(id) ON DELETE CASCADE
        )
        """
    )
    db_exec(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uniq_plan_tc
        ON testplan_items (plan_id, testcase_id)
        """
    )
    db_exec(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL,
            testbed_id INTEGER NOT NULL,
            start_ts TEXT,
            end_ts TEXT,
            status TEXT DEFAULT 'RUNNING',
            FOREIGN KEY(plan_id) REFERENCES testplans(id),
            FOREIGN KEY(testbed_id) REFERENCES testbeds(id)
        )
        """
    )
    db_exec(
        """
        CREATE TABLE IF NOT EXISTS run_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL,
            testcase_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            logs TEXT DEFAULT '',
            metrics_json TEXT DEFAULT '{}',
            duration_s REAL DEFAULT 0,
            FOREIGN KEY(run_id) REFERENCES runs(id) ON DELETE CASCADE,
            FOREIGN KEY(testcase_id) REFERENCES testcases(id) ON DELETE CASCADE
        )
        """
    )
    db_exec(
        """
        CREATE TABLE IF NOT EXISTS device_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            testbed_id INTEGER NOT NULL,
            dut_device_id INTEGER NOT NULL,
            backbone_device_id INTEGER NOT NULL,
            UNIQUE(testbed_id, dut_device_id, backbone_device_id),
            FOREIGN KEY(testbed_id) REFERENCES testbeds(id) ON DELETE CASCADE,
            FOREIGN KEY(dut_device_id) REFERENCES devices(id) ON DELETE CASCADE,
            FOREIGN KEY(backbone_device_id) REFERENCES devices(id) ON DELETE CASCADE
        )
        """
    )

    # Schema migration: ensure testcases.testbed_id exists (if needed)
    try:
        cols = db_query("PRAGMA table_info(testcases)")
        colnames = [c["name"] for c in cols] if cols else []
        if "testbed_id" not in colnames:
            db_exec("ALTER TABLE testcases ADD COLUMN testbed_id INTEGER")
    except Exception:
        pass


def seed_examples_if_empty():
    """Seed database with example content if empty."""
    if not db_query("SELECT 1 FROM testcases LIMIT 1"):
        # Sleep example
        db_exec(
            """
            INSERT OR IGNORE INTO testcases (name, description, category, action_type, action_name, parameters_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "Sleep 5s",
                "Simulated wait to demonstrate progress",
                "Utility",
                "builtin",
                "sleep",
                json.dumps({"duration_s": 5}),
            ),
        )
        # Ping example
        db_exec(
            """
            INSERT OR IGNORE INTO testcases (name, description, category, action_type, action_name, parameters_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "Ping target",
                "Ping a target IP from the local machine",
                "Connectivity",
                "builtin",
                "ping",
                json.dumps({"target_ip": "8.8.8.8", "count": 3}),
            ),
        )
        # iperf3 example
        db_exec(
            """
            INSERT OR IGNORE INTO testcases (name, description, category, action_type, action_name, parameters_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "iPerf3 TCP 10s",
                "Run iperf3 TCP test for 10s to AP/server",
                "Throughput",
                "builtin",
                "iperf3",
                json.dumps({"duration_s": 10}),
            ),
        )
        # tshark capture example
        db_exec(
            """
            INSERT OR IGNORE INTO testcases (name, description, category, action_type, action_name, parameters_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "Tshark 5s capture",
                "Capture 5 seconds on default iface to demo_capture.pcapng",
                "Utility",
                "builtin",
                "tshark_capture",
                json.dumps({"duration_s": 5, "outfile": "demo_capture.pcapng"}),
            ),
        )
        # Example testbed
        db_exec(
            "INSERT OR IGNORE INTO testbeds (name, description) VALUES (?, ?)",
            ("Sample Testbed", "Sample bed with AP and STA for demo"),
        )
        tb = db_query("SELECT id FROM testbeds WHERE name=?", ("Sample Testbed",), one=True)
        if tb:
            tbid = tb["id"]
            db_exec(
                """
                INSERT INTO devices (testbed_id, role, name, mgmt_ip, username, password, extra_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tbid,
                    "AP",
                    "AP-1",
                    "192.168.1.2",
                    "root",
                    "password",
                    json.dumps({"model": "GenericAP", "com_port": "COM3", "adb_serial": "DEVICEID"}),
                ),
            )
            db_exec(
                """
                INSERT INTO devices (testbed_id, role, name, mgmt_ip)
                VALUES (?, ?, ?, ?)
                """,
                (tbid, "STA", "STA-1", "192.168.1.100"),
            )
        # Example plan
        db_exec(
            "INSERT OR IGNORE INTO testplans (name, description) VALUES (?, ?)",
            ("Demo Plan", "Sleep, Ping, iPerf3, Tshark"),
        )
        plan = db_query("SELECT id FROM testplans WHERE name=?", ("Demo Plan",), one=True)
        tc_sleep = db_query("SELECT id FROM testcases WHERE name=?", ("Sleep 5s",), one=True)
        tc_ping = db_query("SELECT id FROM testcases WHERE name=?", ("Ping target",), one=True)
        if plan and tc_sleep and tc_ping:
            db_exec("INSERT OR IGNORE INTO testplan_items (plan_id, testcase_id, seq) VALUES (?, ?, ?)", (plan["id"], tc_sleep["id"], 1))
            db_exec("INSERT OR IGNORE INTO testplan_items (plan_id, testcase_id, seq) VALUES (?, ?, ?)", (plan["id"], tc_ping["id"], 2))
