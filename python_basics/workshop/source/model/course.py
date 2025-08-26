class Course:
    _id_counter_course=1
    def __init__(self,name):
        self.name=name
        self.course_id=Course._id_counter_course
        Course._id_counter_course+=1
        self.enrolled_students=[]
    def enroll_student(self,student_name):
        self.enrolled_students.append(student_name)

    def remove_student(self,student_name):
         if student_name in self.enrolled_students:
            self.enrolled_students.remove(student_name)