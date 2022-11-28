# Returns a plotly graph

import plotly.graph_objs as go

def uo(df, name, color):
    return go.Scatter(x=list(df['Datetime']),
                      y=list(df['Value']),
                      mode='markers',
                      #marker_symbol='circle-open',
                      marker_color=color,
                      opacity=0.4,
                      name=name)

def udx(df, name, color, variable):
    return go.Scatter(x=list(df['Datetime']),
                      y=list(df[variable+'.value']),
                      mode='markers',
                      #marker_symbol='circle-open',
                      marker_color=color,
                      opacity=0.4,
                      name=name)