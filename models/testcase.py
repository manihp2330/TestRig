"""Data model for Testcase."""
from typing import Dict, Any, Optional
from ..database import db_query


class Testcase:
    """Testcase model."""
    
    def __init__(self, testcase_id: int = None, **kwargs):
        self.id = testcase_id
        self.name = kwargs.get('name')
        self.description = kwargs.get('description', '')
        self.category = kwargs.get('category', 'General')
        self.action_type = kwargs.get('action_type')
        self.action_name = kwargs.get('action_name', '')
        self.command_template = kwargs.get('command_template', '')
        self.parameters_json = kwargs.get('parameters_json', '{}')
    
    @staticmethod
    def get_by_id(testcase_id: int) -> Optional['Testcase']:
        """Fetch testcase by ID."""
        row = db_query("SELECT * FROM testcases WHERE id=?", (testcase_id,), one=True)
        if row:
            return Testcase(**dict(row))
        return None
    
    @staticmethod
    def get_all() -> list['Testcase']:
        """Fetch all testcases."""
        rows = db_query("SELECT * FROM testcases ORDER BY name")
        return [Testcase(**dict(row)) for row in rows]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'action_type': self.action_type,
            'action_name': self.action_name,
            'command_template': self.command_template,
            'parameters_json': self.parameters_json,
        }
