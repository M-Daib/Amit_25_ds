from datetime import datetime
from typing import Optional
from person import Person

class Patient(Person):
    """Enhanced Patient class with medical record tracking."""
    
    def __init__(self, name: str, age: int, medical_record: str):
        """
        Initialize a patient with admission tracking.
        
        Args:
            medical_record: Initial medical notes
        """
        super().__init__(name, age)
        self.medical_record = medical_record.strip()
        self.admission_date = datetime.now()
        self.is_discharged = False
        self.discharge_date: Optional[datetime] = None
        self.patient_id = f"PAT-{self.id[:5]}"  # Patient-specific ID

    def discharge(self, notes: str = "") -> None:
        """Mark patient as discharged with optional notes"""
        if self.is_discharged:
            raise ValueError("Patient already discharged")
            
        self.is_discharged = True
        self.discharge_date = datetime.now()
        self.medical_record += f"\n[Discharge Note] {notes}"

    def view_record(self) -> str:
        """Get formatted medical record with admission status"""
        status = "Discharged" if self.is_discharged else "Admitted"
        return (
            f"Patient ID: {self.patient_id}\n"
            f"Status: {status}\n"
            f"Record: {self.medical_record}"
        )

    def __repr__(self) -> str:
        return f"<Patient: {self.name} ({self.patient_id})>"