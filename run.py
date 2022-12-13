import os
import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

import getData
import allValues
import latestValues
import displayGraphs
import displayMaps
import suspectReadings
import displayGauge

load_dotenv()
day_period = float(os.getenv('day_period'))

def times(day_period):
    start = datetime.datetime.now()-relativedelta(days=day_period)
    end   = datetime.datetime.now()
    return start, end


def run(src, location, variable, units='None'):
    start, end = times(day_period)
    data = {'start': start, 'end': end}

    df = getData.fetch(src, location, variable, units, start, end)
    if df.empty:
        data.update({'status': 'Offline'})
        return data

    if location == 'Newcastle':
        df, sus_df = suspectReadings.run(variable, df)
        data.update({'suspect_dataframe': sus_df})

    sensor_dfs = allValues.run(df)
    latest_readings_df = latestValues.run(variable, df, sensor_dfs, src)
    
    display_graphs = displayGraphs.run(variable, sensor_dfs)
    display_maps   = displayMaps.run(variable, latest_readings_df, units)
    display_gauge  = displayGauge.display(latest_readings_df)

    data.update({
        'dataframe': df, 
        'display_graphs': display_graphs,
        'latest_readings': latest_readings_df,
        'map_display': display_maps,
        'display_gauge': display_gauge,
        'status': 'Online'
    })

    return data