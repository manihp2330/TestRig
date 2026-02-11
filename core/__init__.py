"""Core module for TestRig Automator."""
from .device_manager import (
    check_reachability,
    device_reachability_status,
    device_reachability_summary,
    reachability_probe_and_cache,
    probe_ip_once,
    probe_com_once,
    probe_adb_once,
)
from .testbed_manager import (
    export_testbed_json,
    import_testbed_from_json,
)
from .action_executor import (
    execute_builtin_action,
    execute_external_command,
)
from .device_shell import (
    run_shell_on_device,
    run_streaming_shell_on_device,
    write_text_file_on_device,
    fetch_file_from_device,
)

__all__ = [
    'check_reachability',
    'device_reachability_status',
    'device_reachability_summary',
    'reachability_probe_and_cache',
    'probe_ip_once',
    'probe_com_once',
    'probe_adb_once',
    'export_testbed_json',
    'import_testbed_from_json',
    'execute_builtin_action',
    'execute_external_command',
    'run_shell_on_device',
    'run_streaming_shell_on_device',
    'write_text_file_on_device',
    'fetch_file_from_device',
]
