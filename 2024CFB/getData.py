#from requests_html import HTMLSession
import pandas as pd
import numpy as np
import requests
import json
from requests.structures import CaseInsensitiveDict
import warnings
warnings.simplefilter(action='ignore',category=FutureWarning)

def getData(source:str,params:dict,output='DataFrame'):
    '''Pull data from the CFB Data API'''
    
    warnings.simplefilter(action='ignore',category=FutureWarning)
    parameters = params
    url = "https://api.collegefootballdata.com/"+source+"?"
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["Authorization"] = "Bearer Sd1t1XM5n6z7inx0fvYlxLHQZ53clVzWz7aOcNfXGYzYtVgPWnFDOpY7KQbobYZK"
    #https://api.collegefootballdata.com/stats/game/advanced?year=2021&week=1&excludeGarbageTime=true
    resp = requests.get(url,params = parameters, headers=headers)
    if output == 'DataFrame':
        data = pd.DataFrame()
        #data = data.append(pd.json_normalize(json.loads(resp.text)))
        data = pd.concat([data,pd.json_normalize(json.loads(resp.text))])
    else: data = json.loads(resp.text)
    return data