import os
import datetime
from dateutil.relativedelta import relativedelta
import requests
import pandas as pd
import json

import mapping

def run(variable, start, end):

    variable_map = mapping.variables()
    requestVariable = variable_map[variable]['request-variable']
    units = variable_map[variable]['units']

    source_map = mapping.UDXsources()

    dfs = []
    for organisation in source_map:
        for source in source_map[organisation]:
            for stream in source_map[organisation][source]:
                if variable in source_map[organisation][source][stream]:
                    try:

                        df = request(organisation, source, stream, requestVariable, start, end)

                        if source == 'Newcastle-UO':
                            df = selectNewcastle(requestVariable, df)
                        else:
                            df = select(requestVariable, df)

                        df = format(organisation, source, stream, variable, units, df)

                        dfs.append(df)

                    except:
                        continue

    df = pd.concat(dfs)

    return df


def request(organisation, source, stream, variable, start, end):

    start = f"{start.strftime('%Y-%m-%d')}T{start.strftime('%H')}%3A{start.strftime('%M')}%3A{start.strftime('%S')}.000Z"
    end = f"{end.strftime('%Y-%m-%d')}T{end.strftime('%H')}%3A{end.strftime('%M')}%3A{end.strftime('%S')}.000Z"

    print('fetching UDX data...', organisation, source, stream, variable, start, end)

    if source == 'Zephyr' and stream == 'PM2.5':
        response_API = requests.get(
            url=f"{os.getenv(f'{source}_url')}?start={start}&end={end}", 
            headers={
                "Content-Type":os.getenv('cont'), 
                "Authorization":os.getenv(f'{source}_auth')+' '+os.getenv(f'{source}_key')
            }
        )
    elif source == 'Sheffield-UF' and variable != 'intensity':
        response_API = requests.get(
            url=f"{os.getenv(f'{source}_aq_url')}?start={start}&end={end}", 
            headers={
                "Content-Type":os.getenv('cont'), 
                "Authorization":os.getenv(f'{source}_auth')+' '+os.getenv(f'{source}_aq_key')
            }
        )
    else:
        response_API = requests.get(
            url=f"{os.getenv(f'{source}_{variable}_url')}?start={start}&end={end}",
            headers={
                "Content-Type":os.getenv('cont'), 
                "Authorization":os.getenv(f'{source}_auth')+' '+os.getenv(f'{source}_{variable}_key')
            }
        )
            
    print(variable, 'status code: ', response_API.status_code)
    json_data = json.loads(response_API.text)
    return pd.json_normalize(json_data)


def selectNewcastle(variable, df):
            
    if variable == 'Temperature':
        df = df[[
            'id', 
            # variable+'.unit', 
            variable+'.value', 
            variable+'.suspectReading',
            'dateObserved.value',
            'location.value.coordinates'
            ]]
        df.rename({
            'id': 'ID',
            # variable+'.unit': 'Units',
            variable+'.value': 'Value',
            'timestamp.value': 'Timestamp',
            variable+'.suspectReading': 'Suspect Reading'
        }, axis='columns', inplace=True)

    else:
        df = df[[
            'id', 
            # variable+'.unit', 
            variable+'.value', 
            'suspectReading.value',
            'dateObserved.value',
            'location.value.coordinates'
            ]]
        df.rename({
            'id': 'ID',
            # variable+'.unit': 'Units',
            variable+'.value': 'Value',
            'timestamp.value': 'Timestamp',
            'suspectReading.value': 'Suspect Reading'
        }, axis='columns', inplace=True)

    return df


def select(variable, df):

    df = df[[
        'id', 
        # variable+'.unit', 
        variable+'.value', 
        'dateObserved.value',
        'location.value.coordinates'
        ]]

    df.rename({
        'id': 'ID',
        # variable+'.unit': 'Units',
        variable+'.value': 'Value',
        'timestamp.value': 'Timestamp'
    }, axis='columns', inplace=True)

    return df


def format(organisation, source, stream, variable, units, df):

    if source == 'Zephyr':
        df['ID'] = df['ID'].str.split(":").str[5]
    elif source == 'Sheffield-UF':
        df['ID'] = df['ID'].str.split(":").str[4]
    else:
        df['ID'] = df['ID'].str.split(":").str[3]

    df['Datetime'] = pd.to_datetime(df['dateObserved.value'].str.replace('.000','', regex=True), format='%Y-%m-%dT%H:%M:%SZ')
    df['Timestamp'] = pd.to_datetime(df['Datetime']).astype(int) / 10**6
    df['Longitude'] = df['location.value.coordinates'].str[0]
    df['Latitude'] = df['location.value.coordinates'].str[1]

    df['Organisation'] = organisation
    df['Source'] = source
    df['Steam'] = stream
    df['Variable'] = variable
    df['Units'] = units

    df = df.drop(['location.value.coordinates', 'dateObserved.value'], axis='columns')
    df = df[df['Value'].notna()]
    df.sort_values(by='Datetime', inplace = True)

    return df