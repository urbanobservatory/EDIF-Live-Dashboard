# Gets data from file or url

import os
import datetime
import requests
import pandas as pd
import json
import dateutil.parser
from dotenv import load_dotenv

load_dotenv()
local_file_dir = os.getenv('local_file_dir')

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

def udx(location, variable):
    print('fetching UDX data...', location, variable, datetime.datetime.now())
    response_API = requests.get(os.getenv(f'{location}_{variable}_url'), 
        headers={"Content-Type":os.getenv('cont'), "Authorization":os.getenv(f'{location}_auth')+' '+os.getenv(f'{location}_{variable}_key')})
    print(variable, 'status code: ', response_API.status_code)
    json_data = json.loads(response_API.text)
    df = pd.json_normalize(json_data)

    #TODO: Drop relevant columns for each variable to save on memory
    # df = df.drop(['type','@context',variable+'.type','height.type','altitude.type',
    #               'location.type','timestamp.type','aggregation.type',
    #               'dateObserved.type','suspectReading.type','location.value.type'], axis=1)

    df = df.rename(columns={variable+'.value': 'Value'})
    df = df.rename(columns={variable+'.unit': 'Units'})

    df['id'] = df['id'].str.split(":").str[3]
    df = df[df['Value'].notna()]
    df['Datetime'] = pd.to_datetime(df['dateObserved.value'].str.replace('.000','', regex=True), format='%Y-%m-%dT%H:%M:%SZ')
    df['Timestamp'] = pd.to_datetime(df['Datetime']).astype(int) / 10**6
    df['Variable'] = variable

    return df
