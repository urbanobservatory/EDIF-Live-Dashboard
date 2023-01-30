import os
import dash
from datetime import datetime
from dash import dcc, html, ctx
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
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
        html.Div(
            html.H1('EDIF - Live Dashboard Demo'),
            className="title"),
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='checklist',
                    options=[
                        'PM1',
                        'PM2.5',
                        'PM4',
                        'PM10',
                        'Traffic Flow',
                        'Black Carbon',
                        'Nitric Oxide',
                        'Ozone',
                        'Nitrogen Dioxide',
                        'Sulfur Dioxide',
                        'Temperature',
                        'Humidity',
                        'Pressure'
                    ],
                    value='PM2.5',
                    clearable=False)
            ], className='dropDown')
        ], className='dropDownBox'),
        html.Div([
            html.Div([
                dcc.DatePickerRange(
                    id='date-picker-range',
                    month_format='Do-MMM-Y')
            ], className='calendar')
        ], className='calendarBox'),
        html.Div([
            html.Div([
                html.Button(
                    'Refresh',
                    id='Refresh Button',
                    n_clicks = 0)
            ], className='refresh')
        ], className='refreshBox')
    ], className='banner'),

    # html.Div([
    #     html.Div([
    #     ], className='divider')
    # ], className='row'),

    html.Br(),

    html.Div([
        html.Div([

            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            dcc.Graph(id='Indicators A')
                        ], className='twelve columns')
                    ])
                ], className="row"),

                html.Div([
                    html.Div([
                        html.Div([
                            dcc.Graph(id='Indicators B')
                        ], className='twelve columns')
                    ])
                ], className="row")
            ], className='graph'),

            html.Br(),
            html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(id='Scatter All')
                    ], className='graph')
                ], className='twelve columns'),
            ], className="row"),

            html.Br(),
            html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(id='Scatter Hover')
                    ], className='graph')
                ], className='six columns'),
                html.Div([
                    html.Div([
                        dcc.Graph(id='Histogram')
                    ], className='histogram')
                ], className='six columns')
            ], className='row')

        ], className="eight columns"),
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(id='Map')
                    ], className='map')
                ], className='twelve columns')
            ], className='row')
        ], className='four columns')
    ], className="row"),

    html.Div([
        html.Div([
        ], className='divider')
    ], className='row'),

    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Label(
                        children=[
                            html.Span('Stream Health', className='labels')
                        ]
                    ),
                    dash.dash_table.DataTable(
                        id = 'Health Table',
                        page_size = 12,
                        style_table = {
                            'overflowY': 'auto'},
                        style_as_list_view = True,
                        style_cell = {
                            'backgroundColor': '#111217', 
                            'textAlign': 'center'},
                        style_header = {
                            'backgroundColor': '#181b1f',
                            'fontWeight': 'bold',
                            'color': '#ccccdc'},
                        style_data_conditional = [
                            {
                                'if': {
                                    'filter_query': "{Alert} contains 'Online'"
                                },
                                'backgroundColor': '#00cc96'
                            },
                            {
                                'if': {
                                    'filter_query': "{Alert} contains 'Offline'"
                                },
                                'backgroundColor': '#ef553b'
                            }
                            
                        ]
                    )
                ], className='healthTable')
            ], className='four columns'),
            html.Div([
                html.Div([
                    html.Label(
                        children=[
                            html.Span('Suspect Reading Logs', className='labels')
                        ]),
                    dash.dash_table.DataTable(
                        id = 'Suspect Table',
                        page_size = 12,
                        style_table = {
                            'overflowY': 'auto'},
                        style_as_list_view = True,
                        style_cell = {
                            'backgroundColor': '#111217'},
                        style_header = {
                            'backgroundColor': '#181b1f',
                            'fontWeight': 'bold',
                            'color': '#ccccdc'},
                        style_data = {'color': "#ccccdc"}
                    )
                ], className='suspectTable')
            ], className='eight columns')
        ], className='table')
        
    ], className='row'),
    

    dcc.Interval(
        id='interval-component',
        interval=60000*update_frequency,
        n_intervals=0),
    dcc.Store(id='signal')

], className="body")


# CALLBACKS
@cache.memoize()
def global_store(variable, start_date=None, end_date=None):

    if start_date != None and end_date != None:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        print(start, end)
    else:
        start = datetime.now()-relativedelta(days=day_period)
        end   = datetime.now()

    df = getData.run(variable, start, end)

    return df


@app.callback(
    Output('signal', 'data'), 
    [
        Input('interval-component', 'n_intervals'),
        Input('checklist', 'value'),
        Input('Refresh Button', 'n_clicks')
    ])
def compute_value(intervals, variable, clicks):
    global_store(variable)
    return variable


@app.callback(
    Output('Map', 'figure'),
    [
        Input('signal', 'data'),
        Input('Map', 'selectedData'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')#,
        # Input('Map', 'relayoutData')
    ])
def update_map(variable, map_selection, start_date, end_date): #, map_relayout):
    df = global_store(variable, start_date, end_date)
    sensor_dfs = allValues.run(df)
    latest_df = latestValues.run(sensor_dfs)
    return figures.map(latest_df, map_selection) #, map_relayout)


@app.callback(
    Output('Scatter All', 'figure'),
    [
        Input('signal', 'data'),
        Input('Map', 'selectedData'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ])
def update_scatter_all(variable, map_selection, start_date, end_date):
    df = global_store(variable, start_date, end_date)
    selected = []
    if 'Map' == ctx.triggered_id:
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
        Input('Scatter All', 'hoverData'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ])
def update_scatter_hover(variable, map_hover, scatter_hover, start_date, end_date):
    df = global_store(variable, start_date, end_date)
    if 'date-picker-range' == ctx.triggered_id:
        raise PreventUpdate
    elif 'signal' == ctx.triggered_id:
        random_df = df.sample().reset_index()
        random_id = random_df['ID'].iloc[0]
        df = df.loc[df['ID'] == random_id]
    elif 'Map' == ctx.triggered_id:
        id = map_hover['points'][0]['text'].split(':')[0]
        df = df.loc[df['ID'].isin([id])]
    elif 'Scatter All' == ctx.triggered_id:
        id = scatter_hover['points'][0]['text'].split(':')[0]
        df = df.loc[df['ID'].isin([id])]
    return figures.scatter_hover(df)


@app.callback(
    Output('Indicators A', 'figure'),
    [
        Input('signal', 'data'), 
        Input('Map', 'selectedData'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ])
def update_indicators(variable, map_selection, start_date, end_date):
    df = global_store(variable, start_date, end_date)
    selected = []
    if 'Map' == ctx.triggered_id:
        for i in range(0, len(map_selection['points'])):
            id = map_selection['points'][i]['text'].split(':')[0]
            selected.append(id)
        df = df.loc[df['ID'].isin(selected)]
    return figures.indicatorsA(df)


@app.callback(
    Output('Indicators B', 'figure'),
    [
        Input('signal', 'data'), 
        Input('Map', 'selectedData'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ])
def update_indicators(variable, map_selection, start_date, end_date):
    df = global_store(variable, start_date, end_date)
    selected = []
    if 'Map' == ctx.triggered_id:
        for i in range(0, len(map_selection['points'])):
            id = map_selection['points'][i]['text'].split(':')[0]
            selected.append(id)
        df = df.loc[df['ID'].isin(selected)]
    return figures.indicatorsB(df)


@app.callback(
    Output('Histogram', 'figure'),
    [
        Input('signal', 'data'), 
        Input('Map', 'selectedData'),
        Input('Scatter All', 'selectedData'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ])
def update_histogram(variable, map_selection, scatter_selection, start_date, end_date):
    df = global_store(variable, start_date, end_date)
    selected = []
    if 'Map' == ctx.triggered_id:
        for i in range(0, len(map_selection['points'])):
            id = map_selection['points'][i]['text'].split(':')[0]
            selected.append(id)
        df = df.loc[df['ID'].isin(selected)]
    if 'Scatter All' == ctx.triggered_id:
        for i in range(0, len(scatter_selection['points'])):
            id = scatter_selection['points'][i]['text'].split(':')[0]
            selected.append(id)
        df = df.loc[df['ID'].isin(selected)]
    return figures.histogram(df)


@app.callback(
    Output('Suspect Table', 'data'),
    [
        Input('signal', 'data'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ])
def update_suspect_table(variable, start_date, end_date):
    df = global_store(variable, start_date, end_date)
    return figures.suspectTable(df)


@app.callback(
    Output('Health Table', 'data'),
    [
        Input('signal', 'data'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ])
def update_health_table(variable, start_date, end_date):
    df = global_store(variable, start_date, end_date)
    return figures.healthTable(df)


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