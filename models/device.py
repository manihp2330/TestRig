"""Data model for Device."""
from typing import Dict, Any, Optional
from ..database import db_query


class Device:
    """Device model for testbed devices."""
    
    def __init__(self, device_id: int = None, **kwargs):
        self.id = device_id
        self.testbed_id = kwargs.get('testbed_id')
        self.role = kwargs.get('role')
        self.name = kwargs.get('name')
        self.mgmt_ip = kwargs.get('mgmt_ip')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.extra_json = kwargs.get('extra_json', '{}')
    
    @staticmethod
    def get_by_id(device_id: int) -> Optional['Device']:
        """Fetch device by ID."""
        row = db_query("SELECT * FROM devices WHERE id=?", (device_id,), one=True)
        if row:
            return Device(**dict(row))
        return None
    
    @staticmethod
    def get_by_testbed(testbed_id: int) -> list['Device']:
        """Fetch all devices in a testbed."""
        rows = db_query("SELECT * FROM devices WHERE testbed_id=? ORDER BY id", (testbed_id,))
        return [Device(**dict(row)) for row in rows]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'testbed_id': self.testbed_id,
            'role': self.role,
            'name': self.name,
            'mgmt_ip': self.mgmt_ip,
            'username': self.username,
            'password': self.password,
            'extra_json': self.extra_json,
        }
