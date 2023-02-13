import json
import dash
import pandas as pd
from datetime import date, datetime, timedelta
from dash import dcc, html, ctx
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dateutil.relativedelta import relativedelta
from flask_caching import Cache

import htmlLayout
import figures
import getData
import allValues
import latestValues


env_vars = json.load(open('/code/env.json'))

update_frequency = int(env_vars['update_frequency'])
day_period = float(env_vars['update_frequency'])

# APPLICATION
app = dash.Dash(__name__)
server = app.server

CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL':  'redis://edif-cache:6379'
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)


# def get_days(start_date, end_date):
#     print('start_date', start_date, type(start_date))
#     print('end_date', end_date, type(end_date))

#     days = []

#     start_date = date(
#         int(start_date.split('-')[0]),
#         int(start_date.split('-')[1]),
#         int(start_date.split('-')[2]))
#     end_date = date(
#         int(end_date.split('-')[0]),
#         int(end_date.split('-')[1]),
#         int(end_date.split('-')[2]))

#     delta = end_date - start_date

#     for i in range(delta.days + 1):
#         day = start_date + timedelta(days=i)
#         days.append(day)

#     return days

def hourly_averages(df, hours):
    averages = []
    for h in range(0, len(hours)-1):
        start = hours[h]
        end = hours[h+1]
        mask = (df['Datetime'] > start) & (df['Datetime'] <= end)
        df2 = df.loc[mask]
        averages.append(df2['Value'].mean())
    return averages

def select(df, item_selection):
    selected = []
    for i in range(0, len(item_selection['points'])):
        id = item_selection['points'][i]['text'].split(':')[0]
        selected.append(id)
    return df.loc[df['ID'].isin(selected)]

app.layout = htmlLayout.layout()


# CALLBACKS
@cache.memoize()
def day_store(variable, start_date=None, end_date=None):

    # start = datetime.strptime(day, '%Y-%m-%d')
    # end = datetime.strptime(day, '%Y-%m-%d') + timedelta(hours=23, minutes=59, seconds=59)

    # if start_date != None and end_date == None \
    # or start_date == None and end_date != None:
    #     raise PreventUpdate

    # elif start_date != None and end_date != None:        
    #     start = datetime.strptime(start_date, '%Y-%m-%d')
    #     end = datetime.strptime(end_date, '%Y-%m-%d') 
    #     end = end + timedelta(hours=23, minutes=59, seconds=59)
    #     print('start', start)
    #     print('end', end)

    if start_date != None and end_date != None:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        start = datetime.now()-relativedelta(days=day_period)
        end   = datetime.now()

    df = getData.run(variable, start, end)

    return df


@cache.memoize()
def hour_store(variable, day):
    pass


@app.callback(
    Output('signal', 'data'), 
    [
        Input('interval-component', 'n_intervals'),
        Input('checklist', 'value'),
        Input('Refresh Button', 'n_clicks')
    ])
def compute_value(intervals, variable, clicks):
    day_store(variable)
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
    df = day_store(variable, start_date, end_date)
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
    df = day_store(variable, start_date, end_date)
    if 'Map' == ctx.triggered_id:
        df = select(df, map_selection)

    # else:
    #     dfs = []

    #     if 'date-picker-range' == ctx.triggered_id:
    #         print('start_date', start_date, type(start_date))
    #         print('end_date', end_date, type(end_date))
    #         days = get_days(start_date, end_date)

    #     else:
    #         start_date = datetime.today()-relativedelta(days=day_period)
    #         start_date = start_date.strftime('%Y-%m-%d')
    #         end_date = datetime.today().strftime('%Y-%m-%d')
    #         # print('start_date', start_date, type(start_date))
    #         # print('end_date', end_date, type(end_date))
    #         # start_date = start_date.strftime('%Y-%m-%d')
            
    #         days = get_days(start_date, end_date)

    #     for day in days:
    #         dfs.append(day_store(variable, day))
    #     df = pd.concat(dfs)

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
    df = day_store(variable, start_date, end_date)
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
    df = day_store(variable, start_date, end_date)
    if 'Map' == ctx.triggered_id:
        df = select(df, map_selection)
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
    df = day_store(variable, start_date, end_date)
    if 'Map' == ctx.triggered_id:
        df = select(df, map_selection)
    return figures.indicatorsB(df)


# @app.callback(
#     Output('Scatter3D', 'figure'),
#     [
#         Input('signal', 'data'),
#         Input('date-picker-range', 'start_date'),
#         Input('date-picker-range', 'end_date')
#     ])
# def update_3Dsurface(variable, start_date, end_date):
#     if start_date == None and end_date == None:
#         start_date = datetime.now()-relativedelta(days=day_period)
#         end_date   = datetime.now()
#         start_date = start_date.strftime("%Y-%m-%d")
#         end_date = end_date.strftime("%Y-%m-%d")

#     df1 = day_store(variable, start_date, end_date)
#     df2 = day_store('Traffic Flow', start_date, end_date)

#     period = pd.date_range(start_date, end_date, freq='D')
#     variable_averages = hourly_averages(df1, period)
#     traffic_averages = hourly_averages(df2, period)

#     period = period.delete(len(period)-1)
#     period = [str(x) for x in period]

#     df = pd.DataFrame({
#         'Period': period,
#         'Variable_values': variable_averages,
#         'Traffic_Flow_values': traffic_averages
#         })
#     df = df.fillna(0)

#     return figures.scatter3D(df)


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
    df = day_store(variable, start_date, end_date)
    if 'Map' == ctx.triggered_id:
        df = select(df, map_selection)
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
    df = day_store(variable, start_date, end_date)
    if 'Map' == ctx.triggered_id:
        df = select(df, map_selection)
    if 'Scatter All' == ctx.triggered_id:
        df = select(df, scatter_selection)
    return figures.histogram(df)


@app.callback(
    Output('Suspect Table', 'data'),
    [
        Input('signal', 'data'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ])
def update_suspect_table(variable, start_date, end_date):
    df = day_store(variable, start_date, end_date)
    return figures.suspectTable(df)


@app.callback(
    Output('Health Table', 'data'),
    [
        Input('signal', 'data'),
        Input('date-picker-range', 'start_date'),
        Input('date-picker-range', 'end_date')
    ])
def update_health_table(variable, start_date, end_date):
    df = day_store(variable, start_date, end_date)
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
    app.run_server(debug=False, processes=6, threaded=False, host='0.0.0.0', port=80)