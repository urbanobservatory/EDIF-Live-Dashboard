# Returns custom graph info based on variable

import os
from dotenv import load_dotenv

load_dotenv()
pm25_display_limit = int(os.getenv('pm25_display_limit'))
temperature_display_limit = int(os.getenv('temperature_display_limit'))

def customise(df, variable, location):
    if variable == 'PM2.5':
        df = df[df['Value'] <= pm25_display_limit]
    elif variable == "Temperature":
        df = df[df['Value'] <= temperature_display_limit]
    elif variable == 'Traffic Flow':
        df = df[df['Value'] != 0]

    if location == 'Newcastle':
        color = '#f44242'
    elif location == "Manchester":
        color = '#4254f5'
    elif location == 'Birmingham':
        color = '#47d65f'
    else:
        color = '#8a8888'

    return df, color