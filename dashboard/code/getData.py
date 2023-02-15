import requests
import pandas as pd
import json
import mapping

env_vars = json.load(open('/code/env.json'))

def run(variable, start, end):

    variable_map = mapping.variables()
    requestVariable = variable_map[variable]['request-variable']
    units = variable_map[variable]['units']

    source_map = mapping.UDXsources()

    dfs = []
    for organisation in source_map:
        print(organisation)
        for source in source_map[organisation]:
            for stream in source_map[organisation][source]:

                if variable in source_map[organisation][source][stream]:

                    try:
                        if organisation == 'Cranfield':

                            df = requestCranfield(organisation, source, stream, requestVariable, start, end,units)
                            print(df)
                            if len(df) > 0:
                                print('adding')
                                dfs.append(df)
                        else:
                            df = request(organisation, source, stream, requestVariable, start, end)
                            if source == 'Newcastle-UO':
                                df = selectNewcastle(requestVariable, df)
                            else:
                                df = select(requestVariable, df)

                            df = format(organisation, source, stream, variable, units, df)

                            dfs.append(df)
                    
                    except Exception as e:
                        print(f'getData Exception for organisation: {organisation}, source: {source}, stream: {stream}, variable: {variable}', flush=True)
                        print(e, flush=True)
                        continue

    if dfs:
        df = pd.concat(dfs)
    print(df)
    df.to_csv('/csvs/mega.csv')
    return df


def request(organisation, source, stream, variable, start, end):

    start = f"{start.strftime('%Y-%m-%d')}T{start.strftime('%H')}%3A{start.strftime('%M')}%3A{start.strftime('%S')}.000Z"
    end = f"{end.strftime('%Y-%m-%d')}T{end.strftime('%H')}%3A{end.strftime('%M')}%3A{end.strftime('%S')}.000Z"

    print('fetching UDX data...', organisation, source, stream, variable, start, end)

    response_API = requests.get(
        url=f"{env_vars[f'{source}_{stream}_url']}?start={start}&end={end}",
        headers={
            "Content-Type":env_vars['cont'],
            "Authorization":env_vars[f'{source}_auth']+' '+env_vars[f'{source}_{stream}_key']
        }
    )
            
    print(variable, 'status code: ', response_API.status_code)
    json_data = json.loads(response_API.text)
    return pd.json_normalize(json_data)


def requestCranfield(organisation, source, stream, variable, start, end,units):

    """
	ID	Value	Suspect Reading	Datetime	Timestamp	Longitude	Latitude	Organisation	Source	Stream	Variable	Units
789	PER_AIRMON_MESH1913150	22.99	False	2023-02-14 12:33:00	1676377980000	-1.704298	55.000748	Newcastle Urban Observatory	Newcastle-UO	PM2.5	PM2.5	μgm⁻³
 """
    import datetime

    var_lookup = {'pm25':'PM2.5','pm10':'PM10','co':'CO','no':'NO'}
    if variable not in var_lookup.keys():
        print(variable)
        return pd.DataFrame([])
    url = "https://api.airmonitors.net/3.5/GET/4ed8059b-C/8cac-fef6-jRSq-AS04-N8u7-6R8y-539d-b388/stations"
    r = requests.get(url)
    print(start,end)
    station_json = r.json()
    for stat in station_json:
        url = "https://api.airmonitors.net/3.5/GET/4ed8059b-C/8cac-fef6-jRSq-AS04-N8u7-6R8y-539d-b388/stationdata/{StartTimestamp}/{EndTimestamp}/{UniqueId}"
        data_url = url.format(
            StartTimestamp=start.strftime('%Y%m%dT%H%M%S'),
            EndTimestamp=end.strftime('%Y%m%dT%H%M%S'),
            UniqueId=stat["UniqueId"]
        )

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
        headers = "ID,Value,Suspect Reading,Datetime,Timestamp,Longitude,Latitude,Organisation,Source,Stream,Variable,Units".split(
            ",")


        frame = pd.DataFrame(pandas_row,columns=headers)
        frame['Value'] = pd.to_numeric(frame['Value'])
        frame['Timestamp'] = pd.to_numeric(frame['Value'])
        frame['Datetime'] = pd.to_datetime(frame['Datetime'])
        frame.to_csv('/csvs/cran.csv')
        return frame

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
    df['Stream'] = stream
    df['Variable'] = variable
    df['Units'] = units

    df = df.drop(['location.value.coordinates', 'dateObserved.value'], axis='columns')
    df = df[df['Value'].notna()]
    df.sort_values(by='Datetime', inplace = True)

    return df