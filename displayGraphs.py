# Returns a list of customised plotly graphs

import graphCustomisation
import os
from dotenv import load_dotenv
import plotly.graph_objs as go

load_dotenv()
pm25_display_limit = int(os.getenv('pm25_display_limit'))
temperature_display_limit = int(os.getenv('temperature_display_limit'))

def plot(df, name, color):
    return go.Scatter(x=list(df['Datetime']),
                      y=list(df['Value']),
                      mode='markers',
                      #marker_symbol='circle-open',
                      marker_color=color,
                      opacity=0.4,
                      name=name)

def run(variable, sensor_dfs):
    display_graphs=[]
    for ds in sensor_dfs:
        ds, color = graphCustomisation.customise(ds, variable)
        try:
            name = ds['ID'].iloc[0]
        except:
            name = 'unknown sensor name'
        display_graphs.append(plot(ds, name, color))
    return display_graphs