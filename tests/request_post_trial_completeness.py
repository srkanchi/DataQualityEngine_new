
# importing the requests library 
import requests 
import json

  
# defining the api-endpoint  
API_ENDPOINT = "http://127.0.0.1:8005/run"
  
with open('/home/ubuntu/DataQualityEngine/tests/input_example_trial_completeness.json') as json_file:
    data = json.load(json_file)

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
# sending post request and saving response as response object 
r = requests.post(url = API_ENDPOINT, data=json.dumps(data), headers=headers) 
  
# extracting response text  
pastebin_url = r.text 
print("The pastebin URL is:%s"%pastebin_url) 

