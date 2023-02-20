import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import json

env_vars = json.load(open('/code/env.json'))

update_frequency = int(env_vars['update_frequency'])
day_period = float(env_vars['update_frequency'])

def layout():
    return html.Div([
        html.Div([
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Information")),
                dbc.ModalBody("Info coming soon. Please report any bugs to daniel.bell2@ncl.ac.uk"),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close",
                        id="close-centered",
                        className="ms-auto",
                        n_clicks=0
                    )
                ),
            ],
            id="modal-centered",
            centered=True,
            is_open=False
            )
        ], className='modal'),

        html.Div([
            html.Div([
                html.Img(
                    id='DTlogo',
                    src='/assets/thumbnail_image006_inverted_201x100.png')
            ], className='logo'),
            html.Div([
                html.H1('Live Dashboard Demo')
            ], className="title"),
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='checklist',
                        options=[
                            'PM1',
                            'PM2.5',
                            'PM4',
                            'PM10',
                            'Traffic Flow',
                            'Black Carbon',
                            'Nitric Oxide',
                            'Ozone',
                            'Nitrogen Dioxide',
                            'Sulfur Dioxide',
                            'Temperature',
                            'Humidity',
                            'Pressure'
                        ],
                        value='Temperature',
                        clearable=False)
                ], className='dropDown')
            ], className='dropDownBox'),
            html.Div([
                html.Div([
                    dcc.DatePickerRange(
                        id='date-picker-range',
                        month_format='Do-MMM-Y')
                ], className='calendar')
            ], className='calendarBox'),
            html.Div([
                html.Div([
                    html.Button(
                        'Refresh',
                        id='Refresh Button',
                        n_clicks = 0)
                ], className='refresh')
            ], className='refreshBox'),
            html.Div([
                html.Div([
                    html.Button(
                        'Info',
                        id='Info Button',
                        n_clicks = 0)
                ], className='refresh')
            ], className='refreshBox')
        ], className='banner'),

        html.Br(),
        
        html.Div([
            html.Div([
                html.Div([
                    dcc.Loading([

                        html.Div([
                            html.Div([
                                html.Div([
                                    dcc.Graph(id='Indicators A')
                                ], className='twelve columns')
                            ])
                        ], className="row"),

                        html.Div([
                            html.Div([
                                html.Div([
                                    dcc.Graph(id='Indicators B')
                                ], className='twelve columns')
                            ])
                        ], className="row")

                    ])
                ], className='graph'),

                html.Br(),
                html.Div([

                    html.Div([
                        html.Div([
                            dcc.Loading(
                                dcc.Graph(id='Scatter All')
                            )
                        ], className='graph')
                    ], className='eight columns'),

                    html.Div([
                        html.Div([
                            dcc.Loading(
                                dcc.Graph(id='BoxPlot')
                            )
                        ], className='boxplot')
                    ], className='four columns')

                ], className="row"),

                html.Br(),

                html.Div([

                    html.Div([
                        html.Div([
                            dcc.Loading(
                                dcc.Graph(id='Scatter3D')
                            )
                        ], className='scatter3d')
                    ], className='six columns'),

                    html.Div([

                        html.Div([
                            dcc.Loading(
                                dcc.Graph(id='Scatter Hover')
                            )
                        ], className='hover'),

                        html.Br(),

                        html.Div([
                            dcc.Loading(
                                dcc.Graph(id='Histogram')
                            )
                        ], className='histogram')

                    ], className='six columns')

                ], className='row'),

            ], className="eight columns"),

            html.Div([
                html.Div([

                    html.Div([
                        html.Div([
                            dcc.Loading(
                                dcc.Graph(id='Map')
                            )
                        ], className='map')
                    ], className='twelve columns')
                    
                ], className='row')
            ], className='four columns')
        ], className="row"),
        
        html.Div([
            html.Div([
            ], className='divider')
        ], className='row'),

        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        dcc.Loading([
                            html.Label(
                                children=[
                                    html.Span('Stream Health', className='labels')
                                ]
                            ),
                            dash.dash_table.DataTable(
                                id = 'Health Table',
                                page_size = 12,
                                style_table = {
                                    'overflowY': 'auto'},
                                style_as_list_view = True,
                                style_cell = {
                                    'backgroundColor': '#111217', 
                                    'textAlign': 'center'},
                                style_header = {
                                    'backgroundColor': '#181b1f',
                                    'fontWeight': 'bold',
                                    'color': '#ccccdc'},
                                style_data_conditional = [
                                    {
                                        'if': {
                                            'filter_query': "{Alert} contains 'Online'"
                                        },
                                        'backgroundColor': '#00cc96'
                                    },
                                    {
                                        'if': {
                                            'filter_query': "{Alert} contains 'Offline'"
                                        },
                                        'backgroundColor': '#ef553b'
                                    }
                                    
                                ]
                            )
                        ])
                    ], className='healthTable')
                ], className='four columns'),
                html.Div([
                    html.Div([
                        dcc.Loading([
                            html.Label(
                                children=[
                                    html.Span('Suspect Reading Logs', className='labels')
                                ]),
                            dash.dash_table.DataTable(
                                id = 'Suspect Table',
                                page_size = 12,
                                style_table = {
                                    'overflowY': 'auto'},
                                style_as_list_view = True,
                                style_cell = {
                                    'backgroundColor': '#111217'},
                                style_header = {
                                    'backgroundColor': '#181b1f',
                                    'fontWeight': 'bold',
                                    'color': '#ccccdc'},
                                style_data = {'color': "#ccccdc"}
                            )
                        ])
                    ], className='suspectTable')
                ], className='eight columns')
            ], className='table')
            
        ], className='row'),
        
        dcc.Interval(
            id='interval-component',
            interval=60000*update_frequency,
            n_intervals=0),

        dcc.Store(id='signal')

    ], className="body")