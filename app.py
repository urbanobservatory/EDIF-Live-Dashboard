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

l = 'Newcastle'
src = 'UDX' # 'UOFile', 'UO', 'UDX', 'UDXFile'
if src == 'UO' or src == 'UOFile':
    variables = ["PM2.5", "Temperature", "Plates Matching"]
elif src == 'UDX' or src == 'UDXFile':
    variables = ['pm25', 'temperature', 'intensity']
update_frequency = int(os.getenv('update_frequency'))

locations = {
                'Newcastle': {
                    'Variables': {
                        'PM2.5': 'pm25', 
                        'Temperature': 'temperature', 
                        'Traffic Flow': 'intensity'
                    }
                },
                'Manchester': {
                    'Variables': {
                        'PM2.5': 'pm25', 
                        'Traffic Flow': 'intensity',
                        'Black Carbon': 'bc'
                    }
                },
                'Birmingham': {
                    'Variables': {
                        'PM2.5': 'pm25'
                    }
                }
            }

# INITIAL RUN
run.udx(locations, src)
    

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
            html.Label(
                children=[
                    html.Span('Suspect Reading Logs', className='labels')
                ]
            ),
            #TODO: Create layout for datatable
            dash.dash_table.DataTable(
                id='Suspect_table',
                page_size=12,
                style_table={'height': '421.2px', 
                             'width': '550px',
                             'overflowY': 'auto'},
                style_as_list_view=True,
                style_cell=dict(backgroundColor='#111217'),
                style_header=dict(backgroundColor='#181b1f',
                                  fontWeight='bold',
                                  color='#ccccdc'),
                style_data=dict(color="#ccccdc")
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
], className="body")

# CALLBACKS

@app.callback(Output('Graph_1', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    if src == 'UO' or src == 'UOFile': v = 'Temperature'
    elif src == 'UDX' or src == 'UDXFile': v = 'temperature'
    units = '°C'
    scheduler.update(v, l, locations, src)
    # return dict(data=dict_all[v]['display_graphs'], layout=layouts.graph(v, units, src, location))
    return dict(data=locations[l][v]['display_gauge'], layout=layouts.gauge(v, src, l))

@app.callback(Output('Graph_2', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    if src == 'UO' or src == 'UOFile': v = 'PM2.5'
    elif src == 'UDX' or src == 'UDXFile': v = 'pm25'
    units = 'μgm⁻³'
    scheduler.update(v, l, locations, src)
    return dict(data=locations[l][v]['display_graphs'], layout=layouts.graph(v, units, src, l))

@app.callback(Output('Graph_3', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    if src == 'UO' or src == 'UOFile': v = 'Plates Matching'
    elif src == 'UDX' or src == 'UDXFile': v = 'intensity'
    units = 'Number of Vehicles'
    scheduler.update(v, l, locations, src)
    return dict(data=locations[l][v]['display_graphs'], layout=layouts.graph(v, units, src, l))

@app.callback(Output('Suspect_table', 'data'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    # for v in variables:
    # scheduler.update(v, l, locations, src)
    i = []
    for v in locations[l]:
        if v != 'Variables':
            i.append(locations[l][v]['suspect_dataframe'])
    sus_df = pd.concat(i)
    if src == 'UO' or src == 'UOFile':
        sus_df = sus_df.loc[:, ["Sensor Name", "Timestamp", "Variable", "Value", "Units"]]
    elif src == 'UDX' or src == 'UDXFile':
        sus_df = sus_df.loc[:, ["id", "dateObserved.value", "Variable", "Value", "Units"]]
    return sus_df.to_dict('records')

@app.callback(Output('map', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    if src == 'UO' or src == 'UOFile': v = 'PM2.5'
    elif src == 'UDX' or src == 'UDXFile': v = 'pm25'
    scheduler.update(v, l, locations, src)
    return dict(data=locations[l][v]['map_display'], layout=layouts.map(v, src, l))


if __name__ == "__main__":
    app.run_server(debug=True)