#TODO: Error handling if no data is available for selected period
#TODO: Auto update after n minutes - Test
#TODO: On refresh only request data which isn't already available, and remove data older than limit
#TODO: Remove 0 values from plates mathcing display graphs
#TODO: Error handling if data isn't available - don't want the app to crash
#TODO: Reference units from something rather than hard coding
#TODO: Could add a slider to maps to show changes over time - need to group and average data by day (https://plotly.com/python/bubble-maps/#reference)

import os
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
from_file = False
local_file_dir = os.getenv('local_file_dir')
day_period = 7
variables = ["PM2.5", "Temperature", "Plates Matching"]
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
    if from_file == False:
        print('fetching data...', variable, datetime.datetime.now())
        url = f"http://uoweb3.ncl.ac.uk/api/v1.1/sensors/data/json/?starttime={start}&endtime={end}&data_variable={variable}"
        response_API = requests.get(url)
        print(variable, 'status code: ', response_API.status_code, url)
        json_data = json.loads(response_API.text)
    elif from_file == True:
        print('fetching data from local file...', variable, datetime.datetime.now())
        json_data = json.load(open(local_file_dir+variable+'.json'))
    df = pd.json_normalize(json_data, record_path=['sensors'])
    df = df[df['data.'+variable].notna()]
    return df

def uo_graph(df, name, color):
    return go.Scatter(x=list(df['Datetime']),
                      y=list(df['Value']),
                      mode='markers',
                      #marker_symbol='circle-open',
                      marker_color=color,
                      opacity=0.4,
                      name=name)

def uo_map(df):
    return [dict(
        type = 'scattermapbox', #'scattergeo',
        locationmode = 'country names',
        lon = df['Sensor Centroid Longitude.0'],
        lat = df['Sensor Centroid Latitude.0'],
        text = df['text'],
        mode = 'markers',
        marker = dict(
            size = df['Value'],
            opacity = 0.8,
            reversescale = False,
            autocolorscale = False,
            symbol = 'circle',
            line = dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            colorscale = "Reds", #Blackbody,Bluered,Blues,Cividis,Earth,Electric,Greens,Greys,Hot,Jet,Picnic,Portland,Rainbow,RdBu,Reds,Viridis,YlGnBu,YlOrRd
            cmin = 0,
            color = df['Value'],
            cmax = df['Value'].max(),
            colorbar=dict(
                title="μgm⁻³"
            )
        ))]

def apply_graph_customisation(df, variable):
    if variable == "PM2.5":
        df = df[df['Value'] <= pm25_display_limit]
        color = '#f44242'
    elif variable == "Temperature":
        df = df[df['Value'] <= temperature_display_limit]
        color = '#4254f5'
    elif variable == 'Plates Matching':
        df = df[df['Value'] != 0]
        color = '#47d65f'
    else:
        color = '#8a8888'
    return df, color

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

def sensor_display_map(variable, df):
    df['text'] = df['Sensor Name']+', '+df['Value'].astype(str)+' μgm⁻³'
    df, color = apply_graph_customisation(df, variable)
    return uo_map(df)

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
        ds_list.append(sensor_df.loc[
                (sensor_df['Timestamp'] == max(sensor_df['Timestamp'])) &
                #(sensor_df['Timestamp'] > (int(time.time())*1000)-(latest_reading_threshold*60000)) &
                (sensor_df['Flagged as Suspect Reading'] == False)])
    ds = pd.concat(ds_list)
    ds = ds.drop('Flagged as Suspect Reading', axis=1)
    return pd.merge(ds, df, how='inner', left_on='Sensor Name', right_on='Sensor Name.0')

def run(variable):
    start, end         = stringtimes(day_period)
    df                 = get_uo_data(variable, start, end)
    sensor_dfs         = uo_sensor_values(variable, df)
    display_graphs     = sensor_display_graphs(variable, sensor_dfs)
    suspect_df         = get_suspect_readings(variable, df)
    latest_readings_df = get_latest_readings(df, sensor_dfs)
    map_display        = sensor_display_map(variable, latest_readings_df)
    dict_all[variable] = {'start': start, 
                          'end': end, 
                          'start_unix': time.time(),
                          'end_unix': time.time(),
                          'dataframe': df, 
                          'display_graphs': display_graphs, 
                          'suspect_dataframe': suspect_df,
                          'latest_readings': latest_readings_df,
                          'map_display': map_display
                          }
    return dict_all

def graph_layout(variable, units):
    return dict(title=f'Newcastle UO {variable}',
        showlegend = False, 
        autosize = True,
        margin = dict(t=60, b=60, l=40, r=40),
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

def map_layout(variable):
    return dict(
        title = f'Newcastle UO {variable} Map',
        colorbar = True,
        autosize = True,
        margin = dict(t=60, b=60, l=40, r=40),
        # geo = dict(
        #     # projection=dict(type='natural earth'),
        #     # showland = True,
        #     # landcolor = "rgb(250, 250, 250)",
        #     # subunitcolor = "rgb(217, 217, 217)",
        #     # countrycolor = "rgb(217, 217, 217)",
        #     # countrywidth = 0.5,
        #     # subunitwidth = 0.5
        # ),
        mapbox = dict(
            style = "carto-positron", # "carto-darkmatter"
            bounds = dict(west=-1.8, east=-1.4, south=54.85, north=55.1)
        )
    )

def update_scheduler(variable):
    # checks whether should update or use previously collected data
    # only allow update if last updated over 2 mins ago (i.e. not at very start)
    if time.time() - dict_all[variable]['end_unix'] > 120 \
    or variable not in dict_all:
        run(variable)

# INITIAL RUN
for v in variables:
    dict_all = run(v)

# APPLICATION
app = dash.Dash(__name__#, 
                #external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
                )

app.layout = html.Div([
    html.Div(
        html.H1('EDIF Live Dashboard'),
        className="banner"
    ),
    # html.Div([
    #     dcc.Input(
    #         id='days-input',
    #         placeholder='Enter number of days to be charted',
    #         type='number',
    #         value=7
    #     ),
    #     html.Button(id="submit-button", 
    #                 n_clicks=0, 
    #                 children="Submit"
    #     )
    # ]),
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
        ], className="four columns"),
        html.Div([
            dcc.Graph(
                id='Graph_2'
            )
        ], className="four columns"),
        html.Div([
            #TODO: Figure out out to center labels
            html.Label('Suspect Readings'),
            dash.dash_table.DataTable(
                id='Suspect_table',
                page_size=12
            )
        ], className="four columns")
    ], className='row'
    ),
    html.Div([
        html.Div([
            dcc.Graph(
                id='map'
            )
        ], className="four columns"),
        html.Div([
            dcc.Graph(
                id='Graph_3'
            )
        ], className="eight columns")
    ], className='row'
    ),
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
    units = '°C'
    update_scheduler(v)
    return dict(data=dict_all[v]['display_graphs'], layout=graph_layout(v, units))

@app.callback(Output('Graph_2', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    v = 'PM2.5'
    units = 'μgm⁻³'
    update_scheduler(v)
    return dict(data=dict_all[v]['display_graphs'], layout=graph_layout(v, units))

@app.callback(Output('Graph_3', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    v = 'Plates Matching'
    units = 'Number of Vehicles'
    update_scheduler(v)
    return dict(data=dict_all[v]['display_graphs'], layout=graph_layout(v, units))

@app.callback(Output('Suspect_table', 'data'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    for v in variables:
        update_scheduler(v)
    l = []
    for v in dict_all:
        l.append(dict_all[v]['suspect_dataframe'])
    sus_df = pd.concat(l)
    sus_df = sus_df.loc[:, ["Sensor Name", "Timestamp", "Variable", "Value", "Units"]]
    return sus_df.to_dict('records')

@app.callback(Output('map', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    v = 'PM2.5'
    update_scheduler(v)
    return dict(data=dict_all[v]['map_display'], layout=map_layout(v))


if __name__ == "__main__":
    app.run_server(debug=True)