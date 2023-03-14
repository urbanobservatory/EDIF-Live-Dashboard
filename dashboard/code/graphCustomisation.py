import json

def customise(df, variable):
    if variable == 'PM2.5':
        df = df[df['Value'] <= 100]
    elif variable == "Temperature":
        df = df[df['Value'] <= 50]
    elif variable == 'Traffic Flow':
        df = df[df['Value'] != 0]
        #df = df[df['Value'] <= 400]
    elif variable == 'PM10':
        df = df[df['Value'] <= 50]

    if variable != 'Temperature':
        df = df[df['Value'] >= 0]

    return df