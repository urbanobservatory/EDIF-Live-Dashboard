import os
import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

import getData
import allValues
import latestValues
import suspectReadings
import indicators

load_dotenv()
day_period = float(os.getenv('day_period'))

def times(day_period):
    start = datetime.datetime.now()-relativedelta(days=day_period)
    end   = datetime.datetime.now()
    return start, end


def run(src, location, variable, df):
    start, end = times(day_period)
    data = {'start': start, 'end': end}

    if df.empty:
        data.update({'status': 'Offline'})
        return data

    if location == 'Newcastle':
        df, sus_df = suspectReadings.run(variable, df)
        data.update({'suspect_dataframe': sus_df})

    sensor_dfs = allValues.run(df)
    sensors, records = indicators.run(df)
    latest_readings_df = latestValues.run(variable, df, sensor_dfs, src)
    
    display_graphs = displayGraphs.run(location, variable, sensor_dfs)

    data.update({
        'dataframe': df, 
        'display_graphs': display_graphs,
        'latest_readings': latest_readings_df,
        'status': 'Online',
        'sensors': sensors,
        'records': records
    })

    return data