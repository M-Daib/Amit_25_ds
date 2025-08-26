def add(x,y):
    print("{}+{}=".format(x,y),x+y)        
def subt(x,y):
    print("{}-{}=".format(x,y),x-y)
def multi(x,y):
    print("{}*{}=".format(x,y),x*y)
def devi(x,y):
    
    if y==0:
        print("You can't divide by zero")
        return
    else:
        print("{}/{}=".format(x,y),x/y)
# running = True
first_time = True
print("What's the Operation you want to perform?\n1-Add 2-Subtraction 3-Multiplication 4-Division 5-To exit")

while True:
    # this block is to skip the first iteration for the another message
    #to make the app more user friendly
    if first_time==True:
        first_time=False
        pass
    else:
        print("Do you want to make another Operation?\n1-Add 2-Subtraction 3-Multiplication 4-Division 5-To exit")

    
    c=int(input())
    if c==1:
        print("Enter two numbers to get their Sum")
        #this is to avoid the error message if user didn't enter valid number
        while True:
            try:
                n1=int(input())
                n2=int(input())
                add(n1,n2)
                break
            except ValueError:
                print("Invalid input\n1- do you want to continue  2-back to home screen")
                # print("enter 1 to back t")
                h=int(input())
                if h==2:
                    break
                else:
                    print("please Enter two valid numbers")
                    pass
    elif c==2:
       print("Enter two numbers to get their Substation")
       while True:
            try:
                n1=int(input())
                n2=int(input())
                subt(n1,n2)
                break
            except ValueError:
                print("Invalid input , 1- do you want to continue 2-back to home screen")
                # print("enter 1 to back t")
                h=int(input())
                if h==2:
                    break
                else:
                    print("please Enter two valid numbers")
                    pass
    elif c==3:
        print("Enter two numbers to get their Multipication")
        while True:
            try:
                n1=int(input())
                n2=int(input())
                multi(n1,n2)
                break
            except ValueError:
                print("Invalid input , 1- do you want to continue 2-back to home screen")
                # print("enter 1 to back t")
                h=int(input())
                if h==2:
                    break
                else:
                    print("please Enter two valid numbers")
                    pass
    elif c==4:
        print("Enter two numbers to get their Division")
        while True:
            try:
                n1=int(input())
                n2=int(input())
                devi(n1,n2)
                break
            except ValueError:
                print("Invalid input , 1- do you want to continue 2-back to home screen")
                # print("enter 1 to back t")
                h=int(input())
                if h==2:
                    break
                else:
                    print("please Enter two valid numbers")
                    pass
    elif c==5:
        print("Good bye")
        break
    else :
        print("please enter valid choice...")


