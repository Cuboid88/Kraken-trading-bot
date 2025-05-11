import requests
from datetime import datetime
# Endpoint for Fear and Greed Index
FNG_URL = "https://api.alternative.me/fng/?limit=1"

def fetch_fng_data():
    """
    Fetches Fear and Greed Index data from the Alternative.me API.
    Returns a sorted list of FNG data points with timestamps.
    """
    response = requests.get(FNG_URL)
    if response.status_code != 200:
        raise Exception(f"Error fetching FNG data: {response.status_code}")
    
    data = response.json()
    fng_data = data.get("data", [])
    for point in fng_data:
        point["timestamp"] = int(point["timestamp"])
    fng_data.sort(key=lambda x: x["timestamp"])
    return fng_data

if __name__ == "__main__":
    fng_data = fetch_fng_data()
    print()
    for point in fng_data:
        print(f"Date: {datetime.fromtimestamp(point['timestamp']).strftime('%d-%m-%Y %H:%M:%S')} | FNG: {point['value']}, Classification: {point['value_classification']}")