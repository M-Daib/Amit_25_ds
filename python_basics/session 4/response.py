import random
import json

with open("C:/Users/COMPUMARTS/Downloads/DEPI/Depi_Amit_BNS3_AIS4_S1/python_basics/session 4/CB responses.json",'r') as file:
    responses = json.load(file)
def get_response(user_input):
  for key in responses:
    if key in user_input:
      return random.choice(responses[key])
  return random.choice(responses["default"])