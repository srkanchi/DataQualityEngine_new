# importing the requests library 
import requests 
import json
  
# defining the api-endpoint  
API_ENDPOINT = "http://localhost:8005/runTests"
  
with open('./input_example.json') as json_file:
    data = json.load(json_file)
  
# sending post request and saving response as response object 
r = requests.post(url = API_ENDPOINT, data=data) 
  
# extracting response text  
pastebin_url = r.text 
print("The pastebin URL is:%s"%pastebin_url) 