# Returns a list of data frames for all sensor values for a given variable

import pandas as pd

def uo(variable, df):
    sensor_dfs=[]
    for i, l in enumerate(df['data.'+variable]):
        ds = pd.DataFrame(l)
        sensor_dfs.append(ds)
    return sensor_dfs

def udx(variable, df):
    #TODO: This
    pass