"""Data model for Testplan."""
from typing import Dict, Any, Optional, List
from ..database import db_query


class Testplan:
    """Testplan model."""
    
    def __init__(self, testplan_id: int = None, **kwargs):
        self.id = testplan_id
        self.name = kwargs.get('name')
        self.description = kwargs.get('description', '')
    
    @staticmethod
    def get_by_id(testplan_id: int) -> Optional['Testplan']:
        """Fetch testplan by ID."""
        row = db_query("SELECT * FROM testplans WHERE id=?", (testplan_id,), one=True)
        if row:
            return Testplan(**dict(row))
        return None
    
    @staticmethod
    def get_all() -> list['Testplan']:
        """Fetch all testplans."""
        rows = db_query("SELECT * FROM testplans ORDER BY name")
        return [Testplan(**dict(row)) for row in rows]
    
    def get_testcases(self) -> List[Dict[str, Any]]:
        """Get all testcases in this testplan."""
        rows = db_query(
            """
            SELECT tc.* FROM testplan_items ti
            JOIN testcases tc ON tc.id = ti.testcase_id
            WHERE ti.plan_id = ? ORDER BY ti.seq
            """,
            (self.id,)
        )
        return rows or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }
