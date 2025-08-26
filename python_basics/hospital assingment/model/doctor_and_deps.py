class Doctor:
    _dID=1
    def __init__(self, name, age, dep_id):
        self.name = name
        self.age = age
        self.id = Doctor._dID
        Doctor._dID += 1
        self.dep = {}
        #date  |  name
        self.appointments = {}
        self.D_department(dep_id)

    def D_department(self, dep_id):
        self.dep = Department.departments[dep_id]['name']
   
    def show_data(self):
        print(f"Name: {self.name} age: {self.age} Department: {self.dep}")
    
    def show_appointments(self):
        print(f"Doctor {self.name.capitalize()} appointments:")
        for i, j in self.appointments.items():
            print(f"Patient name: {j['name']} Date: {j['date']}")

class Department:
    departments={
        1:{'name': 'Eyes'},
        2:{'name': 'kids'},
        3:{'name': 'Emergency'},
        4:{'name': 'ICU'},
        5:{'name': 'Radiology'},
    }
    def display(self):
        for i , j in Department.departments.items():
            print(f'{i} : {j['name']}')
