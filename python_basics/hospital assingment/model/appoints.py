class Appointments:
    def __init__(self):
        self.books={}
        self.counter=1
    def book(self,name,doctorID,date):
        self.books[self.counter]={'name':name,'doctor':doctorID,'date':date}
        self.counter+=1
    def show_books(self):
        for id , data in self.books.items():
            print(f"{id} : name: {data['name']} , Doctor ID: {data['doctor']} , Data: {data['date']}")
