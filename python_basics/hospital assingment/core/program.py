from model.appoints import *
from model.doctor_and_deps import *

class main:
    def __init__(self):
        self.booking=Appointments()
        self.doctors={}
    def book_appointment(self,name,doctorid,date):#*done✅
        #! gone the the Appointments class
        appointmentID=self.booking.counter
        self.booking.book(name,doctorid,date)
        if doctorid in self.doctors:
            #to check for the right doctor
            doctor=self.doctors[doctorid]
            #! add the appointment for the doctor
            doctor.appointments[appointmentID]={'name':name ,'date': date}
            print(f"{name.capitalize()} booked with Doctor {self.doctors[doctorid].name.capitalize()}")
        else:
            print("Doctor not found")

        
    def add_new_doctor(self,name,age,dep):#*done✅
        doctor=Doctor(name,age,dep)
        self.doctors[doctor.id]=doctor
        print('Doctor added successfully')

    def display_appointmetns(self): #*done✅
        if self.booking.books:
            #! show all anointments 
            self.booking.show_books()
        else:
            print('Their is NO appointments right now')
            return 0
    def display_doctor_appointments(self,doctorid):#*done✅
        self.doctors[doctorid].show_appointments()

    def show_doctors(self):
        if self.doctors:
            for i , j in self.doctors.items():
                                    #! 'j.name' because it's an object
                print(f"{i} : Doctor {j.name.capitalize()}")
        else:
            print('their is no doctors')
            return 0
    def show_departments(self):
        d=Department()
        d.display()
    def doctor_date(self,dID):
        self.doctors[dID].show_data()