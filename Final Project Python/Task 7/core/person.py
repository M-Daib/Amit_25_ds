import uuid
from datetime import datetime
from typing import Optional

class Person:
    """Base class for all people in the hospital with improved features."""
    
    def __init__(self, name: str, age: int) -> None:
        """
        Initialize a person with auto-generated ID, name, and age.
        
        Args:
            name: Full name of the person
            age: Age in years (must be positive)
        """
        if age <= 0:
            raise ValueError("Age must be a positive number")
            
        self.id = self._generate_id()
        self.name = name.strip()
        self.age = age
        self.created_at = datetime.now()

    def _generate_id(self) -> str:
        """Generate a unique 8-character ID using UUID"""
        return uuid.uuid4().hex[:8]

    def view_info(self) -> str:
        """Return formatted person information"""
        return f"ID: {self.id} | Name: {self.name} | Age: {self.age}"

    def __repr__(self) -> str:
        return f"<Person: {self.name} ({self.id})>"