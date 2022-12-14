import plotly.graph_objs as go

def card(location, sensors_online, domain):
    return go.Indicator(
        title = f'Active Streams in {location}',
        mode = "number",
        value = sensors_online,
        # number = {'prefix': "Active Streams"},
        delta = {'position': "top", 'reference': 320},
        domain = domain
        )

def run(location, sensors_online, domain):
    return card(location, sensors_online, domain)