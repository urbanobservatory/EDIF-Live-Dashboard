# Returns a list of customised plotly graphs

import os
import pandas as pd
from dotenv import load_dotenv
import graphCustomisation
import graph

load_dotenv()
thin_data_by_factor_of = int(os.getenv('thin_data_by_factor_of'))

def uo(variable, sensor_dfs):
    display_graphs=[]
    for ds in sensor_dfs:
        ds = ds[ds['Flagged as Suspect Reading'] == False]
        ds, color = graphCustomisation.uo(ds, variable)
        ds['Datetime'] = pd.to_datetime(ds['Timestamp'], unit='ms')
        ds = ds.iloc[::thin_data_by_factor_of, :]
        try:
            name = ds['Sensor Name'].iloc[0]
        except:
            name = 'unknown sensor name'
        display_graphs.append(graph.uo(ds, name, color))
    return display_graphs

def udx(variable, sensor_dfs):
    #TODO: This
    pass