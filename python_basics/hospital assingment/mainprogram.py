from core.program import *
import os
def clearscreen():
    os.system('cls')
class mainsystem:
    pr=main()
    def mainmenu(self):
        print('-'*30)
        print('what do you want to perform')
        print('1-Book appointment')
        print('2-Appointments')
        print('3-New doctor')
        print('4-Doctors')
        print('5-Doctor appointments')
        print('6-Doctor data')
        print('7-Exit')
    def run(self):
        clearscreen()
        while True:
            self.mainmenu()
            c=int(input('Please enter your choice\n'))
            if c==1:
                clearscreen()

                if mainsystem.pr.show_doctors()==0:
                    print('sorry for that')
                    continue
                else: 
                    print("with which doctor:")
                    cid=int(input())
                    print("Please enter Patient name:")
                    cname=input()
                    print('Which date(dd-mm-yyyy):')
                    cdate=input()
                    mainsystem.pr.book_appointment(cname,cid,cdate)
            elif c==2 :
                clearscreen()
                mainsystem.pr.display_appointmetns()
            elif c==3:
                clearscreen()
                cname=input('Enter doctor name:\n')
                cage=int(input('Enter doctor age:\n'))
                mainsystem.pr.show_departments()
                cdep=int(input('Enter department ID:\n'))
                mainsystem.pr.add_new_doctor(cname,cage,cdep)
            elif c==4 :
                clearscreen()
                mainsystem.pr.show_doctors()
            elif c==5 :
                clearscreen()
                mainsystem.pr.show_doctors()
                print('Please enter doctor ID:')
                id=int(input())
                mainsystem.pr.display_doctor_appointments(id)
            elif c==6 :
                clearscreen()
                mainsystem.pr.show_doctors()
                print('Please enter doctor ID:')
                id=int(input())
                mainsystem.pr.doctor_date(id)
            elif c==7:
                clearscreen()
                print('Exiting...')
                exit()
            else:
                print('Please enter valid choice')
            
a=mainsystem()
a.run()
