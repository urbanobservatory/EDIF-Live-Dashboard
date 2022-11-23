# Gets data from file or url

import os
import datetime
import requests
import pandas as pd
import json
from dotenv import load_dotenv

load_dotenv()
local_file_dir = os.getenv('local_file_dir')
udx_cont       = os.getenv('udx_cont')
udx_auth       = os.getenv('udx_auth')
udx_PM25_url   = os.getenv('udx_PM25_url')
udx_PM25_key   = os.getenv('udx_PM25_key')

def fromUOFile(variable):
    print('fetching UO data from local file...', variable, datetime.datetime.now())
    json_data = json.load(open(local_file_dir+variable+'.json'))
    df = pd.json_normalize(json_data, record_path=['sensors'])
    df = df[df['data.'+variable].notna()]
    return df

def fromUDXFile(variable):
    #TODO: This
    pass

def uo(variable, start, end):
    start = start.strftime("%Y%m%d%H%M%S")
    end   = end.strftime("%Y%m%d%H%M%S")
    print('fetching UO data...', variable, datetime.datetime.now())
    url = f"http://uoweb3.ncl.ac.uk/api/v1.1/sensors/data/json/?starttime={start}&endtime={end}&data_variable={variable}"
    response_API = requests.get(url)
    print(variable, 'status code: ', response_API.status_code, url)
    json_data = json.loads(response_API.text)
    df = pd.json_normalize(json_data, record_path=['sensors'])
    df = df[df['data.'+variable].notna()]
    return df

def udx(variable):
    #TODO: Remove hard coded variables
    print('fetching UDX data...', variable, datetime.datetime.now())
    response_API = requests.get(udx_PM25_url, headers={
        "Content-Type":udx_cont, "Authorization":udx_auth+' '+udx_PM25_key})
    print(variable, 'status code: ', response_API.status_code)
    json_data = json.loads(response_API.text)
    df = pd.json_normalize(json_data)
    df = df.drop(['type','@context','pm25.type','height.type','altitude.type',
                  'location.type','timestamp.type','aggregation.type',
                  'dateObserved.type','suspectReading.type','location.value.type'], axis=1)
    df = df[df['pm25.value'].notna()]
    return df
