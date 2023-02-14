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
                        if source == 'Cranfield':
                            continue
                            df = requestCranfield(organisation, source, stream, requestVariable, start, end)
                        else:
                            df = request(organisation, source, stream, requestVariable, start, end)
                        print(df)
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


def requestCranfield(organisation, source, stream, variable, start, end):
    print(organisation, source, stream, variable, start, end)

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