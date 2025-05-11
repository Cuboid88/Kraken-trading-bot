import requests
import json
from datetime import datetime

url = "https://api.kraken.com/0/public/SystemStatus"


headers = {
  'Accept': 'application/json'
}

response = requests.request("GET", url, headers=headers)

print(response.text)

data = json.loads(response.text)



print(f"This is the date time: {data["result"]["timestamp"]}")