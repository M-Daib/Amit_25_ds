from hospital import Hospital
from department import Department
from patient import Patient
from staff import Staff

def initialize_sample_data():
    """Initialize sample data for demonstration"""
    hospital = Hospital("City General Hospital", "123 Main St")
    
    # Get existing department
    cardiology = hospital.find_department("Cardiology")
    
    if cardiology:
        # Add sample patients
        patient1 = Patient("Alice Johnson", 35, "Hypertension monitoring")
        patient2 = Patient("Bob Smith", 52, "Post-operative care")
        
        cardiology.add_patient(patient1)
        cardiology.add_patient(patient2)
        
        # Add sample staff
        doctor = Staff("Dr. Sarah Miller", 42, "Cardiologist", "Cardiology")
        nurse = Staff("Emma Wilson", 28, "Head Nurse", "Cardiology")
        
        cardiology.add_staff(doctor)
        cardiology.add_staff(nurse)
        
        # Demonstrate features
        print("\n--- Hospital Summary ---")
        print(f"Hospital: {hospital.name}")
        print(f"Total Departments: {len(hospital.departments)}")
        
        print("\n--- Cardiology Department ---")
        print(f"Patients: {len(cardiology.patients)}")
        print(f"Staff: {len(cardiology.staff)}")
        
        print("\n--- Patient Discharge Example ---")
        patient1.discharge("Recovered well, follow-up in 2 weeks")
        print(patient1.view_record())
        
    return hospital

if __name__ == "__main__":
    hospital = initialize_sample_data()