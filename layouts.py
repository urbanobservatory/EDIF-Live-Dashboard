#TODO: Remove hard coded titles

def graph(variable, units, src, location):
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
                    dict(count=5,
                        label="5d",
                        step="day",
                        stepmode="backward"),
                    dict(count=3,
                        label="3d",
                        step="day",
                        stepmode="backward"),
                    dict(count=1,
                        label="1d",
                        step="day",
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