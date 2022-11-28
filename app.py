import os
import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import pandas as pd
import run
import layouts
import scheduler
from dotenv import load_dotenv

load_dotenv()

location = 'Newcastle'
src = 'UDX' # 'UOFile', 'UO', 'UDX', 'UDXFile'
if src == 'UO' or src == 'UOFile':
    variables = ["PM2.5", "Temperature", "Plates Matching"]
elif src == 'UDX' or src == 'UDXFile':
    variables = ['pm25', 'temperature', 'intensity']
update_frequency = int(os.getenv('update_frequency'))
figures = {}
dict_all = {}

# INITIAL RUN
for v in variables:
    if src == 'UO' or src == 'UOFile': run.uo(v, dict_all, src)
    elif src == 'UDX' or src == 'UDXFile': run.udx(v, dict_all, src)
    

# APPLICATION
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(
        html.H1('EDIF Interactive Live Dashboard'),
        className="banner"
    ),
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
            #TODO: Figure out to center labels
            html.Label('Suspect Reading Logs'),
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

@app.callback(Output('Graph_1', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    if src == 'UO' or src == 'UOFile': v = 'Temperature'
    elif src == 'UDX' or src == 'UDXFile': v = 'temperature'
    units = '°C'
    scheduler.update(v, dict_all, src)
    # return dict(data=dict_all[v]['display_graphs'], layout=layouts.graph(v, units, src, location))
    return dict(data=dict_all[v]['display_gauge'], layout=layouts.gauge(v, src, location))

@app.callback(Output('Graph_2', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    if src == 'UO' or src == 'UOFile': v = 'PM2.5'
    elif src == 'UDX' or src == 'UDXFile': v = 'pm25'
    units = 'μgm⁻³'
    scheduler.update(v, dict_all, src)
    return dict(data=dict_all[v]['display_graphs'], layout=layouts.graph(v, units, src, location))

@app.callback(Output('Graph_3', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    if src == 'UO' or src == 'UOFile': v = 'Plates Matching'
    elif src == 'UDX' or src == 'UDXFile': v = 'intensity'
    units = 'Number of Vehicles'
    scheduler.update(v, dict_all, src)
    return dict(data=dict_all[v]['display_graphs'], layout=layouts.graph(v, units, src, location))

@app.callback(Output('Suspect_table', 'data'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    for v in variables:
        scheduler.update(v, dict_all, src)
    l = []
    for v in dict_all:
        l.append(dict_all[v]['suspect_dataframe'])
    sus_df = pd.concat(l)
    if src == 'UO' or src == 'UOFile':
        sus_df = sus_df.loc[:, ["Sensor Name", "Timestamp", "Variable", "Value", "Units"]]
    elif src == 'UDX' or src == 'UDXFile':
        sus_df = sus_df.loc[:, ["id", "dateObserved.value", "Variable", "pm25.value", "pm25.unit"]]
    return sus_df.to_dict('records')

@app.callback(Output('map', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    if src == 'UO' or src == 'UOFile': v = 'PM2.5'
    elif src == 'UDX' or src == 'UDXFile': v = 'pm25'
    scheduler.update(v, dict_all, src)
    return dict(data=dict_all[v]['map_display'], layout=layouts.map(v, src, location))


if __name__ == "__main__":
    app.run_server(debug=True)