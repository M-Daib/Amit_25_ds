                            #all this are classes
from PyQt5.QtWidgets import QApplication, QMainWindow,QStatusBar
from PyQt5 import uic
from PyQt5.QtCore import QTimer
import sys
import time
#to link with data base
import psycopg2


        #inheritance
class Main(QMainWindow):
    #the goal from init is to make every thing ready for the window only
    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi("C:/Users/COMPUMARTS/Downloads/DEPI/Depi_Amit_BNS3_AIS4_S1/application workshop/std.ui", self)  # Make sure student.ui is in the same folder
        self.InitUI()
        
        self.handel_db_conn()
    
    
    def InitUI(self):
        #change window title
        #! self for ensuring that every thing is done with the same object
        self.setWindowTitle("my System")
        #make tab bar not visible
        self.tabWidget.tabBar().setVisible(False)
        
        #! to make link every button with his function
        self.handle_btn()
        # Explicitly create and set a status bar
        #here i created a status bar as variable
        #?this allows me to use the status bar again in where in obj
        #!  _ in first mean that variable is only inside the class and dont use it out side
        self._status_bar = QStatusBar(self)
             #this is a function not a variable
             #? here i said make a status bar and give it a variable have status bar
             #*this is a short way but not flexible
             #self.setstatusbar(QMainWindow(self))        
        self.setStatusBar(self._status_bar)
        ### changes in the run time
        print("hello")


    def handel_db_conn(self):
         self.db = psycopg2.connect(
            host="localhost",
            database="student_management",
            user="postgres",
            password="1212")
         self.curr = self.db.cursor()
         print("connection is Done!")
          
    def handle_btn(self):
        self.std_add_btn.clicked.connect(self.add_std_info)
        self.std_update_btn.clicked.connect(self.update_std_info)
        self.std_del_btn.clicked.connect(self.delete_std_info)
        
        
        self.btn_search.clicked.connect(self.search)
    ########################################
    
    
    
    def search(self):
        print("search")
        print(self.listWidget.row(self.listWidget.currentItem()))
    ## student_info
    
    
    ## add student info
    def add_std_info(self):
        #variables we have
        #! we don't add self. because its a local variable and we need it for short time
        std_id =self.std_Id_txt.text()
        std_nme = self.std_name_txt.text()
        std_email = self.std_email_txt.text()
        std_phone = self.std_phone_txt.text()
        # std_phone = self.std_phone_txt.currentIndex()
        self.curr.execute('INSERT INTO students (student_id, name, email, phone) VALUES (%s, %s, %s, %s)',
                    (std_id, std_nme, std_email, std_phone))
        self.curr.execute('INSERT INTO enrollments (student_id) VALUES (%s)',
                    (std_id,))
        self.db.commit()
        
        self.std_Id_txt.setText("")
        self.std_name_txt.setText("")
        self.statusBar().showMessage("Student info added successfully")
        # Removed time.sleep(10) to avoid freezing the UI
        # Optionally, you can use a QTimer to clear the message after a delay
        self.statusBar().showMessage("Student info added successfully")
        #!this makes app lag
        # time.sleep(10)
                        #ms ,    need a function to do after message
                                       #statusBar is a function not a variable
        QTimer.singleShot(3000, lambda: self.statusBar().clearMessage())

        self.statusBar().showMessage("Student info added successfully")


    #update student info
    def update_std_info(self):
        pass
    ## Delete Student
    def delete_std_info(self):
        pass
    ############################################
    #############################################
    #############################################
    
    ########################################
    ## enrollment _info ############
    def add_enroll_info(self):
        pass
    #update student info
    def update_enroll_info(self):
        pass
    ## Delete Student
    def delete_enroll_info(self):
        pass
    ########################################
    ## Courses _info ############
    def add_course_info(self):
        pass
    #update student info
    def update_course_info(self):
        pass
    ## Delete Student
    def delete_course_info(self):
        pass
      ########################################
    ## Instructors_info ############
    def add_instructor_info(self):
        pass
    #update student info
    def update_instructor_info(self):
        pass
    ## Delete Student
    def delete_instructor_info(self):
        pass
    
    
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())
