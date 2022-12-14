import os
import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import plotly.graph_objects as go
import pandas as pd
import run
import displayCard
import displayGauge
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
                style_table={
                    'height': '210.6px', 
                    'width': '550px',
                    'overflowY': 'auto'
                    },
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
                style_table={
                    'height': '210.6px', 
                    'width': '550px',
                    'overflowY': 'auto'
                    },
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
    variables_a = ['PM2.5', 'Temperature', 'Traffic Flow']
    variable_b = 'Temperature'
    domain_a = {'row': 0, 'column': 0}
    domain_b = {'row': 0, 'column': 1}
    units_b = '°C'
    fig = go.Figure()

    sensors_online = 0
    for variable_a in variables_a:
        data_a = run.run(src, location, variable_a)
        sensors_online += data_a['sensors_online']
    fig.add_trace(displayCard.run(location, sensors_online, domain_a))

    data_b = run.run(src, location, variable_b)
    display_gauge = displayGauge.run(src, location, variable_b, units_b, data_b['latest_readings'], domain_b)
    fig.add_trace(display_gauge[0])

    layout = layouts.indicators()
    fig.update_layout(
        autosize      = layout['autosize'],
        paper_bgcolor = layout['paper_bgcolor'],
        plot_bgcolor  = layout['plot_bgcolor'],
        font          = layout['font'],
        margin        = layout['margin'],
        grid          = layout['grid'],
        template      = layout['template']
    )
    return fig

@app.callback(Output('Graph_2', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    src      = 'UDX'
    location = 'Newcastle'
    variable = 'PM2.5'
    units    = 'μgm⁻³'
    data = run.run(src, location, variable, units)
    layout = layouts.graph(src, location, variable, units)
    return dict(data=data['display_graphs'], layout=layout)

@app.callback(Output('Graph_3', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    src      = 'UDX'
    location = 'Newcastle'
    variable = 'Traffic Flow'
    units    = 'Number of Vehicles'
    data = run.run(src, location, variable, units)
    layout = layouts.graph(src, location, variable, units)
    return dict(data=data['display_graphs'], layout=layout)

@app.callback(Output('Suspect_table', 'data'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    src       = 'UDX'
    location  = 'Newcastle'
    variables = ['PM2.5', 'Temperature', 'Traffic Flow']
    l = []
    for variable in variables:
        d = run.run(src, location, variable)
        l.append(d['suspect_dataframe'])
    df = pd.concat(l)
    df = df.drop_duplicates(subset=['ID', 'Datetime'], keep='last')
    df = df.loc[:, ["ID", "Datetime", "Variable", "Value", "Units"]]  
    return df.to_dict('records')

@app.callback(Output('Alerts_table', 'data'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    src       = 'UDX'
    locations = ['Newcastle', 'Manchester', 'Birmingham']
    variables = ['PM2.5', 'Temperature', 'Traffic Flow', 'Black Carbon']
    l = []
    for location in locations:
        for variable in variables:
            try:
                d = run.run(src, location, variable)
                if d['status'] == 'Offline':
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
    variable = 'PM2.5'
    units    = 'μgm⁻³'
    data = run.run(src, location, variable, units)
    layout = layouts.map(src, location, variable)
    return dict(data=data['map_display'], layout=layout)


if __name__ == "__main__":
    app.run_server(debug=True)