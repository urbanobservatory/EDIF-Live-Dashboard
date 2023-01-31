# Returns custom graph info based on variable

import json


env_vars = json.load(open('/code/env.json'))

pm25_display_limit = int(env_vars['pm25_display_limit'])
temperature_display_limit = int(env_vars['temperature_display_limit'])

def customise(df, variable):
    if variable == 'PM2.5':
        df = df[df['Value'] <= pm25_display_limit]
    elif variable == "Temperature":
        df = df[df['Value'] <= temperature_display_limit]
    elif variable == 'Traffic Flow':
        df = df[df['Value'] != 0]

    if variable != 'Temperature':
        df = df[df['Value'] >= 0]

    return df