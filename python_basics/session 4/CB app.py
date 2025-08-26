import random
import json
import os
from response import get_response
def clearscreen():
    os.system("cls")
with open("C:/Users/COMPUMARTS/Downloads/DEPI/Depi_Amit_BNS3_AIS4_S1/python_basics/session 4/CB responses.json",'r') as file:
    responses = json.load(file)
 
def chatbot():
    clearscreen()
    print("Chatbot: Hi How can i assist you today?")
    while True:
        user_input = input("User:  ").lower()
        theresponse = get_response(user_input)
        print("Chatbot: ", theresponse)
        if user_input == "goodbye":
            break
chatbot()
