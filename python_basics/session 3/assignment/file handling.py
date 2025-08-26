import os
import random
def createfolders(path):
    '''
    this function for creating 5 folders into the given folder and arrang their names in ascending
    order
    :parameter: takes the path we want to add create folders into 
    :parameter type: string storing the path
    :if the input form user not valid: it will give and error because of we are dealing with os libirary
    that needs a path not any thing else
     :return: none
     :return: none

    '''
    
    for i in range(5):
        j=os.path.join(path,f"dir{i+1}")
        os.makedirs(j,exist_ok=True)
    length=len(os.listdir(path))    

def deletehalf(path):
    '''
    this function for delete the random of half folders in main folder

    :parameter: takes the path we want to delete subfolders from 
    :parameter type: string storing the path
    :if the input form user not valid: it will give and error because of we are dealing with os libirary
    that needs a path not any thing else
     :return: none
     :return: none

    
    
    '''
    files=[f for f in os.listdir(path)]
    # this to delete random folders not the first five
    random.shuffle(files)
    todelete=files[:len(files)//2]
    for i in todelete:
        os.rmdir(os.path.join(path,i))
    print(os.listdir(path))

path="C:/Users/COMPUMARTS/Downloads/DEPI/Depi_Amit_BNS3_AIS4_S1/python_basics/session 3/test os"
createfolders(path)
deletehalf(path)