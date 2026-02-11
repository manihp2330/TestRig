# TestRig Automator

Professional WLAN testbed automation tool with modular architecture.

## Features

- **Testbed Management**: Create and manage WLAN testbeds with multiple devices
- **Testcase Builder**: Define test scenarios with builtin or custom actions
- **Testplan Execution**: Organize and execute testcases with progress tracking
- **Device Control**: SSH, ADB, Serial access to test devices
- **Live Monitoring**: Real-time test execution logs and metrics
- **Results Tracking**: Persistent storage with SQLite database

## Project Structure

```
TestRig_Automator/
├── config/              # Configuration & constants
├── database/            # Database layer (schema, operations, connection)
├── models/              # Data models
├── core/                # Core business logic (device mgmt, execution)
├── utils/               # Utility functions & helpers
├── ui/                  # Streamlit UI components
├── main.py              # Application entry point
├── requirements.txt     # Dependencies
├── setup.py             # Package setup
└── README.md            # This file
```

## Installation

### Option 1: Direct Install
```bash
pip install -r requirements.txt
streamlit run main.py
```

### Option 2: Editable Install
```bash
pip install -e .
streamlit run main.py
```

## Usage

### Quick Start
```bash
streamlit run main.py
```

Then navigate to:
- **Dashboard**: View statistics and overview
- **Testbeds**: Create and manage testbeds with devices
- **Testcases**: Define test scenarios
- **Testplans**: Organize testcases into execution plans
- **Runner**: Execute testplans on testbeds
- **Results**: View execution results and logs

### Creating a Testbed
1. Go to Testbeds tab
2. Fill in testbed name and description
3. Click "Create Testbed"
4. Add devices (AP, STA, Controller, etc.) with management IPs
5. Configure optional serial (COM port) or ADB access

### Creating Testcases
1. Go to Testcases tab
2. Select a testbed
3. Choose action type (builtin or custom)
4. Configure action parameters
5. Save testcase

### Running a Testplan
1. Create a testplan and add testcases
2. Go to Runner tab
3. Select testbed and testplan
4. Click "Run"
5. Monitor live progress and logs

## Builtin Actions

- **sleep**: Wait for specified duration
- **ping**: Test IP connectivity
- **iperf3**: Throughput testing (TCP/UDP)
- **tshark_capture**: Packet capture
- **ssh_exec**: Remote command execution

## Architecture

### Modular Design
- **config/**: Constants, settings, enums
- **database/**: SQLite operations, schema
- **models/**: Data classes for testbeds, devices, testcases
- **core/**: Device management, command execution, testplan runner
- **utils/**: Helpers, loggers, SSH utilities
- **ui/**: Streamlit components and pages

### Design Benefits
✅ Separated concerns  
✅ Easy to test and extend  
✅ Clear dependencies  
✅ Professional structure  
✅ Maintainable codebase  

## Database Schema

### Tables
- **testbeds**: Test infrastructure configurations
- **devices**: Physical/virtual devices in testbeds
- **testcases**: Individual test scenarios
- **testplans**: Collections of testcases
- **testplan_items**: Testcase membership in plans
- **runs**: Test execution records
- **run_results**: Individual testcase results

## Configuration

Edit `config/constants.py` for:
- Device roles
- Test statuses
- Node types
- Default delays
- UI settings

## Extending

### Add New Action Type
1. Edit `core/action_executor.py`
2. Add new function in `execute_builtin_action()`
3. Update documentation

### Add New UI Page
1. Create page file in `ui/pages/`
2. Import and route in `main.py`
3. Add navigation entry

### Add New Device Type
1. Update `DEVICE_ROLES` in `config/constants.py`
2. Extend device management logic in `core/device_manager.py`

## Troubleshooting

### Database Issues
- Delete `wlan_automation.db` to reset
- Check database permissions
- Verify Streamlit has write access

### Device Connection Issues
- Verify IP addresses and network connectivity
- Check SSH keys and credentials
- Ensure paramiko and pyserial installed for SSH/serial access

### Streamlit Cache Issues
- Clear browser cache
- Restart Streamlit with `streamlit run main.py --logger.level=debug`

## Requirements

- Python 3.8+
- Streamlit 1.31+
- Paramiko 3.0+ (for SSH)
- pyserial 3.5+ (for Serial)
- Pandas 2.0+

## License

Proprietary - Test Engineering

## Support

For issues and feature requests, contact the test engineering team.
