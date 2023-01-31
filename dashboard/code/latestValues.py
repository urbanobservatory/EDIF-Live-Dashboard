import os
import pandas as pd

import json


env_vars = json.load(open('/code/env.json'))
latest_reading_threshold = int(env_vars['latest_reading_threshold'])

def run(sensor_dfs):
    ds_list = []
    for sensor_df in sensor_dfs:
        ds_list.append(sensor_df.loc[
            (sensor_df['Timestamp'] == max(sensor_df['Timestamp']))])
    return pd.concat(ds_list)