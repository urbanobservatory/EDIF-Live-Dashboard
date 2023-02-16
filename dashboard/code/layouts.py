import plotly.graph_objects as go

theme = 'dark'

if theme == 'light':
    theme = {
        'text': '#000000',
        'background_body': '#ffffff',
        'background_frame': '#dbdbd9',
        'gridlines': '#ffffff',
        'map': 'carto-positron'
    }
elif theme == 'dark':
    theme = {
        'text': '#ccccdc',
        'background_body': '#111217',
        'background_frame': '#181b1f',
        'gridlines': '#2e2f30',
        'map': 'carto-darkmatter'
    }

def scatterAll(variable, units):

    period = ['minute', 20, 40, 60, 'm']

    return go.Layout(
        title = dict(
            text = f'{variable} Timeline',
            x = 0.5
        ),
        height = 300,
        showlegend = False, 
        autosize = True,
        margin = dict(t=60, b=20, l=20, r=20),
        hovermode = 'closest',
        hoverlabel = dict(namelength=-1),
        xaxis = dict(
            # domain = [0,0.7],
            gridwidth=1, 
            gridcolor=theme['gridlines'],
            zerolinecolor=theme['gridlines'],
            type="date"
            # rangeselector=dict(
            #     bgcolor='#111217',
            #     buttons=list([
            #         dict(label="All",
            #             step="all"),
            #         dict(count=period[3],
            #             label=str(period[3])+" "+period[4],
            #             step=period[0],
            #             stepmode="backward"),
            #         dict(count=period[2],
            #             label=str(period[2])+" "+period[4],
            #             step=period[0],
            #             stepmode="backward"),
            #         dict(count=period[1],
            #             label=str(period[1])+" "+period[4],
            #             step=period[0],
            #             stepmode="backward")
            #     ])
            # ), # rangeslider=dict(visible=True)
        ),
        yaxis = dict(
            title = units,
            gridwidth=1, 
            gridcolor=theme['gridlines'],
            zerolinecolor=theme['gridlines']
        ),
        paper_bgcolor=theme['background_frame'],
        plot_bgcolor=theme['background_frame'],
        font = {
            'color': theme['text']
        },
        # xaxis2 = dict(
        #     domain = [0.7,1],
        # )
    )


def scatterHover(variable, units):

    period = ['minute', 20, 40, 60, 'm']

    return go.Layout(
        title = dict(
            text = f'{variable} Timeline',
            x = 0.5
        ),
        height = 270,
        showlegend = False, 
        autosize = True,
        margin = dict(t=60, b=20, l=20, r=20),
        hovermode = 'closest',
        hoverlabel = dict(namelength=-1),
        xaxis = dict(
            gridwidth=1, 
            gridcolor=theme['gridlines'],
            zerolinecolor=theme['gridlines'],
            type="date",
            rangeslider=dict(visible=True)
        ),
        yaxis = dict(
            title = units,
            gridwidth=1, 
            gridcolor=theme['gridlines'],
            zerolinecolor=theme['gridlines']
        ),
        paper_bgcolor=theme['background_frame'],
        plot_bgcolor=theme['background_frame'],
        font=dict(color=theme['text'])
    )


def scatter3d(variable, units):
    return go.Layout(
        title = dict(
            text = f'{variable} 3D Scatter',
            x = 0.5
        ),
        height = 600,
        showlegend = False, 
        autosize = True,
        margin = dict(t=60, b=20, l=20, r=20),
        hovermode = 'closest',
        hoverlabel = dict(namelength=-1),
        scene = {
            'xaxis': {
                'title': '', #'Date',
                'backgroundcolor': theme['background_frame'],
                'gridcolor': theme['gridlines'],
                'showbackground': True,
                'zerolinecolor': theme['gridlines']
            },
            'yaxis': {
                'title': '', #'Source',
                'backgroundcolor': theme['background_frame'],
                'gridcolor': theme['gridlines'],
                'showbackground': True,
                'zerolinecolor': theme['gridlines']
            },
            'zaxis': {
                'title': units,
                'backgroundcolor': theme['background_frame'],
                'gridcolor': theme['gridlines'],
                'showbackground': True,
                'zerolinecolor': theme['gridlines']
            }
        },
        paper_bgcolor=theme['background_frame'],
        plot_bgcolor=theme['background_frame'],
        font=dict(color=theme['text'])
    )


def boxplot(variable, units):
    return go.Layout(
        title = dict(
            text = f'{variable} Box Plot',
            x = 0.5
        ),
        height = 300,
        showlegend = False, 
        autosize = True,
        margin = dict(t=60, b=20, l=20, r=20),
        hovermode = 'closest',
        hoverlabel = dict(namelength=-1),
        xaxis = dict(
            # title = 'Source',
            gridwidth=1, 
            gridcolor=theme['gridlines'],
            zerolinecolor=theme['gridlines']
        ),
        yaxis = dict(
            title = units,
            gridwidth=1, 
            gridcolor=theme['gridlines'],
            zerolinecolor=theme['gridlines']
        ),
        paper_bgcolor=theme['background_frame'],
        plot_bgcolor=theme['background_frame'],
        font=dict(color=theme['text'])
    )


def histogram(variable, units):
    return go.Layout(
        title = dict(
            text = f'{variable} Histogram',
            x = 0.5
        ),
        height = 270,
        showlegend = False, 
        autosize = True,
        margin = dict(t=60, b=20, l=20, r=20),
        hovermode = 'closest',
        hoverlabel = dict(namelength=-1),
        xaxis = dict(
            title = units,
            gridwidth=1, 
            gridcolor=theme['gridlines'],
            zerolinecolor=theme['gridlines']
        ),
        yaxis = dict(
            title = 'Instances',
            gridwidth=1, 
            gridcolor=theme['gridlines'],
            zerolinecolor=theme['gridlines']
        ),
        paper_bgcolor=theme['background_frame'],
        plot_bgcolor=theme['background_frame'],
        font=dict(color=theme['text'])
    )

def map(variable, map_selection): #, map_relayout):

    # if map_selection == None:
    map_bounds = {
        'west': -6,
        'north': 56,
        'east': 2,
        'south': 50
    }
    zoom = 6
    # else:
    #     map_bounds = {
    #         'west': map_selection['range']['mapbox'][0][0],
    #         'north': map_selection['range']['mapbox'][0][1],
    #         'east': map_selection['range']['mapbox'][1][0],
    #         'south': map_selection['range']['mapbox'][1][1]
    #     }
    #     zoom = 10

    mid_lat = (map_bounds['north']+map_bounds['south'])/2
    mid_lon = (map_bounds['east']+map_bounds['west'])/2

    return go.Layout(
        title = dict(
            text = f'{variable} Latest',
            x = 0.5
        ),
        autosize = True,
        height = 1280,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=theme['text']),
        margin = dict(t=20, b=0, l=0, r=0),
        mapbox = dict(
            style = theme['map'],
            # NEWCATSLE BOUNDS
            # bounds = dict(west=-1.8, east=-1.4, south=54.85, north=55.1)
            # England BOUNDS
            # bounds = dict(
            #     west = map_bounds['west'], 
            #     east = map_bounds['east'], 
            #     south = map_bounds['south'], 
            #     north = map_bounds['north']
            # ),
            center = go.layout.mapbox.Center(lat=mid_lat, lon=mid_lon), 
            zoom = zoom
        )
    )

def gauge(src, location, variable):
    return dict(
       title = f'{location} Average {variable} ({src})',
       paper_bgcolor='rgba(0,0,0,0)',
       plot_bgcolor='rgba(0,0,0,0)',
       font=dict(color=theme['text'])
    #    margin = dict(t=80, b=60, l=40, r=20),
    )

def card():
    return dict(
        autosize = True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=theme['text']),
        margin = dict(t=80, b=60, l=40, r=20)
    )

def indicators(variable):
    return go.Layout(
        # title = {
        #     'text': f'{variable} Overview',
        #     'x': 0.5,
        #     'font_size': 30
        # },
        height = 150,
        autosize = True,
        paper_bgcolor=theme['background_frame'],
        plot_bgcolor=theme['background_frame'],
        font = {
            'color': theme['text']
        },
        margin = dict(t=40, b=40, l=30, r=30),
        grid = {
            'rows': 1, 
            'columns': 3, 
            'pattern': "independent"
        },
        template = {
            'data' : {
                'indicator': [{
                    'mode' : "number"
                }]
            }
        }
    )