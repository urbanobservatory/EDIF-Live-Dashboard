def graph(src, location, variable, units):
    if src == 'UO' or src == 'UOFile':
        period = ['day', 1, 3, 5, 'd']
    elif src == 'UDX' or src == 'UDXFile':
        period = ['minute', 20, 40, 60, 'm']
    elif src == 'SUF':
        period = ['hour', 1, 2, 3, 'h']
    #TODO: Remove all if statements like one below and have associated display names for variables
    if variable == 'intensity' or variable == 'Plates Out':
        variable = 'Traffic Flow'
    elif variable == 'pm25': variable = 'PM2.5'
    elif variable == 'temperature': variable = 'Temperature'
    return dict(title=f'{location} {variable} ({src})',
        showlegend = False, 
        autosize = True,
        margin = dict(t=80, b=60, l=40, r=20),
        hovermode = 'closest',
        hoverlabel = dict(namelength=-1),
        xaxis = dict(
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
        yaxis = dict(title = units),
        paper_bgcolor='#181b1f',
        plot_bgcolor='#181b1f',
        font=dict(color="#ccccdc")
    )

def map(src, location, variable):
    #TODO: Remove all if statements like one below and have associated display names for variables
    if variable == 'intensity' or variable == 'Plates Out':
        variable = 'Traffic Flow'
    elif variable == 'pm25': variable = 'PM2.5'
    elif variable == 'temperature': variable = 'Temperature'
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
    #TODO: Remove all if statements like one below and have associated display names for variables
    if variable == 'intensity' or variable == 'Plates Out':
        variable = 'Traffic Flow'
    elif variable == 'pm25': variable = 'PM2.5'
    elif variable == 'temperature': variable = 'Temperature'
    return dict(
       title = f'{location} Average {variable} ({src})',
       paper_bgcolor='rgba(0,0,0,0)',
       plot_bgcolor='rgba(0,0,0,0)',
       font=dict(color="#ccccdc")
    #    margin = dict(t=80, b=60, l=40, r=20),
    )