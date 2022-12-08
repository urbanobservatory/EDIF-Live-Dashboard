import os
import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import pandas as pd
import run
import layouts
from dotenv import load_dotenv

load_dotenv()
update_frequency = int(os.getenv('update_frequency'))
    

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
                style_table={'height': '210.6px', 
                             'width': '550px',
                             'overflowY': 'auto'},
                style_as_list_view=True,
                style_cell=dict(backgroundColor='#111217'),
                style_header=dict(backgroundColor='#181b1f',
                                  fontWeight='bold',
                                  color='#ccccdc'),
                style_data=dict(color="#ccccdc")
            ),
            dash.dash_table.DataTable(
                id='Alerts_table',
                page_size=12,
                style_table={'height': '210.6px', 
                             'width': '550px',
                             'overflowY': 'auto'},
                style_as_list_view=True,
                style_cell=dict(backgroundColor='#111217', textAlign='center'),
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
        ], className="eight columns"),
    ], className='row'
    ),
    dcc.Interval(
        id='interval-component',
        interval=60000*update_frequency,
        n_intervals=0
    ),
    html.Div([
        html.Div(
            html.Img(src="/assets/DfT_logo_60.png"),
            className='img'            
        ),
        html.Div(
            html.Img(src="/assets/ATI_logo_60.png"),
            className='img'            
        ),
        html.Div(
            html.Img(src="/assets/UDX_logo_60.png"),
            className='img'            
        ),
        html.Div(
            html.Img(src="/assets/UO_logo_60.png"),
            className='img'
        ),
        html.Div(
            html.Img(src="/assets/Man_UO_logo_60.png"),
            className='img'
        ),
        html.Div(
            html.Img(src="/assets/Birm_UO_logo_60.png"),
            className='img'
        )
    ], className="footer"
    )
], className="body")


# CALLBACKS
@app.callback(Output('Graph_1', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    src      = 'UDX'
    location = 'Newcastle'
    variable = 'temperature'
    units    = '°C'
    data = run.udx(src, location, variable, units)
    layout = layouts.gauge(src, variable, location)
    return dict(data=data['display_gauge'], layout=layout)

@app.callback(Output('Graph_2', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    src      = 'UDX'
    location = 'Newcastle'
    variable = 'pm25'
    units    = 'μgm⁻³'
    data = run.udx(src, location, variable, units)
    layout = layouts.graph(src, location, variable, units)
    return dict(data=data['display_graphs'], layout=layout)

@app.callback(Output('Graph_3', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    src      = 'UDX'
    location = 'Newcastle'
    variable = 'intensity'
    units    = 'Number of Vehicles'
    data = run.udx(src, location, variable, units)
    layout = layouts.graph(src, location, variable, units)
    return dict(data=data['display_graphs'], layout=layout)

@app.callback(Output('Suspect_table', 'data'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    src       = 'UDX'
    location  = 'Newcastle'
    variables = ['pm25', 'temperature', 'intensity']
    l = []
    for variable in variables:
        data = run.udx(src, location, variable)
        l.append(data['suspect_dataframe'])
    df = pd.concat(l)
    print(df)
    df = df.loc[:, ["ID", "Datetime", "Variable", "Value", "Units"]]
    return df.to_dict('records')

@app.callback(Output('Alerts_table', 'data'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    src       = 'UDX'
    locations = ['Newcastle', 'Manchester', 'Birmingham']
    variables = ['pm25', 'temperature', 'intensity', 'bc']
    l = []
    for location in locations:
        for variable in variables:
            try:
                data = run.udx(src, location, variable)
                if data['status'] == 'Offline':
                    l.append(f'{location} {variable} Stream is Offline')
            except:
                continue
    if len(l) == 0:
        l.append('No Alerts')
    df = pd.DataFrame({'Alerts':l})
    return df.to_dict('records')

@app.callback(Output('map', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    src      = 'UDX'
    location = 'Newcastle'
    variable = 'pm25'
    units    = 'μgm⁻³'
    data = run.udx(src, location, variable, units)
    layout = layouts.map(src, location, variable)
    return dict(data=data['map_display'], layout=layout)


if __name__ == "__main__":
    app.run_server(debug=True)