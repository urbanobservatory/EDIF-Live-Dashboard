def graph(variable, units, src, location):
    if src == 'UO' or src == 'UOFile':
        period = ['day', 1, 3, 5, 'd']
    elif src == 'UDX' or src == 'UDXFile':
        period = ['minute', 20, 40, 60, 'm']
    return dict(title=f'{location} {variable} ({src})',
        showlegend = False, 
        autosize = True,
        margin = dict(t=80, b=60, l=40, r=20),
        hovermode = 'closest',
        hoverlabel = dict(namelength=-1),
        xaxis = dict(
            rangeselector=dict(
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
        yaxis = dict(title = units)
    )

def map(variable, src, location):
    return dict(
        title = f'{location} {variable} Map ({src})',
        colorbar = True,
        autosize = True,
        margin = dict(t=80, b=60, l=40, r=20),
        mapbox = dict(
            style = "carto-positron", # "carto-darkmatter"
            bounds = dict(west=-1.8, east=-1.4, south=54.85, north=55.1)
        )
    )

def gauge(variable, src, location):
    return dict(
       title = f'{location} average {variable} ({src})' 
    )