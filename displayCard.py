import plotly.graph_objs as go

def card(location, sensors_online, domain, title):
    return go.Indicator(
        title = title,
        mode = "number",
        value = sensors_online,
        # number = {'prefix': "Active Streams"},
        delta = {'position': "top", 'reference': 320},
        domain = domain
        )

def run(location, sensors_online, domain, title):
    return card(location, sensors_online, domain, title)