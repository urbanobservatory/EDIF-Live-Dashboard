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

load_dotenv()
day_period = int(os.getenv('day_period'))

def times(day_period):
    start = datetime.datetime.now()-relativedelta(days=day_period)
    end   = datetime.datetime.now()
    return start, end

def uo(variable, dict_all, src):
    start, end         = times(day_period)
    df = getData.fromUOFile(variable) if src=='UOFile' else getData.uo(variable,start,end)
    sensor_dfs         = allValues.uo(variable, df)
    latest_readings_df = latestValues.uo(df, sensor_dfs, src)
    display_graphs     = displayGraphs.uo(variable, sensor_dfs)
    suspect_df         = suspectReadings.uo(variable, df)
    map_display        = displayMaps.uo(variable, latest_readings_df)
    dict_all[variable] = {'start': start, 
                          'end': end,
                          'dataframe': df, 
                          'display_graphs': display_graphs, 
                          'suspect_dataframe': suspect_df,
                          'latest_readings': latest_readings_df,
                          'map_display': map_display
                          }
    return dict_all

def udx(variable, dict_all, src):
    start, end         = times(day_period)
    df = getData.fromUOFile(variable) if src=='UDXFile' else getData.udx(variable)
    sensor_dfs         = allValues.udx(variable, df)
    latest_readings_df = latestValues.udx(df, sensor_dfs, src)
    display_graphs     = displayGraphs.udx(variable, sensor_dfs)
    suspect_df         = suspectReadings.udx(variable, df)
    map_display        = displayMaps.udx(variable, latest_readings_df)
    dict_all[variable] = {'start': start, 
                          'end': end,
                          'dataframe': df, 
                          'display_graphs': display_graphs, 
                          'suspect_dataframe': suspect_df,
                          'latest_readings': latest_readings_df,
                          'map_display': map_display
                          }
    return dict_all

