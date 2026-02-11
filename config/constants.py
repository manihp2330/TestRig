"""Constants and enums for TestRig Automator."""
import os

# Database
DB_PATH = os.path.join(
    os.path.dirname(__file__) or os.getcwd(), 
    "wlan_automation.db"
)

# Device roles
DEVICE_ROLES = [
    "AP",
    "STA", 
    "Controller",
    "Ixia", 
    "Attenuator",
    "Switch",
    "Server",
    "Sniffer",
    "Backbone",
    "Other"
]

# Test statuses
TEST_STATUSES = [
    "RUNNING",
    "PASSED",
    "FAILED",
    "PARTIAL",
    "ABORTED",
    "SKIPPED"
]

# Action types
ACTION_TYPES = [
    "builtin",
    "external",
    "node_graph"
]

# Builtin actions
BUILTIN_ACTIONS = [
    "sleep",
    "ping",
    "iperf3",
    "tshark_capture",
    "ssh_exec"
]

# Node types for graph execution
NODE_TYPES = [
    'config_write',
    'custom_cmd',
    'verify_connectivity',
    'iperf_between_devices',
    'tcpdump',
    'parallel_group',
    'iteration_group',
    'live_tail',
    'assert_expr'
]

# Default node delays (seconds)
DEFAULT_NODE_DELAYS = {
    "config_write": 0,
    "custom_cmd": 0,
    "verify_connectivity": 0,
    "iperf_between_devices": 2,
    "tcpdump": 1,
    "tshark_capture": 1,
    "parallel_group": 0,
    "iteration_group": 0,
    "verify_sniffer": 0,
    "live_tail": 0,
    "assert_expr": 0,
}

# Testcase categories
TESTCASE_CATEGORIES = [
    "Connectivity",
    "Throughput",
    "Roaming",
    "Security",
    "Utility",
    "General"
]

# CSV field names for import/export
CSV_HEADERS = {
    "devices": ["ID", "Testbed", "Role", "Name", "Mgmt IP", "Username", "COM Port", "ADB ID"],
    "testcases": ["ID", "Name", "Category", "Action Type", "Parameters"],
    "testplans": ["ID", "Name", "Description"],
}
