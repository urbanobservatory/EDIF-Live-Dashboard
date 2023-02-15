import time

import pandas as pd
from datetime import date, datetime, timedelta

from dateutil.relativedelta import relativedelta


from dash_data import getData, mapping

import math
import os
def day_store(variable, start,end):

    # start = datetime.strptime(day, '%Y-%m-%d')
    # end = datetime.strptime(day, '%Y-%m-%d') + timedelta(hours=23, minutes=59, seconds=59)

    # if start_date != None and end_date == None \
    # or start_date == None and end_date != None:
    #     raise PreventUpdate

    # elif start_date != None and end_date != None:
    #     start = datetime.strptime(start_date, '%Y-%m-%d')
    #     end = datetime.strptime(end_date, '%Y-%m-%d')
    #     end = end + timedelta(hours=23, minutes=59, seconds=59)
    #     print('start', start)
    #     print('end', end)
    TD = timedelta(minutes=30)
    start = datetime.min + math.floor((start - datetime.min ).total_seconds()/TD.total_seconds())*TD
    end = datetime.min + math.ceil((end - datetime.min ).total_seconds()/TD.total_seconds())*TD
    frame_path =  f'/cached/all-{start}-{end}-{variable}.csv'
    if os.path.exists(frame_path):
        df = pd.read_csv(frame_path,index_col=False)
    else:
        df = getData.run(variable, start, end)
        try:
            df.to_csv(frame_path)
        except:
            pass
    return df

while True:

    for var_name in mapping.variables().keys():
        end = datetime.now()
        df = day_store(var_name,end-timedelta(days=7),end)
    time.sleep(300)