from person import Person
from typing import Optional

class Staff(Person):
    """Enhanced Staff class with department support."""
    
    def __init__(self, name: str, age: int, position: str, department: Optional[str] = None):
        """
        Initialize staff member with professional details.
        
        Args:
            position: Job title/position
            department: Optional department assignment
        """
        super().__init__(name, age)
        self.position = position.strip()
        self.department = department.strip() if department else "Unassigned"
        self.staff_id = f"STF-{self.id[:5]}"  # Staff-specific ID
        self.is_active = True

    def transfer_department(self, new_department: str) -> None:
        """Transfer staff to a different department"""
        self.department = new_department.strip()
        print(f"{self.name} transferred to {self.department}")

    def toggle_active_status(self) -> None:
        """Toggle staff active/inactive status"""
        self.is_active = not self.is_active
        status = "active" if self.is_active else "inactive"
        print(f"{self.name} is now {status}")

    def view_info(self) -> str:
        """Get formatted staff information"""
        return (
            f"Staff ID: {self.staff_id}\n"
            f"Name: {self.name}\n"
            f"Position: {self.position}\n"
            f"Department: {self.department}\n"
            f"Status: {'Active' if self.is_active else 'Inactive'}"
        )

    def __repr__(self) -> str:
        return f"<Staff: {self.name} ({self.position})>"