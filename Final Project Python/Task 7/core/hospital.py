from typing import Dict, List, Optional
from department import Department

class Hospital:
    """Enhanced Hospital class with default departments."""
    
    def __init__(self, name: str, location: str):
        """
        Initialize hospital with default departments.
        
        Args:
            name: Hospital name
            location: Physical address
        """
        self.name = name.strip()
        self.location = location.strip()
        self.departments: Dict[str, Department] = {}
        self._initialize_default_departments()

    def _initialize_default_departments(self) -> None:
        """Create common hospital departments"""
        default_depts = {
            "Cardiology": 40,
            "Pediatrics": 35,
            "Emergency": 60,
            "Surgery": 30
        }
        
        for name, capacity in default_depts.items():
            self.add_department(Department(name, capacity))

    def add_department(self, department: Department) -> None:
        """Add a new department"""
        if department.name in self.departments:
            raise ValueError(f"Department {department.name} already exists")
            
        self.departments[department.name] = department
        print(f"Department '{department.name}' added successfully")

    def find_department(self, name: str) -> Optional[Department]:
        """Find department by name (case-insensitive)"""
        lower_name = name.lower()
        for dept_name, dept in self.departments.items():
            if dept_name.lower() == lower_name:
                return dept
        return None

    def get_all_patients(self) -> List[dict]:
        """Get summary of all patients across departments"""
        return [
            {
                "patient": patient,
                "department": dept.name
            }
            for dept in self.departments.values()
            for patient in dept.patients
        ]

    def __repr__(self) -> str:
        return f"<Hospital: {self.name} ({len(self.departments)} departments)>"