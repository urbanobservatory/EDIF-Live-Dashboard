import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import json
import utils

env_vars = json.load(open('/code/env.json'))

update_frequency = int(env_vars['update_frequency'])
day_period = float(env_vars['update_frequency'])

def layout():
  return html.Div([
    html.Div([
      dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle("Information")),
        dbc.ModalBody(
          "Info coming soon. Please report any bugs to daniel.bell2@ncl.ac.uk"
        ),
        dbc.ModalFooter(
          dbc.Button(
            "Close",
            id="close-centered",
            className="ms-auto",
            n_clicks=0
          )
        ),
      ], id="modal-centered", centered=True, is_open=False)
    ], className='modal'),

    html.Div([
      html.Div([
        html.Img(
          id='DTlogo',
          src='/assets/thumbnail_image006_inverted_153x76.png'
        )
      ], className='oneBanner column'),
      html.Div([
        html.Div([
          html.H1(
            'Live Dashboard Demo',
            style={"color": "#ccccdc"}
          )
        ], className='banner box')
      ], className='threeBanner columns'),
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
            value='PM2.5',
            clearable=False
          )
        ], className='banner box')
      ], className='threeBanner columns'),
      html.Div([
        html.Div([
          dcc.DatePickerRange(
            id='date-picker-range',
            month_format='Do-MMM-Y'
          )
        ], className='banner box')
      ], className='threeBanner columns'),
      html.Div([
        html.Div([
          dcc.Loading([
            html.Button(
              'Refresh',
              id='Refresh Button',
              n_clicks = 0
            )
          ], type='circle')
        ], className='banner box')
      ], className='oneBanner column'),
      html.Div([
        html.Div([
          dcc.Loading([
            html.Button(
              'Download',
              id='Download-Button',
              n_clicks = 0
            ),
            dcc.Download(id='download-dataframe-csv')
          ], type='circle')
        ], className='banner box')
      ], className='oneBanner column'),
    ], className='row'),

    html.Br(),

    dcc.Tabs([
      dcc.Tab(
        id='Tab1',
        label='Visualisation',
        style={'backgroundColor':'#181b1f'},
        selected_style={
          'color':'#ccccdc',
          'backgroundColor':'#272a2e'},
        children=[

          html.Br(),

          html.Div([

            html.Div([

              html.Div([
                html.Div([
                  dcc.Loading([
                    html.Div([
                      html.Div([
                        dcc.Graph(
                          id='Indicators A',
                          style={'height':140}
                        )
                      ])
                    ], className="row"),
                    html.Div([
                      html.Div([
                        dcc.Graph(
                          id='Indicators B',
                          style={'height':140})
                      ])
                    ], className="row")
                  ])
                ], className='figure box')
              ], className='row'),

              html.Br(),

              html.Div([
                html.Div([
                  html.Div([
                    dcc.Loading(
                      dcc.Graph(
                        id='Scatter All',
                        style={'height':280}
                      )
                    )
                  ], className='figure box')
                ], className='eightGraphsOuter columns'),
                html.Div([
                  html.Div([
                    dcc.Loading(
                      dcc.Graph(
                        id='BoxPlot',
                        style={'height':280}
                      )
                    )
                  ], className='figure box')
                ], className='fourGraphsOuter columns')
              ], className="row"),

              html.Br(),

              html.Div([

                html.Div([
                  html.Div([
                    dcc.Loading(
                      dcc.Graph(
                        id='Scatter3D',
                        style={'height':600}
                      )
                    )
                  ], className='scatter3d figure box')
                ], className='sixGraphs columns'),
                html.Div([
                  html.Div([
                    dcc.Loading(
                      dcc.Graph(
                        id='Scatter Hover',
                        style={'height':278}
                      )
                    )
                  ], className='figure box row'),
                  html.Br(),
                  html.Div([
                    dcc.Loading(
                      dcc.Graph(
                        id='Histogram',
                        style={'height':278}
                      )
                    )
                  ], className='figure box row')
                ], className='sixGraphs columns')
              ], className='row'),

            ], className="eightGraphsOuter columns"),

            html.Div([
              html.Div([
                dcc.Loading(
                  dcc.Graph(
                    id='Map',
                    style={'height':1288}
                  )
                )
              ], className='map figure box')
            ], className='fourGraphsOuter columns')

          ], className="row"),
                  
        ], className='custom-tab', selected_className='custom-tab--selected'
        ),

        dcc.Tab(
          id='Tab2',
          label='Metadata', 
          style={'backgroundColor':'#181b1f'},
          selected_style={
            'color':'#ccccdc',
            'backgroundColor':'#272a2e'},
          children=[

            html.Br(),

            html.Div([
              html.Div([
                html.Div([
                  html.Label(
                    children=[
                      html.Span('Data Availability', className='labels')
                    ]
                  ),
                  dcc.Loading(
                    html.Div(
                      dcc.Graph(
                        id='Calendar Plot',
                        style={'height':150}
                      )
                    )
                  )
                ], className='calendarPlot')
              ], className='twelve columns')
            ], className='row'),

            html.Br(),

            # html.Div([
            #   html.Div([
            #     html.Div([
            #       dcc.Loading(
            #         html.Div(
            #           dcc.Graph(
            #             id='Update Intervals',
            #             style={'height':300}
            #           )
            #         )
            #       )
            #     ], className='calendarPlot')
            #   ], className='twelve columns')
            # ], className='row'),

            # html.Br(),

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
                        style_table = {'overflowY': 'auto'},
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
                            'if': {'filter_query': "{Alert} contains 'Online'"},
                            'backgroundColor': '#00cc96'
                          },
                          {
                            'if': {'filter_query': "{Alert} contains 'Offline'"},
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
                        ]
                      ),
                      dash.dash_table.DataTable(
                        id = 'Suspect Table',
                        page_size = 12,
                        style_table = {'overflowY': 'auto'},
                        style_as_list_view = True,
                        style_cell = {'backgroundColor': '#111217'},
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

          ], className='custom-tab', selected_className='custom-tab--selected'
        )
    ], parent_className='custom-tabs', className='custom-tabs-container'
    ),
              
    dcc.Interval(
      id='interval-component',
      interval=60000*update_frequency,
      n_intervals=0
    ),

    dcc.Store(id='signal')

  ], className="body")