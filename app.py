#TODO: Error handling if no data is available for selected period
#TODO: Figure out why data is requested twice (or seems to be at least)
#TODO: Auto update after n minutes

import requests
import json
import dash
from dash.dependencies import Output, Input, State
import pandas as pd
import datetime
import plotly.graph_objs as go
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

load_dotenv()
day_period = 7
variables = ["PM2.5", "Temperature"]
pm25_display_limit = 30
temperature_display_limit = 50
thin_data_by_factor_of = 50
figures = {}

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

def uo_graph(ds, name, color):
    return go.Scatter(x=list(ds['Datetime']),
                      y=list(ds['Value']),
                      mode='markers',
                      marker_symbol='circle-open',
                      marker_color=color,
                      opacity=0.2,
                      name=name)

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

def uo_sensor_values(variable, df, df_list):
    for i, l in enumerate(df['data.'+variable]):
        ds = pd.DataFrame(l)
        ds = ds[ds['Flagged as Suspect Reading'] == False]
        ds, color = apply_graph_customisation(ds, variable)
        ds['Datetime'] = pd.to_datetime(ds['Timestamp'], unit='ms')
        ds = ds.iloc[::thin_data_by_factor_of, :]
        try:
            name = ds['Sensor Name'].iloc[0]
        except:
            name = 'unknown sensor name'
        df_list.append(uo_graph(ds, name, color))
    return df, df_list

def get_suspect_readings(variable, df, suspects=[]):
    #TODO: Make sure table headings are always displayed in same order
    for i, l in enumerate(df['data.'+variable]):
        ds = pd.DataFrame(l)
        ds = ds[ds['Flagged as Suspect Reading'] == True]
        ds = ds.drop('Flagged as Suspect Reading', axis=1)
        suspects.append(ds)
    sus_df = pd.concat(suspects).drop_duplicates().reset_index(drop=True)
    return sus_df

def run(variable):
    df_list = []
    start, end = stringtimes(day_period)
    df = get_uo_data(variable, start, end)
    df, df_list = uo_sensor_values(variable, df, df_list)
    sus_df = get_suspect_readings(variable, df)
    return df_list, sus_df

def layout(variable):
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
                    ), rangeslider=dict(visible=True),
                type="date"
                )
            )

for v in variables:
    df_list, sus_df = run(v)
    figures[v] = dict(data=df_list, layout=layout(v))

app = dash.Dash(__name__, 
                external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"])

app.layout = dash.html.Div([
    dash.html.Div(
        dash.html.H1('EDIF Live Dashboard'),
        className="banner"
    ),
    dash.html.Div([
        dash.dcc.Input(
            id='Graph_3-input',
            placeholder='Enter variable to be charted',
            type='text',
            value='Temperature'),
        dash.html.Button(id="submit-button", n_clicks=0, children="Submit")
    ]),
    # dash.html.Div(
    #     dash.dcc.Dropdown(
    #         options=[
    #             {'label': 'Candlestick', 'value': 'Candlestick'},
    #             {'label': 'Line', 'value': 'Line'}
    #         ]
    #     )
    # ),
    dash.html.Div([
        dash.html.Div([
            dash.dcc.Graph(
                id='Graph_1', 
                figure=figures["Temperature"]
            )
        ], className="six columns"),
        dash.html.Div([
            dash.dcc.Graph(
                id='Graph_2', 
                figure=figures["PM2.5"]
            )
        ], className="six columns"),
        dash.html.Div([
            dash.dcc.Graph(
                id='Graph_3'
            )
        ], className="six columns")
    ], className='row'
    ),
    dash.html.Div([
        dash.html.Div([
            dash.dash_table.DataTable(
                sus_df.to_dict('records'), 
                [{"name": i, "id": i} for i in sus_df.columns],
                id='Suspect_table')
        ], className="six columns")
    ], className='row')
])

# CALLBACKS
@app.callback(Output("Graph_3", "figure"),
             [Input("submit-button", "n_clicks")],
             [State("Graph_3-input", "value")])

def update_fig(n_clicks, input_value):
    if input_value in figures:
        df_list = figures[input_value]["data"]
    else:
        df_list = run(input_value)
    return dict(data=df_list, layout=layout(input_value))

if __name__ == "__main__":
    app.run_server(debug=True)