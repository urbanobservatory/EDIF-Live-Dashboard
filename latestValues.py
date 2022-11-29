import os
import pandas as pd
import time
from dotenv import load_dotenv

load_dotenv()
latest_reading_threshold = int(os.getenv('latest_reading_threshold'))

def uo(df, sensor_dfs, src):
    ds_list = []
    for sensor_df in sensor_dfs:
        if src == 'UOFile':
            ds_list.append(sensor_df.loc[
                    (sensor_df['Timestamp'] == max(sensor_df['Timestamp'])) &
                    (sensor_df['Flagged as Suspect Reading'] == False)])
        elif src == 'UO':
            ds_list.append(sensor_df.loc[
                    (sensor_df['Timestamp'] == max(sensor_df['Timestamp'])) &
                    (sensor_df['Timestamp'] > (int(time.time())*1000)-(latest_reading_threshold*60000)) &
                    (sensor_df['Flagged as Suspect Reading'] == False)])
    ds = pd.concat(ds_list)
    ds = ds.drop('Flagged as Suspect Reading', axis=1)
    return pd.merge(ds, df, how='inner', left_on='Sensor Name', right_on='Sensor Name.0')

def udx(variable, df, sensor_dfs, src):
    ds_list = []
    for sensor_df in sensor_dfs:
        if variable == 'pm25' or variable == 'intensity':
            ds_list.append(sensor_df.loc[
                (sensor_df['Timestamp'] == max(sensor_df['Timestamp']))])
        elif variable == 'temperature':
            ds_list.append(sensor_df.loc[
                (sensor_df['Timestamp'] == max(sensor_df['Timestamp']))])
    return pd.concat(ds_list)