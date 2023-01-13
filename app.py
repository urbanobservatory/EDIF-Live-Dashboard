import os
import dash
import datetime
from dash import dcc, html, ctx
from dash.dependencies import Output, Input, State
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import pandas as pd
from flask_caching import Cache

import figures
import getData
import allValues
import latestValues

load_dotenv()
update_frequency = int(os.getenv('update_frequency'))
day_period = float(os.getenv('day_period'))

# APPLICATION
app = dash.Dash(__name__)
server = app.server

CACHE_CONFIG = {
    # try 'FileSystemCache' if you don't want to setup redis
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379')
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)


app.layout = html.Div([

    html.Div([
        html.Div([
            html.Div([
                html.Div(
                    dcc.Dropdown(
                        id='checklist',
                        options=[
                            'PM2.5',
                            'Traffic Flow',
                            'Black Carbon',
                            'Nitric Oxide',
                            'Ozone',
                            'Nitrogen Dioxide',
                            'PM1',
                            'PM10',
                            'Temperature',
                            'Humidity',
                            'Pressure'
                        ],
                        value='PM2.5',
                        clearable=False
                        # style={
                        #     'color': '#ccccdc', 
                        #     'font-size': 20,
                        #     'text-align': 'center'
                        # }
                    )
                )
            ], className='dropDown')
        ], className='four columns'),
        html.Div([
            html.Div(
                html.H1('EDIF Live Dashboard'),
                className="banner"),
        ], className='four columns'),
        html.Div([
            html.Div([

            ], className='banner')
        ], className='four columns')
    ], className='row'),

    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(id='Map')
                ], className='twelve columns')
            ], className='row')
        ], className='four columns'),
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(id='Indicators')
                    ], className='six columns'),
                    html.Div([
                        html.Div([
                            html.Label(
                                children=[
                                    html.Span('Suspect Reading Logs', className='labels')
                                ]
                            ),
                            #TODO: Create layout for datatable
                            dash.dash_table.DataTable(
                                id='Suspect Table',
                                page_size=12,
                                style_table={
                                    'height': '200px', 
                                    'width': '550px',
                                    'overflowY': 'auto'
                                    },
                                style_as_list_view=True,
                                style_cell=dict(backgroundColor='#111217'),
                                style_header=dict(backgroundColor='#181b1f',
                                                fontWeight='bold',
                                                color='#ccccdc'),
                                style_data=dict(color="#ccccdc")
                            )
                        ], className='row'),
                        html.Div([
                            dash.dash_table.DataTable(
                            id='Alerts Table',
                            page_size=12,
                            style_table={
                                'height': '100px', 
                                'width': '550px',
                                'overflowY': 'auto'
                                },
                            style_as_list_view=True,
                            style_cell=dict(backgroundColor='#111217', textAlign='center'),
                            style_header=dict(backgroundColor='#181b1f',
                                            fontWeight='bold',
                                            color='#ccccdc'),
                            style_data=dict(color="#ccccdc")
                        )
                        ], className='row')
                    ], className='six columns')
                ])
            ], className="row"),
            html.Div([
                html.Div([
                    dcc.Graph(id='Scatter All')
                ], className='twelve columns')
            ], className="row"),
            html.Div([
                html.Div([
                    dcc.Graph(id='Scatter Hover')
                ], className='six columns')
            ], className="row")
        ], className="eight columns")
    ], className="row"),

    dcc.Interval(
        id='interval-component',
        interval=60000*update_frequency,
        n_intervals=0),
    dcc.Store(id='signal')

], className="body")


# CALLBACKS
@cache.memoize()
def global_store(variable):
    src = 'UDX'
    locations = ['Newcastle', 'Manchester', 'Birmingham']

    start = datetime.datetime.now()-relativedelta(days=day_period)
    end   = datetime.datetime.now()

    dfs = []
    for location in locations:
        try:
            df = getData.fetch(src, location, variable, start, end)
            dfs.append(df)
        except:
            continue

    df = pd.concat(dfs)

    return df


@app.callback(
    Output('signal', 'data'), 
    [
        Input('interval-component', 'n_intervals'),
        Input('checklist', 'value')
    ])
def compute_value(n, variable):
    global_store(variable)
    return variable


@app.callback(
    Output('Map', 'figure'),
    [
        Input('signal', 'data'),
        Input('Map', 'selectedData')#,
        # Input('Map', 'relayoutData')
    ])
def update_map(variable, map_selection): #, map_relayout):
    df = global_store(variable)
    sensor_dfs = allValues.run(df)
    latest_df = latestValues.run(sensor_dfs)
    return figures.map(latest_df, map_selection) #, map_relayout)


@app.callback(
    Output('Scatter All', 'figure'),
    [
        Input('signal', 'data'),
        Input('Map', 'selectedData')
    ])
def update_scatter_all(variable, map_selection):
    df = global_store(variable)
    triggered = ctx.triggered_id
    selected = []
    if triggered == 'Map':
        for i in range(0, len(map_selection['points'])):
            id = map_selection['points'][i]['text'].split(':')[0]
            selected.append(id)
        df = df.loc[df['ID'].isin(selected)]
    return figures.scatter_all(df)


@app.callback(
    Output('Scatter Hover', 'figure'),
    [
        Input('signal', 'data'), 
        Input('Map', 'hoverData'),
        Input('Scatter All', 'hoverData')
    ])
def update_scatter_hover(variable, map_hover, scatter_hover):
    df = global_store(variable)
    triggered = ctx.triggered_id
    if triggered == 'signal':
        df = df.sample()
    elif triggered == 'Map':
        id = map_hover['points'][0]['text'].split(':')[0]
        df = df.loc[df['ID'].isin([id])]
    elif triggered == 'Scatter All':
        id = scatter_hover['points'][0]['text'].split(':')[0]
        df = df.loc[df['ID'].isin([id])]
    return figures.scatter_hover(df)


@app.callback(
    Output('Indicators', 'figure'),
    [
        Input('signal', 'data'), 
        Input('Map', 'selectedData')
    ])
def update_indicators(variable, map_selection):
    df = global_store(variable)
    triggered = ctx.triggered_id
    selected = []
    if triggered == 'Map':
        for i in range(0, len(map_selection['points'])):
            id = map_selection['points'][i]['text'].split(':')[0]
            selected.append(id)
        df = df.loc[df['ID'].isin(selected)]
    return figures.indicators(df)


# For if CSS Stylesheet does not load
# css_directory = os.getcwd()
# stylesheets = ['stylesheet.css']
# static_css_route = '/static/'

# @app.server.route('{}<stylesheet>'.format(static_css_route))
# def serve_stylesheet(stylesheet):
#     if stylesheet not in stylesheets:
#         raise Exception(
#             '"{}" is excluded from the allowed static files'.format(
#                 stylesheet
#             )
#         )
#     return flask.send_from_directory(css_directory, stylesheet)

# for stylesheet in stylesheets:
#     app.css.append_css({"external_url": "/static/{}".format(stylesheet)})
    

# Run App
if __name__ == "__main__":
    app.run_server(debug=True, processes=6, threaded=False)