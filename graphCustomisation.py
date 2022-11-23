# Returns custom graph info based on variable

import os
from dotenv import load_dotenv

load_dotenv()
pm25_display_limit = int(os.getenv('pm25_display_limit'))
temperature_display_limit = int(os.getenv('temperature_display_limit'))

def uo(df, variable): #TODO: Define colours in parameters/dotenv file
    if variable == "PM2.5":
        df = df[df['Value'] <= pm25_display_limit]
        color = '#f44242'
    elif variable == "Temperature":
        df = df[df['Value'] <= temperature_display_limit]
        color = '#4254f5'
    elif variable == 'Plates Matching':
        df = df[df['Value'] != 0]
        color = '#47d65f'
    else:
        color = '#8a8888'
    return df, color

def udx(df, variable):
    #TODO: This
    pass