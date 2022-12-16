import os
import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import figures
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
    html.Div(
        dcc.Checklist(
            id='checklist',
            options=[
                'Birmingham',
                'Hull',
                'Manchester',
                'Newcastle',
                'Sheffield'
            ],
            value=[
                'Birmingham',
                'Hull',
                'Manchester',
                'Newcastle',
                'Sheffield'
            ],
            inline=True,
            style={
                'color': '#ccccdc', 
                'font-size': 20,
                'text-align': 'center'
            }
        )
    ),
    html.Div([
        html.Div([
            dcc.Graph(
                id='indicators'
            )
        ], className="four columns"),
        html.Div([
            dcc.Graph(
                id='PM25 Graph'
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
                id='Traffic Flow Graph'
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
@app.callback(
    Output('indicators', 'figure'),
    [Input('interval-component', 'n_intervals'), Input('checklist', 'value')])
def update_graph_live(n, checklist_locations):
    src      = 'UDX'
    variables_a = ['PM2.5', 'Temperature', 'Traffic Flow', 'Black Carbon']
    variable_b = 'Temperature'
    domain_a = {'row': 0, 'column': 0}
    domain_b = {'row': 1, 'column': 0}
    domain_c = {'row': 0, 'column': 1}
    units_b = '°C'
    return figures.indicators(src, checklist_locations, variables_a, variable_b, domain_a, domain_b, domain_c, units_b)


@app.callback(
    Output('PM25 Graph', 'figure'),
    [Input('interval-component', 'n_intervals'), Input('checklist', 'value')])
def update_graph_live(n, checklist_locations):
    src      = 'UDX'
    variable = 'PM2.5'
    units    = 'μgm⁻³'
    return figures.pm25Graph(src, checklist_locations, variable, units)


@app.callback(
    Output('Traffic Flow Graph', 'figure'),
    [Input('interval-component', 'n_intervals'), Input('checklist', 'value')])
def update_graph_live(n, checklist_locations):
    src      = 'UDX'
    variable = 'Traffic Flow'
    units    = 'Number of Vehicles'        
    return figures.trafficFlowGraph(src, checklist_locations, variable, units)


@app.callback(Output('Suspect_table', 'data'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    src       = 'UDX'
    location  = 'Newcastle'
    variables = ['PM2.5', 'Temperature', 'Traffic Flow']
    return figures.suspectTable(src, location, variables)


@app.callback(Output('Alerts_table', 'data'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    src       = 'UDX'
    locations = ['Newcastle', 'Manchester', 'Birmingham']
    variables = ['PM2.5', 'Temperature', 'Traffic Flow', 'Black Carbon']
    return figures.alertsTable(src, locations, variables)


@app.callback(Output('map', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    src      = 'UDX'
    location = 'Newcastle'
    variable = 'PM2.5'
    units    = 'μgm⁻³'
    return figures.map(src, location, variable, units)


if __name__ == "__main__":
    app.run_server(debug=True)