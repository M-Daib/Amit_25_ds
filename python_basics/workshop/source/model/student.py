class Student:
    _id_counter=1
    
    def __init__(self,name):
        self.name=name
        self.id=Student._id_counter
        Student._id_counter+=1
        self.grades={}
        self.courses=[]
    
    def add_grade(self,course_id,grade):
        self.grades[course_id]=grade
    
    def enroll_course(self,course_name):
        self.courses.append(course_name)
    def remove_course(self,course_name):
        self.courses.remove(course_name)