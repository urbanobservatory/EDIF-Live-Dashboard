# Returns a plotly gauge

import plotly.graph_objs as go

def gauge(value):
    if value <= 0: color = '#c0d8ff'
    elif 0 < value <= 10: color = '#8ab8ff'
    elif 10 < value <= 20: color = '#73bf69'
    elif 20 < value <= 30: color = '#eab839'
    elif 30 < value <= 40: color = '#eab839'
    elif value > 40: color = '#f2495c'
    return go.Indicator(
        mode = "gauge+number",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = '°C',
        gauge = {'axis': {'range': [-10, 40]}, 'bar': {'color': color}}
    )