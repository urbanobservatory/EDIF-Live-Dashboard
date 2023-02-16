import json
import dash
import pandas as pd
from datetime import date, datetime, timedelta
from dash import ctx, CeleryManager
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from flask_caching import Cache
from celery import Celery

import htmlLayout
import figures
import getData
import allValues
import latestValues
import utils

import warnings
warnings.filterwarnings("ignore")


env_vars = json.load(open('/code/env.json'))
update_frequency = int(env_vars['update_frequency'])
day_period = float(env_vars['update_frequency'])


# CONFIGURE CACHE
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': 'redis://edif-cache:6379'}

# celery_app = Celery(
#     __name__, 
#     broker=CACHE_CONFIG['CACHE_REDIS_URL'], 
#     backend=CACHE_CONFIG['CACHE_REDIS_URL'])

# background_callback_manager = CeleryManager(
#     celery_app,
#     cache_by=[])


# APPLICATION
app = dash.Dash(
    __name__,
    # background_callback_manager=background_callback_manager
    )
server = app.server

cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)

app.layout = htmlLayout.layout()


# CACHE MEMOIZE
@cache.memoize()
def day_store(variable, day):
    start, end = utils.get_start_end_time(day)
    df = getData.run(variable, start, end)
    return df

@cache.memoize()
def hour_store(variable, day):
    pass

def cache_controller(variable, start_date, end_date, dfs=[], today=None):
    # Get past n days if no dates selected
    if start_date == None or end_date == None:
        start_date, end_date = utils.get_start_end_date(start_date, end_date)
    
    # Request/get df for each day from cache
    days = utils.get_days(start_date, end_date)

    # If today in days, request fresh data
    if days[-1] == datetime.today().date():
        today = days.pop()
        start, end = utils.get_start_end_time(today)

    for day in days:
        dfs.append(day_store(variable, day))
    if today:
        dfs.append(getData.run(variable, start, end))

    # Concatenate dfs
    return pd.concat(dfs)


# CALLBACKS
@app.callback(
    Output('signal', 'data'), 
    [
        Input('interval-component', 'n_intervals'),
        Input('checklist', 'value'),
        Input('Refresh Button', 'n_clicks')
    ])
def compute_value(intervals, variable, clicks):
    #day_store(variable)
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
    df = cache_controller(variable, start_date, end_date)
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
    df = cache_controller(variable, start_date, end_date)    
    if 'Map' == ctx.triggered_id:
        df = utils.select(df, map_selection)
    return figures.scatter_all(df)


@app.callback(
    Output('Scatter Hover', 'figure'),
    [
        Input('signal', 'data'), 
        Input('Map', 'hoverData'),
        Input('Scatter All', 'hoverData'),
        Input('Scatter3D', 'hoverData'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ])
def update_scatter_hover(variable, map_hover, scatter_hover, scatter3d_hover, start_date, end_date):
    df = cache_controller(variable, start_date, end_date) 
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
        try:
            id = scatter_hover['points'][0]['text'].split(':')[0]
            df = df.loc[df['ID'].isin([id])]
        except:
            raise PreventUpdate
    elif 'Scatter3D' == ctx.triggered_id:
        id = scatter3d_hover['points'][0]['text'].split(':')[0]
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
    df = cache_controller(variable, start_date, end_date) 
    if 'Map' == ctx.triggered_id:
        df = utils.select(df, map_selection)
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
    df = cache_controller(variable, start_date, end_date) 
    if 'Map' == ctx.triggered_id:
        df = utils.select(df, map_selection)
    return figures.indicatorsB(df)


@app.callback(
    Output('Scatter3D', 'figure'),
    [
        Input('signal', 'data'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ])
def update_3Dscatter(variable, start_date, end_date):
    df = cache_controller(variable, start_date, end_date)
    return figures.scatter3D(df)


@app.callback(
    Output('BoxPlot', 'figure'),
    [
        Input('signal', 'data'), 
        Input('Map', 'selectedData'),
        Input('Scatter All', 'selectedData'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ])
def update_boxplot(variable, map_selection, scatter_selection, start_date, end_date):
    df = cache_controller(variable, start_date, end_date)
    if 'Map' == ctx.triggered_id:
        df = utils.select(df, map_selection)
    return figures.boxPlot(df)


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
    df = cache_controller(variable, start_date, end_date)
    if 'Map' == ctx.triggered_id:
        df = utils.select(df, map_selection)
    if 'Scatter All' == ctx.triggered_id:
        df = utils.select(df, scatter_selection)
    return figures.histogram(df)


@app.callback(
    Output('Suspect Table', 'data'),
    [
        Input('signal', 'data'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ])
def update_suspect_table(variable, start_date, end_date):
    df = cache_controller(variable, start_date, end_date)
    return figures.suspectTable(df)


@app.callback(
    Output('Health Table', 'data'),
    [
        Input('signal', 'data'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ])
def update_health_table(variable, start_date, end_date):
    df = cache_controller(variable, start_date, end_date)
    return figures.healthTable(df)



@app.callback(
    Output("modal-centered", "is_open"),
    [Input("Info Button", "n_clicks"), Input("close-centered", "n_clicks")],
    [State("modal-centered", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open
    

# Run App
if __name__ == "__main__":
    app.run_server(debug=True, processes=6, threaded=False, host='0.0.0.0', port=80)