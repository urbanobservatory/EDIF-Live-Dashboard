import os
import datetime
from dateutil.relativedelta import relativedelta
import requests
import pandas as pd
import json

import mapping

def run(location, variable, start, end):
    variable_map = mapping.variables()

    requestVariable = variable_map[variable]['request-variable']
    units = variable_map[variable]['units']

    df = request(location, requestVariable, start, end)
    if df.empty:
        return df

    if location == 'Newcastle':
        df = selectNewcastle(requestVariable, df)
    else:
        df = select(requestVariable, df)

    df = format(location, variable, units, df)

    return df


def request(location, variable, start, end):
    print('fetching UDX data...', location, variable, datetime.datetime.now())
    multiple_requests = False

    start = f"{start.strftime('%Y-%m-%d')}T{start.strftime('%H')}%3A{start.strftime('%M')}%3A{start.strftime('%S')}.000Z"
    end = f"{end.strftime('%Y-%m-%d')}T{end.strftime('%H')}%3A{end.strftime('%M')}%3A{end.strftime('%S')}.000Z"

    print('fetching UDX data...', location, variable, start, end)

    if multiple_requests == True:
        # Time format: '2023-01-09T06%3A00%3A00.000Z'
        # Accumulate half-hours as UDX has a pagination limit of 1000
        time = start
        times = [start]
        # 48 - the number of half-hours in one day
        for i in range(0, 23):
            time = times[-1]+relativedelta(minutes=60)
            times.append(time)

        dfs = []
        for time in range(0, len(times)):
            if time == len(times)-1:
                break
            start = times[time]
            end = times[time+1]

            if location == 'Birmingham':
                response_API = requests.get(
                    url=f"{os.getenv(f'{location}_url')}?start={start}&end={end}", 
                    headers={
                        "Content-Type":os.getenv('cont'), 
                        "Authorization":os.getenv(f'{location}_auth')+' '+os.getenv(f'{location}_key')
                    }
                )
            else:
                response_API = requests.get(
                    url=f"{os.getenv(f'{location}_{variable}_url')}?start={start}&end={end}",
                    headers={
                        "Content-Type":os.getenv('cont'), 
                        "Authorization":os.getenv(f'{location}_auth')+' '+os.getenv(f'{location}_{variable}_key')
                    }
                )

            print(variable, 'status code: ', response_API.status_code)

            try:
                json_data = json.loads(response_API.text)
                dfs.append(pd.json_normalize(json_data))
            except:
                continue

        df = pd.concat(dfs, ignore_index=True)
        # df.drop_duplicates - can't when lists are included
        return df

    else:
        
        # if location == 'Birmingham':
        #     response_API = requests.get(os.getenv(f'{location}_url'), 
        #     headers={"Content-Type":os.getenv('cont'), "Authorization":os.getenv(f'{location}_auth')+' '+os.getenv(f'{location}_key')})
        # else:
        #     response_API = requests.get(os.getenv(f'{location}_{variable}_url'), 
        #     headers={"Content-Type":os.getenv('cont'), "Authorization":os.getenv(f'{location}_auth')+' '+os.getenv(f'{location}_{variable}_key')})

        if location == 'Birmingham':
                response_API = requests.get(
                    url=f"{os.getenv(f'{location}_url')}?start={start}&end={end}", 
                    headers={
                        "Content-Type":os.getenv('cont'), 
                        "Authorization":os.getenv(f'{location}_auth')+' '+os.getenv(f'{location}_key')
                    }
                )
        else:
            response_API = requests.get(
                url=f"{os.getenv(f'{location}_{variable}_url')}?start={start}&end={end}",
                headers={
                    "Content-Type":os.getenv('cont'), 
                    "Authorization":os.getenv(f'{location}_auth')+' '+os.getenv(f'{location}_{variable}_key')
                }
            )
                
        print(variable, 'status code: ', response_API.status_code)
        json_data = json.loads(response_API.text)
        return pd.json_normalize(json_data)


def selectNewcastle(variable, df):
            
    if variable == 'Temperature':
        df = df[[
            'id', 
            variable+'.unit', 
            variable+'.value', 
            variable+'.suspectReading',
            'dateObserved.value',
            'location.value.coordinates'
            ]]
        df.rename({
            'id': 'ID',
            variable+'.unit': 'Units',
            variable+'.value': 'Value',
            'timestamp.value': 'Timestamp',
            variable+'.suspectReading': 'Suspect Reading'
        }, axis='columns', inplace=True)

    else:
        df = df[[
            'id', 
            variable+'.unit', 
            variable+'.value', 
            'suspectReading.value',
            'dateObserved.value',
            'location.value.coordinates'
            ]]
        df.rename({
            'id': 'ID',
            variable+'.unit': 'Units',
            variable+'.value': 'Value',
            'timestamp.value': 'Timestamp',
            'suspectReading.value': 'Suspect Reading'
        }, axis='columns', inplace=True)

    return df


def select(variable, df):

    df = df[[
        'id', 
        variable+'.unit', 
        variable+'.value', 
        'dateObserved.value',
        'location.value.coordinates'
        ]]

    df.rename({
        'id': 'ID',
        variable+'.unit': 'Units',
        variable+'.value': 'Value',
        'timestamp.value': 'Timestamp'
    }, axis='columns', inplace=True)

    return df


def format(location, variable, units, df):

    if location == 'Birmingham':
        df['ID'] = df['ID'].str.split(":").str[5]
    else:
        df['ID'] = df['ID'].str.split(":").str[3]

    df['Variable'] = variable
    df['Units'] = df['Units'] = units
    df['Datetime'] = pd.to_datetime(df['dateObserved.value'].str.replace('.000','', regex=True), format='%Y-%m-%dT%H:%M:%SZ')
    df['Timestamp'] = pd.to_datetime(df['Datetime']).astype(int) / 10**6
    df['Longitude'] = df['location.value.coordinates'].str[0]
    df['Latitude'] = df['location.value.coordinates'].str[1]
    df['Location'] = location+'UO'

    df = df.drop(['location.value.coordinates', 'dateObserved.value'], axis='columns')
    df = df[df['Value'].notna()]
    df.sort_values(by='Datetime', inplace = True)

    return df