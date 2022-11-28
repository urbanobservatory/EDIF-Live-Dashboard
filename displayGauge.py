import gauge

def uo(df):
    return [gauge.gauge(round(df['Value'].mean(), 1))]

def udx(variable, df):
    return [gauge.gauge(round(df[variable+'.value'].mean(), 1))]