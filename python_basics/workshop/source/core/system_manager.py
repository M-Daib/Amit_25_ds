from model.course import Course
from model.student import Student

class SystemManager:
    def __init__(self):
        self.students={}
        self.courses={}
    def add_student(self,name):
        student=Student(name)
        self.students[student.id]=student
        print(f"Student {student.name.capitalize()} added successfully")
        print("----------------------------------------")

    def remove_student(self,student_id):
        if student_id in self.students:
            #! to get the student object from dict and check is he in a course or not
            student=self.students[student_id]
            if not student.courses:
                del self.students[student_id]
            else: 
                print("Student is in a course")
        else:
            print("Invalid student ID")
    def add_course(self,name):
        course=Course(name)
        self.courses[course.course_id]=course
        print(f"Course {course.name} added successfully")
        print("----------------------------------------")

    def remove_course(self,course_id):
        if course_id in self.courses:
            course=self.courses[course_id]
            if not course.enrolled_students:
                del self.courses[course_id]
                print("Course removed successfully")
                print("----------------------------------------")

            else:
                print("Their is students studying this course")
                print("----------------------------------------")

    def enroll_studentToCourse(self,student_id,course_id):
        #! to access the classes and add student to course and add the course in student
        student=self.students[student_id]
        course=self.courses[course_id]
        if course.name in student.courses:
            print("The student already in the course")
        else:
            student.enroll_course(course.name)
            course.enroll_student(student.name)
            print(f"Student {student.name} successfully added to course {course.name}")
            print(f"The courses {student.name} enrolled in is:{student.courses}")
            print(f"The students enrolled in {course.name} course is:{course.enrolled_students}")
            print("--------------------------------------------------")

    def remove_studentFromCourse(self,student_id,course_id):
        student=self.students[student_id]
        course=self.courses[course_id]
        course.remove_student(student.name)
        student.remove_course(course.name)
        print(f"{student.name.capitalize()} doesn't take {course.name} any more ")
    def give_grade(self,student_id,course_id,gradee):
        student=self.students[student_id]
        course=self.courses[course_id]
        student.add_grade(course.course_id,gradee)
        print(f"{student.name} Have a grade {student.grades[course.course_id]} in {course.name}")
        print("----------------------------------------")

    def show_grades(self,student_id):
        student=self.students[student_id]
        print(student.name.capitalize(),"Grades")
        for key,value in student.grades.items():
            course=self.courses[key]
            print(f"{course.name}:{value}",end=" , ")
    def show_students(self):
        print("ID | name")
        for key, value in self.students.items():
            print(f"{key}  : {value.name}")
    def show_courses(self):
        print("ID | course")
        for key, value in self.courses.items():
            print(f"{key}  : {value.name}")
    def students_InCourses(self,course_id):
        course=self.courses[course_id]
        print(f"Students in {course.name} course is {course.enrolled_students}")
    def student_courses(self,student_id):
        student=self.students[student_id]
        print(f"Student {student.name.capitalize()} have cousrses {student.courses}")


m=SystemManager()
m.add_course("DS")
m.add_course("ML")
m.add_student("fares")
m.add_student("ali")
m.enroll_studentToCourse(1,1)
m.enroll_studentToCourse(1,2)
m.enroll_studentToCourse(2,1)
m.show_students()
m.show_courses()
m.students_InCourses(1)
m.student_courses(1)