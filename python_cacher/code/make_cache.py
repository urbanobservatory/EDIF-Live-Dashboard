import time
import json
import pandas as pd
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from dash_data import getData, mapping
import traceback
import os

import warnings
warnings.filterwarnings("ignore")

env_vars = json.load(open('/code/env.json'))

cache_path = '/cached/'

# def get_days_between(start_date, end_date):
#     days = []

#     start_date = date(
#         int(start_date.split('-')[0]),
#         int(start_date.split('-')[1]),
#         int(start_date.split('-')[2]))
#     end_date = date(
#         int(end_date.split('-')[0]),
#         int(end_date.split('-')[1]),
#         int(end_date.split('-')[2]))

#     delta = end_date - start_date

#     for i in range(delta.days + 1):
#         day = start_date + timedelta(days=i)
#         days.append(day)

#     return days


def get_start_end_date():
    start_date = datetime.now()-relativedelta(
        seconds=int(env_vars['request_period']))
    end_date   = datetime.now()
    #start_date = datetime.strftime(start_date, '%Y-%m-%d, %H:%M:%S')
    #end_date = datetime.strftime(end_date, '%Y-%m-%d, %H:%M:%S')
    return start_date, end_date


# def get_start_end_time(day):
#     start = datetime.strftime(day, '%Y-%m-%d, %H:%M:%S')
#     start = datetime.strptime(start, '%Y-%m-%d, %H:%M:%S')
#     end = start + timedelta(hours=23, minutes=59, seconds=59)
#     return start, end


def day_store(variable):
    try:
        start_date, end_date = get_start_end_date()
        df = getData.pull_data(variable, start_date, end_date)

        if df is None:
            return

        days = df['Datetime'].dt.normalize().unique()

        print('days', type(days), days, flush=True)

        for day in days:
            day = pd.to_datetime(str(day))
            print('day', type(day), day, flush=True)
            df2 = df.loc[df['Datetime'].dt.normalize() == day]
            day = day.strftime('%Y-%m-%d')
            day_path = f'{cache_path}{variable}-{day}.csv'

            if os.path.exists(day_path):
                pd.read_csv(day_path)\
                .append(df2)\
                .drop_duplicates()\
                .sort_values(by='Datetime', inplace = True)\
                .to_csv(day_path, mode='w', header=False)
            else:
                df2.sort_values(by='Datetime', inplace = True)
                df2.to_csv(day_path, mode='w', header=True)
    except Exception:
        print('MAKE CACHE ERROR')
        print(traceback.format_exc(), flush=True)

        
    # days = get_days_between(start_date, end_date)

    # for day in reversed(days):
    #     start, end = get_start_end_time(day)
    #     day_path = f'{cache_path}{variable}-{day}.csv'

    #     # if day == datetime.today().date():
    #     #print('CACHE - REFETCH TODAY', variable, day_path)
    #     print('CACHE', variable, day_path)
    #     df = getData.pull_data(variable, start, end)
    #     if df is not None:
    #         df.to_csv(day_path)

        # elif os.path.exists(day_path):
        #     print('CACHE - ALREADY STORED', variable, day_path)

        # else:
        #     print('CACHE - RUNNING', variable, day_path)
        #     df = getData.pull_data(variable, start, end)
        #     if df is not None:
        #         df.to_csv(day_path)


while True:
    for variable in mapping.variables().keys():
        day_store(variable)
    print('sleeping')
    time.sleep(int(env_vars['update_frequency']))