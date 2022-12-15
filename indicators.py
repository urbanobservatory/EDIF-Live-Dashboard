import time

def run(df):
    one_hour_ago = (time.time()*1000)-3600000
    df = df.loc[df['Timestamp'] >= one_hour_ago]

    sensors = df['ID'].nunique()
    records = len(df.index)
    
    return sensors, records