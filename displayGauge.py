import gauge

def display(df):
    return [gauge.gauge(round(df['Value'].mean(), 1))]