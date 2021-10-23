
# importing the requests library 
import requests 
import json

  
# defining the api-endpoint  
API_ENDPOINT = "http://127.0.0.1:8005/run"

##<<<<<<< HEAD
##with open('C:/cls/codigo/qualityEngine/DataQualityEngine/tests/input_example_TD_Completeness_0.json') as json_file:
## =======
with open('./input_example_TD_completeness_0.json') as json_file:
##>>>>>>> a04b92aa36a56ddc75c408d9563f102907fe87f1
    data = json.load(json_file)


headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
# sending post request and saving response as response object 
r = requests.post(url = API_ENDPOINT, data=json.dumps(data), headers=headers) 
  
# extracting response text  
pastebin_url = r.text 
print("The pastebin URL is:%s"%pastebin_url) 

