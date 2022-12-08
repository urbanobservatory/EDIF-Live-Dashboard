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

def uo(variable, dict_all, src):
    start, end         = times(day_period)
    df = getData.fromUOFile(variable) if src=='UOFile' else getData.uo(variable,start,end)
    sensor_dfs         = allValues.uo(variable, df)
    latest_readings_df = latestValues.uo(df, sensor_dfs, src)
    suspect_df         = suspectReadings.uo(variable, df, dict_all)
    display_graphs     = displayGraphs.uo(variable, sensor_dfs)
    display_maps       = displayMaps.uo(variable, latest_readings_df)
    display_gauge      = displayGauge.uo(latest_readings_df)
    dict_all[variable] = {'start': start, 
                          'end': end,
                          'dataframe': df, 
                          'display_graphs': display_graphs, 
                          'suspect_dataframe': suspect_df,
                          'latest_readings': latest_readings_df,
                          'map_display': display_maps,
                          'display_gauge': display_gauge
                          }
    return dict_all

def udx(src, location, variable, units=None):
    start, end = times(day_period)
    data = {'start': start, 'end': end}

    df = getData.fetch(src, location, variable, units, start, end)
    if df.empty:
        data.update({'status': 'Offline'})

    else:
        if location == 'Newcastle':
            df, sus_df = suspectReadings.udx(variable, df)
            data.update({'suspect_dataframe': sus_df})

        sensor_dfs = allValues.udx(df)
        latest_readings_df = latestValues.udx(variable, df, sensor_dfs, src)
        
        display_graphs = displayGraphs.udx(variable, sensor_dfs)
        display_maps   = displayMaps.udx(variable, latest_readings_df)
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