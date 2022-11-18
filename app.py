#TODO: Error handling if no data is available for selected period
#TODO: Figure out a way of only updating streams once every n minutes, rather than updating every graph with a new request
#TODO: Auto update after n minutes - Test
#TODO: On refresh only request data which isn't already available, and remove data older than limit

import requests
import json
import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import pandas as pd
import time
import datetime
import plotly.graph_objs as go
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

load_dotenv()
day_period = 7
variables = ["PM2.5", "Temperature"]
pm25_display_limit = 100
temperature_display_limit = 50
thin_data_by_factor_of = 50
update_frequency = 5 #minutes
latest_reading_threshold = 60 #minutes
figures = {}
dict_all = {}

def stringtimes(day_period):
    start_datetime = datetime.datetime.now()-relativedelta(days=day_period)
    end_datetime = datetime.datetime.now()
    start = start_datetime.strftime("%Y%m%d%H%M%S")
    end   = end_datetime.strftime("%Y%m%d%H%M%S")
    return start, end

def get_uo_data(variable, start, end):
    url = f"http://uoweb3.ncl.ac.uk/api/v1.1/sensors/data/json/?starttime={start}&endtime={end}&data_variable={variable}"
    response_API = requests.get(url)
    print(variable, 'status code: ', response_API.status_code, url)
    json_data = json.loads(response_API.text)
    df = pd.json_normalize(json_data, record_path=['sensors'])
    df = df[df['data.'+variable].notna()]
    return df

def uo_graph(df, name, color):
    return go.Scatter(x=list(df['Datetime']),
                      y=list(df['Value']),
                      mode='markers',
                      marker_symbol='circle-open',
                      marker_color=color,
                      opacity=0.2,
                      name=name)

# def uo_map(df):
#     #TODO: May need to iterate through dataframe?
#     return go.Scattergeo(#dict(data_frame=df['Value'], ),
#                          lat=df['Sensor Centroid Latitude.0'],
#                          lon=df['Sensor Centroid Longitude.0'],
#                          #text=df['Sensor Name'],
#                          projection='natural earth')

def apply_graph_customisation(ds, variable):
    if variable == "PM2.5":
        ds = ds[ds['Value'] <= pm25_display_limit]
        color = '#f44242'
    elif variable == "Temperature":
        ds = ds[ds['Value'] <= temperature_display_limit]
        color = '#4254f5'
    else:
        color = '#8a8888'
    return ds, color

def uo_sensor_values(variable, df):
    sensor_dfs=[]
    for i, l in enumerate(df['data.'+variable]):
        ds = pd.DataFrame(l)
        sensor_dfs.append(ds)
    return sensor_dfs

def sensor_display_graphs(variable, sensor_dfs):
    display_graphs=[]
    for ds in sensor_dfs:
        ds = ds[ds['Flagged as Suspect Reading'] == False]
        ds, color = apply_graph_customisation(ds, variable)
        ds['Datetime'] = pd.to_datetime(ds['Timestamp'], unit='ms')
        ds = ds.iloc[::thin_data_by_factor_of, :]
        try:
            name = ds['Sensor Name'].iloc[0]
        except:
            name = 'unknown sensor name'
        display_graphs.append(uo_graph(ds, name, color))
    return display_graphs

# def display_maps(df):
#     return list(uo_map(df))

def get_suspect_readings(variable, df):
    suspects = []
    for i, l in enumerate(df['data.'+variable]):
        ds = pd.DataFrame(l)
        ds = ds[ds['Flagged as Suspect Reading'] == True]
        ds = ds.drop('Flagged as Suspect Reading', axis=1)
        suspects.append(ds)
    suspect_df = pd.concat(suspects).drop_duplicates().reset_index(drop=True)
    return suspect_df

def get_latest_readings(df, sensor_dfs):
    ds_list = []
    for sensor_df in sensor_dfs:
        ds_list.append(
            sensor_df.loc[
                (sensor_df['Timestamp'] == max(sensor_df['Timestamp'])) &
                (sensor_df['Timestamp'] > (int(time.time())*1000)-(latest_reading_threshold*60000)) &
                (sensor_df['Flagged as Suspect Reading'] == False)
            ]
        )
    ds = pd.concat(ds_list)
    ds = ds.drop('Flagged as Suspect Reading', axis=1)
    return pd.merge(ds, df, how='inner', left_on='Sensor Name', right_on='Sensor Name.0')

def run(variable):
    print('fetching data...', variable, datetime.datetime.now())
    start, end         = stringtimes(day_period)
    df                 = get_uo_data(variable, start, end)
    sensor_dfs         = uo_sensor_values(variable, df)
    display_graphs     = sensor_display_graphs(variable, sensor_dfs)
    suspect_df         = get_suspect_readings(variable, df)
    latest_readings_df = get_latest_readings(df, sensor_dfs)
    # map_display        = display_maps(latest_readings_df)
    dict_all[variable] = {'start': start, 
                          'end': end, 
                          'start_unix': time.time(),
                          'end_unix': time.time(),
                          'dataframe': df, 
                          'display_graphs': display_graphs, 
                          'suspect_dataframe': suspect_df,
                          'latest_readings': latest_readings_df#,
                          #'map_display': map_display
                          }
    return dict_all

def graph_layout(variable):
    return dict(title=f'Newcastle UO {variable}', 
                showlegend=False, 
                autosize = False,
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
                )
            )

def update_scheduler(variable):
    # checks whether should update or use previously collected datas
    # only allow update if last updated over 1 min ago (i.e. not at very start)
    if time.time() - dict_all[variable]['end_unix'] > 60 \
    or variable not in dict_all:
        run(variable)

# INITIAL RUN
for v in variables:
    dict_all = run(v)

# APPLICATION
app = dash.Dash(__name__, 
                external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])

app.layout = html.Div([
    html.Div(
        html.H1('EDIF Live Dashboard'),
        className="banner"
    ),
    html.Div([
        dcc.Input(
            id='days-input',
            placeholder='Enter number of days to be charted',
            type='number',
            value=7
        ),
        html.Button(id="submit-button", 
                    n_clicks=0, 
                    children="Submit"
        )
    ]),
    # html.Div(
    #     dcc.Dropdown(
    #         options=[
    #             {'label': 'Candlestick', 'value': 'Candlestick'},
    #             {'label': 'Line', 'value': 'Line'}
    #         ]
    #     )
    # ),
    html.Div([
        html.Div([
            dcc.Graph(
                id='Graph_1'
            )
        ], className="six columns"),
        html.Div([
            dcc.Graph(
                id='Graph_2'
            )
        ], className="six columns")#,
        # html.Div([
        #     dcc.Graph(
        #         id='Graph_3'
        #     )
        # ], className="six columns")
    ], className='row'
    ),
    html.Div([
        html.Div([
            #TODO: Figure out out to center labels
            html.Label('Suspect Readings'),
            dash.dash_table.DataTable(
                id='Suspect_table',
                page_size=10
            )
        ], className="six columns")
    ], className='row'
    ),
    # html.Div([
    #     dcc.Graph(
    #         id='map'
    #     )
    # ]),
    dcc.Interval(
        id='interval-component',
        interval=60000*update_frequency,
        n_intervals=0
    )
])

# CALLBACKS
# @app.callback(Output("Graph_3", "figure"),
#              [Input("submit-button", "n_clicks")],
#              [State("Graph_3-input", "value")])
# def update_fig(n_clicks, input_value):
#     if input_value in figures:
#         sensor_dfs = figures[input_value]["data"]
#     else:
#         sensor_dfs, sus_df = run(input_value)
#     return dict(data=sensor_dfs, layout=layout(input_value))

#TODO: Figure out how to update entire page with a single callback
@app.callback(Output('Graph_1', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    v = 'Temperature'
    update_scheduler(v)
    return dict(data=dict_all[v]['display_graphs'], layout=graph_layout(v))

@app.callback(Output('Graph_2', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    v = 'PM2.5'
    update_scheduler(v)
    return dict(data=dict_all[v]['display_graphs'], layout=graph_layout(v))

@app.callback(Output('Suspect_table', 'data'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    for v in dict_all:
        update_scheduler(v)
    l = []
    for v in dict_all:
        l.append(dict_all[v]['suspect_dataframe'])
    sus_df = pd.concat(l)
    sus_df = sus_df.loc[:, ["Sensor Name", "Timestamp", "Variable", "Value", "Units"]]
    return sus_df.to_dict('records')

# @app.callback(Output('map', 'figure'),
#               Input('interval-component', 'n_intervals'))
# def update_graph_live(n):
#     #run('Temperature')
#     run('PM2.5')
#     map = dict_all['PM2.5']['map_display']
#     return dict(data=map)


if __name__ == "__main__":
    app.run_server(debug=True)