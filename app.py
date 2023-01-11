import os
import dash
import datetime
from dash import dcc, html
from dash.dependencies import Output, Input, State
from dateutil.relativedelta import relativedelta
import figures
from dotenv import load_dotenv
import flask
import pandas as pd

import getData
import allValues
import latestValues

load_dotenv()
update_frequency = int(os.getenv('update_frequency'))
day_period = float(os.getenv('day_period'))
previous_checklist_variable = None
    

# APPLICATION
app = dash.Dash(__name__)

app.layout = html.Div([

    html.Div([
        html.Div([
            html.Div(
                html.H1('EDIF Live Dashboard'),
                className="banner"
            ),
        ], className='four columns'
        ),
        html.Div([
            html.Div([
                html.Div(
                    dcc.Dropdown(
                        id='checklist',
                        options=[
                            'PM2.5',
                            'Traffic Flow',
                            'Black Carbon',
                            'Nitric Oxide',
                            'Ozone',
                            'Nitrogen Dioxide',
                            'PM1',
                            'PM10',
                            'Temperature',
                            'Humidity',
                            'Pressure'
                        ],
                        value='PM2.5',
                        clearable=False
                        # style={
                        #     'color': '#ccccdc', 
                        #     'font-size': 20,
                        #     'text-align': 'center'
                        # }
                    )
                )
            ], className='dropDown'
            )
        ], className='four columns'
        ),
        html.Div([
            html.Div([

            ], className='banner'
        )
        ], className='four columns'
        )
    ], className='row'
    ),

    html.Div([
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(
                            id='Indicators'
                        )
                    ], className='six columns'
                    ),
                    html.Div([
                        html.Div([
                            html.Label(
                                children=[
                                    html.Span('Suspect Reading Logs', className='labels')
                                ]
                            ),
                            #TODO: Create layout for datatable
                            dash.dash_table.DataTable(
                                id='Suspect Table',
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
                            )
                        ], className='row'),
                        html.Div([
                            dash.dash_table.DataTable(
                            id='Alerts Table',
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
                        ], className='row')
                    ], className='six columns'
                    )
                ])
            ], className="row"
            ),
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='Scatter'
                    )
                ], className='twelve columns'
                )
            ], className="row"
            )
        ], className="eight columns"
        ),
        html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='Map'
                    )
                ], className='twelve columns'
                )
            ], className='row'
            )
        ], className='four columns'
        )
    ], className="row"
    ),
    dcc.Interval(
        id='interval-component',
        interval=60000*update_frequency,
        n_intervals=0
    )
], className="body"
)


# CALLBACKS

# @app.callback(Output('Suspect_table', 'data'),
#               Input('interval-component', 'n_intervals'))
# def update_graph_live(n):
#     src       = 'UDX'
#     location  = 'Newcastle'
#     variables = ['PM2.5', 'Temperature', 'Traffic Flow']
#     return figures.suspectTable(src, location, variables)


# @app.callback(Output('Alerts_table', 'data'),
#               Input('interval-component', 'n_intervals'))
# def update_graph_live(n):
#     src       = 'UDX'
#     locations = ['Newcastle', 'Manchester', 'Birmingham']
#     variables = ['PM2.5', 'Temperature', 'Traffic Flow', 'Black Carbon']
#     return figures.alertsTable(src, locations, variables)


@app.callback(
    [
        Output('Indicators', 'figure'),
        Output('Scatter', 'figure'),
        Output('Map', 'figure')#,
        #Output('Suspect Table', 'data'),
        #Output('Alerts Table', 'data')
    ],
    [
        Input('interval-component', 'n_intervals'), 
        Input('checklist', 'value'), 
        Input('Map', 'selectedData')
        #TODO: Add from-to time input
        #TODO: Add refresh input button
    ])
def update_all(n, checklist_variable, map_selection):
    global previous_checklist_variable

    src = 'UDX'
    units = 'hello'
    locations = ['Newcastle', 'Manchester', 'Birmingham']
    
    # Start and end times
    start = datetime.datetime.now()-relativedelta(days=day_period)
    end   = datetime.datetime.now()

    # Get DataFrame
    dfs = []
    for location in locations:
        try:
            df = getData.fetch(src, location, checklist_variable, start, end)
            dfs.append(df)
        except:
            continue
    df = pd.concat(dfs)

    # Get latest values
    sensor_dfs = allValues.run(df)
    latest_df = latestValues.run(sensor_dfs)

    # Reset map_selection if new variable is selected
    if previous_checklist_variable != checklist_variable:
        map_selection = None

    # Get Map Selections DataFrame
    selected = []
    if map_selection != None:
        for i in range(0, len(map_selection['points'])):
            id = map_selection['points'][i]['text'].split(':')[0]
            selected.append(id)
        df = df.loc[df['ID'].isin(selected)]

    previous_checklist_variable = checklist_variable

    return \
        figures.indicators(checklist_variable, df), \
        figures.scatter(checklist_variable, units, df), \
        figures.map(checklist_variable, latest_df)


# For if CSS Stylesheet does not load
css_directory = os.getcwd()
stylesheets = ['stylesheet.css']
static_css_route = '/static/'

@app.server.route('{}<stylesheet>'.format(static_css_route))
def serve_stylesheet(stylesheet):
    if stylesheet not in stylesheets:
        raise Exception(
            '"{}" is excluded from the allowed static files'.format(
                stylesheet
            )
        )
    return flask.send_from_directory(css_directory, stylesheet)

for stylesheet in stylesheets:
    app.css.append_css({"external_url": "/static/{}".format(stylesheet)})
    

# Run App
if __name__ == "__main__":
    app.run_server(debug=True)