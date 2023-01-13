# Gets data from file or url

import os
import datetime
from dateutil.relativedelta import relativedelta
import requests
import pandas as pd
import json
import numpy as np
import dateutil.parser
from dotenv import load_dotenv

load_dotenv()
local_file_dir = os.getenv('local_file_dir')

# ID, Value, Variable, Units, Suspect Reading, Timestamp, Datetime, Latitude, Longitude

def getUOFile(variable):
    print('fetching UO data from local file...', variable, datetime.datetime.now())
    json_data = json.load(open(local_file_dir+variable+'.json'))
    df = pd.json_normalize(json_data, record_path=['sensors'])
    return df[df['data.'+variable].notna()]

def getUO(variable, start, end):
    #TODO: Put this in same format as others
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

def getUDX(location, variable, start, end):
    print('fetching UDX data...', location, variable, datetime.datetime.now())
    multiple_requests = False

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

            start = f"{start.strftime('%Y-%m-%d')}T{start.strftime('%H')}%3A{start.strftime('%M')}%3A{start.strftime('%S')}.000Z"
            end = f"{end.strftime('%Y-%m-%d')}T{end.strftime('%H')}%3A{end.strftime('%M')}%3A{end.strftime('%S')}.000Z"

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
        print('fetching UDX data...', location, variable, datetime.datetime.now())
        if location == 'Birmingham':
            response_API = requests.get(os.getenv(f'{location}_url'), 
            headers={"Content-Type":os.getenv('cont'), "Authorization":os.getenv(f'{location}_auth')+' '+os.getenv(f'{location}_key')})
        else:
            response_API = requests.get(os.getenv(f'{location}_{variable}_url'), 
            headers={"Content-Type":os.getenv('cont'), "Authorization":os.getenv(f'{location}_auth')+' '+os.getenv(f'{location}_{variable}_key')})
        print(variable, 'status code: ', response_API.status_code)
        json_data = json.loads(response_API.text)
        return pd.json_normalize(json_data)

def getSUF(location, variable, units, start, end):
    start = start.strftime("%Y-%m-%dT%H:%M:%S")
    end   = end.strftime("%Y-%m-%dT%H:%M:%S")
    print('fetching SUF data...', variable, datetime.datetime.now())
    url = (
        f"{os.getenv('SUF_base_url')}"
        f"?Tfrom={start}"
        f"&Tto={end}"
        f"&bySelect={os.getenv('bySelect_'+variable)}"
        f"&freqInMin={os.getenv('freqInMin')}"
        f"&udfnoval={os.getenv('udfnoval')}"
        f"&udfbelow={os.getenv('udfbelow')}"
        f"&udfabove={os.getenv('udfabove')}"
        f"&hrtFormat={os.getenv('hrtFormat')}"
        f"&tabCont={os.getenv('tabCont')}"
        f"&gdata={os.getenv('gdata')}"
        f"&src={os.getenv('src')}"
        f"&op={os.getenv('op')}"
        f"&fmt={os.getenv('fmt')}"
        f"&output={os.getenv('output')}"
        f"&tok={os.getenv('tok')}"
        f"&spatial={os.getenv('spatial')}"
        f"&addTimeInMs={os.getenv('addTimeInMs')}"
        f"&addGeoloc={os.getenv('addGeoloc')}"
    )
    response_API = requests.get(url)
    print(variable, 'status code: ', response_API.status_code, url)
    json_data = json.loads(response_API.text)

    dfs = []
    for n in range(0,len(json_data['bundles'])):
        source = json_data['bundles'][n]['source'].split("-")[1]
        rows = json_data['bundles'][n]['dataByRow']
        df = pd.DataFrame(rows)

        df.rename({
            'Time_ms': 'Timestamp', 
            source+'.sensor': 'ID',
            source+'.'+variable: 'Value',
            'longitude': 'Longitude',
            'latitude': 'Latitude'
        }, axis='columns', inplace=True)

        df = df.drop([source+'.time', 'altitude'], axis='columns')
        df['Variable'] = variable
        df['Units'] = units
        df['Suspect Reading'] = False
        df['Datetime'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df['ID'] = df['ID'].astype(str)
        dfs.append(df)

    return pd.concat(dfs)


def fetch(src, location, variable, start, end):

    if src == 'UO':

        if variable == 'PM2.5':
            units = 'μgm⁻³'
            df = getUO(variable, start, end)
            if df.empty:
                return df

        elif variable == 'Temperature':
            units = '°C'
            df = getUO(variable, start, end)
            if df.empty:
                return df

        elif variable == 'Traffic Flow':
            variable = 'Plates Matching'
            units = 'Vehicles'
            df = getUO(variable, start, end)
            if df.empty:
                return df

        df = df[[
            'data.'+variable,
            'Sensor Centroid Latitude.0',
            'Sensor Centroid Longitude.0'
            ]]

        dfs=[]
        for i, l in enumerate(df['data.'+variable]):
            ds = pd.DataFrame(l)
            ds['Latitude'] = df['Sensor Centroid Latitude.0']
            ds['Longitude'] = df['Sensor Centroid Longitude.0']
            dfs.append(ds)
        df = pd.concat(dfs)

        df.rename({
            'Sensor Name': 'ID',
            'Flagged as Suspect Reading': 'Suspect Reading'
        }, axis='columns', inplace=True)

        df['Datetime'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df = df.iloc[::int(os.getenv('thin_data_by_factor_of')), :]


    elif src == 'UDX':

        if location == 'Newcastle':

            if variable == 'PM2.5':

                variable = 'pm25'
                units = 'μgm⁻³'
                df = getUDX(location, variable, start, end)

                if df.empty:
                    return df
                
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

            elif variable == 'Temperature':

                variable = 'temperature'
                units = '°C'
                df = getUDX(location, variable, start, end)

                if df.empty:
                    return df
                
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

            elif variable == 'Traffic Flow':

                variable = 'intensity'
                units = 'Vehicles'
                df = getUDX(location, variable, start, end)

                if df.empty:
                    return df
                
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

            df['ID'] = df['ID'].str.split(":").str[3]
            df['Variable'] = variable
            df['Units'] = units
            df['Datetime'] = pd.to_datetime(df['dateObserved.value'].str.replace('.000','', regex=True), format='%Y-%m-%dT%H:%M:%SZ')
            df['Timestamp'] = pd.to_datetime(df['Datetime']).astype(int) / 10**6
            df['Longitude'] = df['location.value.coordinates'].str[0]
            df['Latitude'] = df['location.value.coordinates'].str[1]
            df['Location'] = 'NewcastleUO'
            df = df.drop(['location.value.coordinates', 'dateObserved.value'], axis='columns')

        elif location == 'Manchester':

            if variable == 'PM2.5':

                variable = 'pm25'
                units = 'μgm⁻³'
                df = getUDX(location, variable, start, end)

                if df.empty:
                    return df

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

            elif variable == 'Traffic Flow':

                variable = 'intensity'
                units = 'Vehicles'
                df = getUDX(location, variable, start, end)

                if df.empty:
                    return df

                print(df)

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

            elif variable == 'Black Carbon':

                variable = 'bc'
                units = 'ngm⁻³'
                df = getUDX(location, variable, start, end)

                if df.empty:
                    return df

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

            df['ID'] = df['ID'].str.split(":").str[3]
            df['Variable'] = variable
            df['Units'] = units
            df['Datetime'] = pd.to_datetime(df['dateObserved.value'].str.replace('.000','', regex=True), format='%Y-%m-%dT%H:%M:%SZ')
            df['Timestamp'] = pd.to_datetime(df['Datetime']).astype(int) / 10**6
            df['Longitude'] = df['location.value.coordinates'].str[0]
            df['Latitude'] = df['location.value.coordinates'].str[1]
            df['Location'] = 'ManchesterUO'
            df = df.drop(['location.value.coordinates', 'dateObserved.value'], axis='columns')
            
        elif location == 'Birmingham':

            if variable == 'PM2.5':
                variable = 'pm25'
                units = 'μgm⁻³'

            elif variable == 'Nitric Oxide':
                variable = 'no'
                units = 'μgm⁻³'

            elif variable == 'Ozone':
                variable = 'o3'
                units = 'μgm⁻³'

            elif variable == 'Nitrogen Dioxide':
                variable = 'no2'
                units = 'μgm⁻³'

            elif variable == 'PM1':
                variable = 'pm1'
                units = 'μgm⁻³'

            elif variable == 'PM10':
                variable = 'pm10'
                units = 'μgm⁻³'

            elif variable == 'Humidity':
                variable = 'humidity'
                units = '%'

            elif variable == 'Pressure':
                variable = 'pressure'
                units = 'Pa'

            elif variable == 'Temperature':
                variable = 'temperature'
                units = '°C'

            df = getUDX(location, variable, start, end)

            if df.empty:
                return df

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
                'timestamp.value': 'Timestamp',
            }, axis='columns', inplace=True)

            df['ID'] = df['ID'].str.split(":").str[5]
            df['Variable'] = variable
            df['Units'] = units
            df['Datetime'] = pd.to_datetime(df['dateObserved.value'].str.replace('.000','', regex=True), format='%Y-%m-%dT%H:%M:%SZ')
            df['Timestamp'] = pd.to_datetime(df['Datetime']).astype(int) / 10**6
            df['Longitude'] = df['location.value.coordinates'].str[0]
            df['Latitude'] = df['location.value.coordinates'].str[1]
            df['Location'] = 'BirminghamUO'
            df = df.drop(['location.value.coordinates', 'dateObserved.value'], axis='columns')


    elif src == 'SUF': # Sheffield Urban Flows

        if variable == 'PM2.5':
            variable = 'PM25'
            units = 'μgm⁻³'

            df = getSUF(location, variable, units, start, end)

            if df.empty:
                    return df

    
    df = df[df['Value'].notna()]
    df.sort_values(by='Datetime', inplace = True)
    
    return df