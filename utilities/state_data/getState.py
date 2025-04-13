import requests
import os
from dotenv import load_dotenv

load_dotenv()

def getState():
    url = "https://api.countrystatecity.in/v1/countries/MY/states"

    headers = {
        'X-CSCAPI-KEY': os.getenv('GET_STATE_AREA_API')
    }

    response = requests.request("GET", url, headers=headers).json()

    states = {}

    for state in response:
        states[state.get('name')] = state.get('iso2')

    return states