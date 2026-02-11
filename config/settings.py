"""Runtime settings for TestRig Automator."""

# Export retention days
EXPORT_RETENTION_DAYS = 2

# Live log buffer size
LIVE_LOG_MAX_LINES = 2000

# Session state keys
SESSION_KEYS = {
    "db_conn": "_db_conn",
    "live_logs": "_live_log_lines",
    "css_done": "_rig_css_done",
    "quickrun_evt": "_quickrun_evt",
    "dev_status_cache": "_dev_status",
    "tb_reach_cache": "_tb_reach_cache",
    "import_stage": "_import_stage",
    "import_payload": "_import_payload",
}

# UI defaults
UI_DEFAULTS = {
    "serial_baudrate": 115200,
    "iperf3_port": 5201,
    "ssh_timeout": 20,
    "command_timeout": 60,
}
