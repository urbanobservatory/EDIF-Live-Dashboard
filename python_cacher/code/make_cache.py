import time
import pandas as pd
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from dash_data import getData, mapping
import os

import warnings
warnings.filterwarnings("ignore")

cache_path = '/cached/'


def get_days(start_date, end_date):
    days = []

    start_date = date(
        int(start_date.split('-')[0]),
        int(start_date.split('-')[1]),
        int(start_date.split('-')[2]))
    end_date = date(
        int(end_date.split('-')[0]),
        int(end_date.split('-')[1]),
        int(end_date.split('-')[2]))

    delta = end_date - start_date

    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        days.append(day)

    return days


def get_start_end_date(start_date, end_date, day_period=7):
    start_date = datetime.now()-relativedelta(days=day_period)
    end_date   = datetime.now()
    start_date = datetime.strftime(start_date, '%Y-%m-%d')
    end_date = datetime.strftime(end_date, '%Y-%m-%d')
    return start_date, end_date


def get_start_end_time(day):
    start = datetime.strftime(day, '%Y-%m-%d, %H:%M:%S')
    start = datetime.strptime(start, '%Y-%m-%d, %H:%M:%S')
    end = start + timedelta(hours=23, minutes=59, seconds=59)
    return start, end


def select(df, item_selection):
    selected = []
    for i in range(0, len(item_selection['points'])):
        id = item_selection['points'][i]['text'].split(':')[0]
        selected.append(id)
    return df.loc[df['ID'].isin(selected)]


def day_store(variable, start_date, end_date, dfs=[], today=None):
    # Get past n days if no dates selected
    if start_date == None or end_date == None:
        start_date, end_date = get_start_end_date(start_date, end_date)
    
    # Request/get df for each day from cache
    days = get_days(start_date, end_date)

    # If today in days, request fresh data
    if days[-1] == datetime.today().date():
        days.pop()

    # Append to dfs
    for day in days:
        start, end = get_start_end_time(day)
        day_path = f'{cache_path}{variable}-{day}.csv'
        if os.path.exists(day_path):
            print('CACHE - ALREADY STORED', variable, day_path)
        else:
            print('CACHE - RUNNING', variable, day_path)
            df = getData.pull_data(variable, start, end)
            if df is not None:
                df.to_csv(day_path)
                dfs.append(df)

    # Concatenate dfs
    if len(dfs) > 0:
        return pd.concat(dfs)


while True:
    for variable in mapping.variables().keys():
        df = day_store(variable, None, None)
    time.sleep(300)