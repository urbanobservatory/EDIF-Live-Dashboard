import plotly.graph_objs as go

def gauge(src, location, variable, units, value, domain):
    # default
    #TODO: Fix repeat colour codes
    minimum, maximum = -10, 40
    if value <= 0: color = '#c0d8ff'
    elif 0 < value <= 10: color = '#8ab8ff'
    elif 10 < value <= 20: color = '#73bf69'
    elif 20 < value <= 30: color = '#eab839'
    elif 30 < value <= 40: color = '#eab839'
    elif value > 40: color = '#f2495c'

    if variable == 'Temperature':
        minimum, maximum = -10, 40
        if value <= 0: color = '#c0d8ff'
        elif 0 < value <= 10: color = '#8ab8ff'
        elif 10 < value <= 20: color = '#73bf69'
        elif 20 < value <= 30: color = '#eab839'
        elif 30 < value <= 40: color = '#eab839'
        elif value > 40: color = '#f2495c'

    elif variable == 'Humidity':
        minimum, maximum = 0, 100
        if 0 < value <= 20: color = '#8ab8ff'
        elif 20 < value <= 40: color = '#73bf69'
        elif 40 < value <= 60: color = '#eab839'
        elif 60 < value <= 80: color = '#eab839'
        elif value > 80: color = '#f2495c'

    elif variable == 'Pressure':
        minimum, maximum = 87000, 108480
        if 87000 < value <= 91296: color = '#8ab8ff'
        elif 91296 < value <= 95592: color = '#73bf69'
        elif 95592 < value <= 99888: color = '#eab839'
        elif 99888 < value <= 104184: color = '#eab839'
        elif 104184 < value <= 108480: color = '#eab839'
        elif value > 108480: color = '#f2495c'

    return go.Indicator(
        mode = "gauge+number",
        value = value,
        number = {'suffix': ' '+units},
        title = f'{variable} Average',
        gauge = {
            'axis': {'range': [minimum, maximum]}, 
            'bar': {'color': color},
            'threshold' : {
                'line': {
                    'color': "#ccccdc", 
                    'width': 2
                    }, 
                'thickness': 0.75, 
                'value': 0
                }
        },
        domain = domain
    )

def run(src, location, variable, units, value, domain):
    return [gauge(src, location, variable, units, value, domain)]