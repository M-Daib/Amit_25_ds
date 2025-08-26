from typing import List, Optional
from patient import Patient
from staff import Staff

class Department:
    """Enhanced Department class with capacity management."""
    
    def __init__(self, name: str, capacity: int = 50):
        """
        Initialize department with configurable capacity.
        
        Args:
            name: Department name
            capacity: Maximum patient capacity
        """
        self.name = name.strip()
        self.capacity = max(10, capacity)  # Minimum capacity 10
        self.patients: List[Patient] = []
        self.staff: List[Staff] = []
        self.dept_code = name[:3].upper() + str(hash(name) % 1000)

    def add_patient(self, patient: Patient) -> bool:
        """Admit patient if capacity allows"""
        if len(self.patients) >= self.capacity:
            print(f"Cannot admit {patient.name}. Department at capacity!")
            return False
            
        self.patients.append(patient)
        print(f"Patient {patient.name} admitted to {self.name}")
        return True

    def add_staff(self, staff: Staff) -> None:
        """Assign staff member to department"""
        staff.transfer_department(self.name)
        self.staff.append(staff)

    def get_active_patients(self) -> List[Patient]:
        """Return list of non-discharged patients"""
        return [p for p in self.patients if not p.is_discharged]

    def get_staff_by_position(self, position: str) -> List[Staff]:
        """Filter staff by position"""
        return [s for s in self.staff
                if s.position.lower() == position.lower()
                and s.is_active]

    def __repr__(self) -> str:
        return f"<Department: {self.name} ({self.dept_code})>"