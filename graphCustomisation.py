# Returns custom graph info based on variable

import os
from dotenv import load_dotenv

load_dotenv()
pm25_display_limit = int(os.getenv('pm25_display_limit'))
temperature_display_limit = int(os.getenv('temperature_display_limit'))

def customise(df, variable):
    if variable == 'PM2.5':
        df = df[df['Value'] <= pm25_display_limit]
    elif variable == "Temperature":
        df = df[df['Value'] <= temperature_display_limit]
    elif variable == 'Traffic Flow':
        df = df[df['Value'] != 0]

    #Blackbody,Bluered,Blues,Cividis,Earth,Electric,Greens,Greys,Hot,Jet,Picnic,Portland,Rainbow,RdBu,Reds,Viridis,YlGnBu,YlOrRd
    colorscales = {
        'PM2.5': 'reds',
        'Traffic Flow': 'bluered',
        'Black Carbon': 'Blackbody',
        'Nitric Oxide': 'Viridis',
        'Ozone': 'Blues',
        'Nitrogen Dioxide': 'RdBu',
        'PM1': 'reds',
        'PM10': 'reds',
        'Temperature': 'YlOrRd',
        'Humidity': 'Jet',
        'Pressure': 'YlGnBu'
    }

    return df, colorscales