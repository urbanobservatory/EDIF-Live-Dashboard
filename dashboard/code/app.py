import json
import dash
import pandas as pd
from datetime import datetime
from dash import ctx
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import os

import htmlLayout
import figures
from dash_data import getData
import allValues
import latestValues
import utils

import warnings
warnings.filterwarnings("ignore")

env_vars = json.load(open('/code/env.json'))
update_frequency = int(env_vars['update_frequency'])
day_period = float(env_vars['update_frequency'])
cache_path = '/cached/'


# APPLICATION
app = dash.Dash(__name__)
server = app.server
app.layout = htmlLayout.layout()

# CACHE
def cache_controller(variable, start_date, end_date, today=None, refresh=False):
    # Get past n days if no dates selected
    if (start_date == None or end_date == None) \
    or refresh:
        start_date, end_date = utils.get_start_end_date(start_date, end_date)
    
    # Request/get df for each day from cache
    days = utils.get_days(start_date, end_date)

    # If today in days, request fresh data
    if days[-1] == datetime.today().date():
        today = days.pop()
        start_time, end_time = utils.get_start_end_time(today)

    # Append to dfs
    dfs = []
    for day in days:
        start, end = utils.get_start_end_time(day)
        day_path = f'{cache_path}{variable}-{day}.csv'
        if os.path.exists(day_path):
            print('USER - ALREADY STORED', day_path, flush=True)
            dfs.append(pd.read_csv(day_path, index_col=False))
        else:
            print('USER - RUNNING', variable, day_path, flush=True)
            df = getData.pull_data(variable, start, end)
            if df is not None:
                dfs.append(df)
                df.to_csv(day_path)

    # if today:
    #     dfs.append(getData.run(variable, start_time, end_time))

    # Concatenate dfs
    if len(dfs) > 0:
        df = pd.concat(dfs)
        df.sort_values(by='Datetime', inplace=True)
        df['ID'] = df['ID'].astype(str)
        return df


# CALLBACKS
@app.callback(
    Output('signal', 'data'), 
    [
        Input('interval-component', 'n_intervals'),
        Input('checklist', 'value'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date'),
        Input('Refresh Button', 'n_clicks')
    ])
def compute_value(intervals, variable, start_date, end_date, clicks):
    if 'Refresh Button' == ctx.triggered_id:
        data = cache_controller(variable, start_date, end_date, refresh=True)
    else:
        data = cache_controller(variable, start_date, end_date)
    data.reset_index(inplace=True)
    data = data.to_json(orient='split')
    return data


@app.callback(
    Output('Map', 'figure'),
    [
        Input('signal', 'data'),
        Input('Map', 'selectedData')
        # Input('Map', 'relayoutData')
    ])
def update_map(data, map_selection): #, map_relayout):
    df = pd.read_json(data, orient='split')
    sensor_dfs = allValues.run(df)
    latest_df = latestValues.run(sensor_dfs)
    return figures.map(latest_df, map_selection) #, map_relayout)


@app.callback(
    Output('Scatter All', 'figure'),
    [
        Input('signal', 'data'),
        Input('Map', 'selectedData')
    ])
def update_scatter_all(data, map_selection):
    df = pd.read_json(data, orient='split')
    if 'Map' == ctx.triggered_id:
        df = utils.select(df, map_selection)
    return figures.scatter_all(df)


@app.callback(
    Output('Scatter Hover', 'figure'),
    [
        Input('signal', 'data'), 
        Input('Map', 'hoverData'),
        Input('Scatter All', 'hoverData'),
        Input('Scatter3D', 'hoverData')
    ])
def update_scatter_hover(data, map_hover, scatter_hover, scatter3d_hover):
    df = pd.read_json(data, orient='split')
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
    elif 'Scatter3D' == ctx.triggered_id:
        id = scatter3d_hover['points'][0]['text'].split(':')[0]
        df = df.loc[df['ID'].isin([id])]
    return figures.scatter_hover(df)


@app.callback(
    Output('Indicators A', 'figure'),
    [
        Input('signal', 'data'), 
        Input('Map', 'selectedData')
    ])
def update_indicators(data, map_selection):
    df = pd.read_json(data, orient='split')
    if 'Map' == ctx.triggered_id:
        df = utils.select(df, map_selection)
    return figures.indicatorsA(df)


@app.callback(
    Output('Indicators B', 'figure'),
    [
        Input('signal', 'data'), 
        Input('Map', 'selectedData')
    ])
def update_indicators(data, map_selection):
    df = pd.read_json(data, orient='split')
    if 'Map' == ctx.triggered_id:
        df = utils.select(df, map_selection)
    return figures.indicatorsB(df)


@app.callback(
    Output('Scatter3D', 'figure'),
    [
        Input('signal', 'data'),
        Input('Map', 'selectedData')
    ])
def update_3Dscatter(data, map_selection):
    df = pd.read_json(data, orient='split')
    if 'Map' == ctx.triggered_id:
        df = utils.select(df, map_selection)
    return figures.scatter3D(df)


@app.callback(
    Output('BoxPlot', 'figure'),
    [
        Input('signal', 'data'), 
        Input('Map', 'selectedData'),
        Input('Scatter All', 'selectedData')
    ])
def update_boxplot(data, map_selection, scatter_selection):
    df = pd.read_json(data, orient='split')
    if 'Map' == ctx.triggered_id:
        df = utils.select(df, map_selection)
    return figures.boxPlot(df)


@app.callback(
    Output('Histogram', 'figure'),
    [
        Input('signal', 'data'), 
        Input('Map', 'selectedData'),
        Input('Scatter All', 'selectedData')
    ])
def update_histogram(data, map_selection, scatter_selection):
    df = pd.read_json(data, orient='split')
    if 'Map' == ctx.triggered_id:
        df = utils.select(df, map_selection)
    if 'Scatter All' == ctx.triggered_id:
        df = utils.select(df, scatter_selection)
    return figures.histogram(df)


@app.callback(
    Output('Suspect Table', 'data'),
    [
        Input('signal', 'data')
    ])
def update_suspect_table(data):
    df = pd.read_json(data, orient='split')
    return figures.suspectTable(df)


@app.callback(
    Output('Health Table', 'data'),
    [
        Input('signal', 'data')
    ])
def update_health_table(data):
    df = pd.read_json(data, orient='split')
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