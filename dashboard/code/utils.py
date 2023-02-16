from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


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


def get_start_end_date(start_date, end_date, day_period=3):
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