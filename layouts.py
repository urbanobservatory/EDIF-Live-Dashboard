import plotly.graph_objects as go

def graph(src, location, variable, units):
    location = ', '.join(location)

    if src == 'UO' or src == 'UOFile':
        period = ['day', 1, 3, 5, 'd']
    elif src == 'UDX' or src == 'UDXFile':
        period = ['minute', 20, 40, 60, 'm']
    elif src == 'SUF':
        period = ['hour', 1, 2, 3, 'h']

    return go.Layout(
        title = dict(
            text = f'{variable}: {location}',
            x = 0.5
        ),
        showlegend = False, 
        autosize = True,
        margin = dict(t=80, b=60, l=40, r=20),
        hovermode = 'closest',
        hoverlabel = dict(namelength=-1),
        xaxis = dict(
            gridwidth=1, 
            gridcolor='#2e2f30',
            zerolinecolor='#2e2f30',
            rangeselector=dict(
                bgcolor='#111217',
                buttons=list([
                    dict(label="All",
                        step="all"),
                    dict(count=period[3],
                        label=str(period[3])+" "+period[4],
                        step=period[0],
                        stepmode="backward"),
                    dict(count=period[2],
                        label=str(period[2])+" "+period[4],
                        step=period[0],
                        stepmode="backward"),
                    dict(count=period[1],
                        label=str(period[1])+" "+period[4],
                        step=period[0],
                        stepmode="backward")
                ])
            ), #rangeslider=dict(visible=True),
        type="date"
        ),
        yaxis = dict(
            title = units,
            gridwidth=1, 
            gridcolor='#2e2f30',
            zerolinecolor='#2e2f30'
        ),
        paper_bgcolor='#181b1f',
        plot_bgcolor='#181b1f',
        font=dict(color="#ccccdc")
    )

def map(src, location, variable):
    return dict(
        title = f'{location} {variable} Map ({src})',
        colorbar = True,
        autosize = True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#ccccdc"),
        margin = dict(t=80, b=60, l=40, r=20),
        mapbox = dict(
            style = "carto-darkmatter", #"carto-positron"
            bounds = dict(west=-1.8, east=-1.4, south=54.85, north=55.1)
        )
    )

def gauge(src, location, variable):
    return dict(
       title = f'{location} Average {variable} ({src})',
       paper_bgcolor='rgba(0,0,0,0)',
       plot_bgcolor='rgba(0,0,0,0)',
       font=dict(color="#ccccdc")
    #    margin = dict(t=80, b=60, l=40, r=20),
    )

def card():
    return dict(
        autosize = True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#ccccdc"),
        margin = dict(t=80, b=60, l=40, r=20)
    )

def indicators(location, variables):
    v = ', '.join(variables)
    return dict(
        title = {
            'text': f'{location} Status Indicators (1H) [{v}]',
            'x': 0.5
        },
        autosize = True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#ccccdc"),
        # margin = dict(t=80, b=60, l=40, r=20),
        grid = {
            'rows': 2, 
            'columns': 2, 
            'pattern': "independent"
        },
        template = {
            'data' : {
                'indicator': [{
                    'mode' : "number+gauge"
                }]
            }
        }
    )