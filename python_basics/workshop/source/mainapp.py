import os
from core.system_manager import SystemManager
def clearsreen():
    os.system("cls")
class core:
    
    sm = SystemManager()
    def lists(self):
        core.sm.show_students()
        print("-------------------")

        core.sm.show_courses()
    def mainmenu(self):
        bold="\033[1m"
        red="\033[91m"
        green="\033[92m"
        reset="\033[0m"

        # clearsreen()
        print(f"{green}HI,\nWhat do you want to perform{reset}")
        print("--------------------------------------------------------------------------")
        print("1-Add student",end="                   ")
        print("2-Remove Student")
        print("3-Add Course",end="                    ")
        print("4-Remove Course")
        print("5-Enroll student to course",end="      ")
        print("6-remove student form course")
        print("7-Give grade to student",end="         ")
        print("8-Display grades for student")
        print("9-Show students in specific Course",end="      ")
        print("10-Show specific Student courses")
        print("11-Show all students and courses")
        print(f"{' '*23}{red}12-Exit{reset}")
        print("--------------------------------------------------------------------------")




    def startprogram(self):
        bold="\033[1m"
        red="\033[91m"
        green="\033[92m"
        reset="\033[0m"
        print("--------------------------------------------------------------------------")
        clearsreen()
        while True:
            self.mainmenu()
            c=int(input("Enter your choice:"))
            if c==1:
                clearsreen()
                print(f"{bold}{green}Add student{reset}")
                print("Enter student name:")
                name=input()
                core.sm.add_student(name)
            elif c==2:
                clearsreen()
                print(f"{bold}{red}Remove student{reset}")
                print("Enter student ID:")
                id=int(input())
                core.sm.remove_student(id)
            elif c==3:
                clearsreen()
                print(f"{bold}{green}Add new Course{reset}")
                print("Enter course name:")
                name=input()
                core.sm.add_course(name)
            elif c==4:
                clearsreen()
                print(f"{bold}{red}Remove Course{reset}")
                
                print("Enter course ID:")
                id=int(input())
                core.sm.remove_course(id)
            elif c==5:
                clearsreen()
                print(f"{bold}{green}Enroll Student to course{reset}")
                sid=int(input("Enter Student ID:"))
                cid=int(input("Enter Course ID"))
                core.sm.enroll_studentToCourse(sid,cid)
            elif c==6:
                clearsreen()
                print(f"{bold}{red}remove Student from course{reset}")
                sid=int(input("Enter Student ID:"))
                cid=int(input("Enter Course ID"))
                core.sm.remove_studentFromCourse(sid,cid)
            elif c==7:
                clearsreen()
                print(f"{bold}{green}Give Grade{reset}")
                sid=int(input("Enter Student ID:"))
                cid=int(input("Enter Course ID"))
                grade=int(input("Enter grade"))
                core.sm.give_grade(sid,cid,grade)
            elif c==8:
                clearsreen()
                print(f"{bold}{green}Show grades{reset}")
                sid=int(input("Enter student ID:"))
                core.sm.show_grades(sid)
            elif c==9:
                clearsreen()
                print(f"{bold}{green}Show students enrolled in specific Course{reset}")
                cid=int(input("Enter Course ID:"))
                core.sm.students_InCourses(cid)
            elif c==10:
                clearsreen()
                print(f"{bold}{green}Show specific Student courses{reset}")
                sid=int(input("Enter Student ID:"))
                core.sm.student_courses(sid)
            elif c==11:
                print("-------------------")
                self.lists()
            elif c==12:
                print("Good Bye")
                break
        

m=core()
m.startprogram()