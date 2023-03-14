import os
import requests
import pandas as pd
import json
import datetime
import traceback
from .mapping import UDXsources, variables, unit_lookup
env_vars = json.load(open('/code/env.json'))

def pull_data(variable, start, end):
    source_map = UDXsources()
    dfs = []
    variable_map = variables()

    requestVariable = variable_map[variable]['request-variable']
    units = variable_map[variable]['units']

    for organisation in source_map:
        for source in source_map[organisation]:
            for stream in source_map[organisation][source]:

                if variable in source_map[organisation][source][stream]:
                    try:

                        print(f'{organisation}, {source}, {stream}, {variable}, {start}, {end}')

                        if organisation == 'Cranfield':
                            df = requestCranfield(organisation, source, stream, requestVariable, start, end, units)
                            if len(df) > 0:
                                dfs.append(df)

                        elif source == 'Newcastle-UO':
                            df = get_uo_data(organisation, source, stream, requestVariable, start, end, units)
                            try:
                                df = df.drop('Unnamed: 0', axis=1)
                            except:
                                pass
                            try:
                                df = df.drop('index', axis=1)
                            except:
                                pass
                            try:
                                df = df.reset_index(drop=True)
                            except:
                                pass
                            if len(df) > 0:
                                dfs.append(df)

                        else:
                            df = request(organisation, source, stream, requestVariable, start, end)
                            if source == 'Newcastle-UO':
                                df = selectNewcastle(requestVariable, df)
                            else:
                                df = select(requestVariable, df)
                            print('...select success', flush=True)
                            df = format(organisation, source, stream, variable, units, df)
                            print('...format success', flush=True)
                            dfs.append(df)

                    except Exception:
                        print('...getData Exception:', flush=True)
                        # print('......', e, flush=True)
                        print(traceback.format_exc(), flush=True)
                        # print('......', df.info(), flush=True)
                        continue

    if dfs:
        df = pd.concat(dfs)
        return df


def request(organisation, source, stream, variable, start, end):
    start = f"{start.strftime('%Y-%m-%d')}T{start.strftime('%H')}%3A{start.strftime('%M')}%3A{start.strftime('%S')}.000Z"
    end = f"{end.strftime('%Y-%m-%d')}T{end.strftime('%H')}%3A{end.strftime('%M')}%3A{end.strftime('%S')}.000Z"

    print('...fetching UDX data')

    response_API = requests.get(
        url=f"{env_vars[f'{source}_{stream}_url']}?start={start}&end={end}",
        headers={
            "Content-Type":env_vars['cont'],
            "Authorization":env_vars[f'{organisation}_auth']+' '+env_vars[f'{source}_{stream}_key']
        }
    )
            
    print('...^', response_API.status_code)
    json_data = json.loads(response_API.text)
    df = pd.json_normalize(json_data)

    return df


def get_uo_data(organisation, source, stream, variable, start, end,units):
    uo_var_lookup = {'pm25':'PM2.5','pm10':'PM10','intensity':'Plates%20In','temperature':'Temperature',}

    headers = "ID,Value,Suspect Reading,Datetime,Timestamp,Longitude,Latitude,Organisation,Source,Stream,Variable,Units".split(
        ",")
    url = f"http://uoweb3.ncl.ac.uk/api/v1.1/sensors/data/csv/?starttime={start.strftime('%Y%m%d%H%M%S')}&endtime={end.strftime('%Y%m%d%H%M%S')}&data_variable={uo_var_lookup[variable]}"

    df = pd.read_csv(url)
    df['ID'] = df['Sensor Name']
    df['Suspect Reading'] = df['Flagged as Suspect Reading']
    df['Datetime'] = df['Timestamp']
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df['Timestamp'] = df['Datetime'].astype(int) / 10 ** 6
    df['Longitude'] = df['Sensor Centroid Longitude']
    df['Latitude'] = df['Sensor Centroid Latitude']
    df['Organisation'] = organisation
    df['Source'] = source
    df['Stream'] = stream
    df['Units'] = units
    df['Variable'] = unit_lookup()[variable]
    df = df[headers]
    df = df.sort_values(by=['Timestamp'])
    thinned_frames = []
    for sensor_name,frame in df.groupby('ID'):
        thinned_frames.append(frame.iloc[::50, :])
    if thinned_frames:
        df = pd.concat(thinned_frames)
        df = df.sort_values(by=['Timestamp'])
        # df = df.drop('index', axis=1)
        return df
    else:
        return pd.DataFrame([])


def requestCranfield(organisation, source, stream, variable, start, end, units):
    var_lookup = {'pm25':'PM2.5','pm10':'PM10','co':'CO','no':'NO'}

    if variable not in var_lookup.keys():
        print(variable)
        return pd.DataFrame([])

    url = "https://api.airmonitors.net/3.5/GET/4ed8059b-C/8cac-fef6-jRSq-AS04-N8u7-6R8y-539d-b388/stations"
    r = requests.get(url)
    print(start,end)
    station_json = r.json()

    pandas_row = []
    for stat in station_json:
        url = "https://api.airmonitors.net/3.5/GET/4ed8059b-C/8cac-fef6-jRSq-AS04-N8u7-6R8y-539d-b388/stationdata/{StartTimestamp}/{EndTimestamp}/{UniqueId}"
        data_url = url.format(
            StartTimestamp=start.strftime('%Y%m%dT%H%M%S'),
            EndTimestamp=end.strftime('%Y%m%dT%H%M%S'),
            UniqueId=stat["UniqueId"]
        )
        print(data_url)

        r = requests.get(data_url)

        try:
            data_json = r.json()
        except:
            continue

        pandas_row = []
        for row in data_json:
            dt = datetime.datetime.strptime(row['TETimestamp'].split('+')[0],'%Y-%m-%dT%H:%M:%S')

            for channel in row['Channels']:
                if channel['SensorLabel'] == var_lookup[variable]:
                    value = channel['Scaled']
                    row_str = f"""{stat["UniqueId"]},{value},False,{dt},{pd.to_datetime(dt).value / 10**6},{row['Longitude']},{row['Latitude']},{organisation},{source},{stream},{var_lookup[variable]},{units}''"""

                    pandas_row.append(row_str.split(','))

        print(data_url)

    if pandas_row:
        headers = "ID,Value,Suspect Reading,Datetime,Timestamp,Longitude,Latitude,Organisation,Source,Stream,Variable,Units".split(",")

        frame = pd.DataFrame(pandas_row,columns=headers)
        frame['Value'] = pd.to_numeric(frame['Value'])

        frame['Datetime'] = pd.to_datetime(frame['Datetime'])
        frame['Timestamp'] = frame['Datetime'].astype(int) / 10 ** 6

        return frame

    return pd.DataFrame([])


def selectNewcastle(variable, df):
            
    if variable == 'Temperature':
        df = df[[
            'id', 
            # variable+'.unit', 
            variable+'.value', 
            variable+'.suspectReading',
            'dateObserved.value',
            'timestamp.value',
            'location.value.coordinates'
            ]]
        df.rename({
            'id': 'ID',
            # variable+'.unit': 'Units',
            variable+'.value': 'Value',
            'timestamp.value': 'Received_Timestamp',
            variable+'.suspectReading': 'Suspect Reading'
        }, axis='columns', inplace=True)

    else:
        df = df[[
            'id', 
            # variable+'.unit', 
            variable+'.value', 
            'suspectReading.value',
            'dateObserved.value',
            'timestamp.value',
            'location.value.coordinates'
            ]]
        df.rename({
            'id': 'ID',
            # variable+'.unit': 'Units',
            variable+'.value': 'Value',
            'timestamp.value': 'Received_Timestamp',
            'suspectReading.value': 'Suspect Reading'
        }, axis='columns', inplace=True)

    return df


def select(variable, df):

    df = df[[
        'id', 
        # variable+'.unit', 
        variable+'.value', 
        'dateObserved.value',
        'timestamp.value',
        'location.value.coordinates'
        ]]

    df.rename({
        'id': 'ID',
        # variable+'.unit': 'Units',
        variable+'.value': 'Value',
        'timestamp.value': 'Received_Timestamp'
    }, axis='columns', inplace=True)

    return df


def format(organisation, source, stream, variable, units, df):

    if source == 'Zephyr':
        df['ID'] = df['ID'].str.split(":").str[5]
    elif source == 'Sheffield-UF':
        df['ID'] = df['ID'].str.split(":").str[4]
    elif source == 'TfWM' and stream == 'Traffic-Flow':
        df['ID'] = df['ID'].str.split(":").str[4]
    else:
        df['ID'] = df['ID'].str.split(":").str[3]

    df['Datetime'] = pd.to_datetime(
        df['dateObserved.value'], format='%Y-%m-%dT%H:%M:%S.%fZ')
    df['Timestamp'] = pd.to_datetime(df['Datetime']).astype(int) / 10**6

    if 'location.value.coordinates' in df.columns:
        df['Longitude'] = df['location.value.coordinates'].str[0]
        df['Latitude'] = df['location.value.coordinates'].str[1]
        df = df.drop(['location.value.coordinates'], axis='columns')

    df['Organisation'] = organisation
    df['Source'] = source
    df['Stream'] = stream
    df['Variable'] = variable
    df['Units'] = units

    df = df.drop(['dateObserved.value'], axis='columns')
    df = df[df['Value'].notna()]
    df.sort_values(by='Datetime', inplace = True)

    return df