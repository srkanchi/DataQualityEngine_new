
# importing the requests library 
import requests 
import json
import glob
import os
  
# defining the api-endpoint  
API_ENDPOINT = "http://127.0.0.1:8005/run"

test2 = os.getcwd()
test1 = glob.glob('./')
print('*** test 1 ***')
print(test1)
print('*** test 2 ***')
print(test2)

with open(test2 + '/input_example_TD_completeness_0.json') as json_file:
    data = json.load(json_file)


headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
# sending post request and saving response as response object 
r = requests.post(url = API_ENDPOINT, data=json.dumps(data), headers=headers) 
  
# extracting response text  
pastebin_url = r.text 
print("The pastebin URL is:%s"%pastebin_url) 

