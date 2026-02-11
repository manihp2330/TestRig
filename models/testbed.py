"""Data model for Testbed."""
from typing import Dict, Any, Optional
from ..database import db_query


class Testbed:
    """Testbed model."""
    
    def __init__(self, testbed_id: int = None, **kwargs):
        self.id = testbed_id
        self.name = kwargs.get('name')
        self.description = kwargs.get('description', '')
    
    @staticmethod
    def get_by_id(testbed_id: int) -> Optional['Testbed']:
        """Fetch testbed by ID."""
        row = db_query("SELECT * FROM testbeds WHERE id=?", (testbed_id,), one=True)
        if row:
            return Testbed(**dict(row))
        return None
    
    @staticmethod
    def get_by_name(name: str) -> Optional['Testbed']:
        """Fetch testbed by name."""
        row = db_query("SELECT * FROM testbeds WHERE name=?", (name,), one=True)
        if row:
            return Testbed(**dict(row))
        return None
    
    @staticmethod
    def get_all() -> list['Testbed']:
        """Fetch all testbeds."""
        rows = db_query("SELECT * FROM testbeds ORDER BY name")
        return [Testbed(**dict(row)) for row in rows]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }
