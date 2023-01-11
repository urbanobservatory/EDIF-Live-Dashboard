import os
import pandas as pd
import time
from dotenv import load_dotenv

load_dotenv()
latest_reading_threshold = int(os.getenv('latest_reading_threshold'))

def run(sensor_dfs):
    ds_list = []
    for sensor_df in sensor_dfs:
        ds_list.append(sensor_df.loc[
            (sensor_df['Timestamp'] == max(sensor_df['Timestamp']))])
    return pd.concat(ds_list)