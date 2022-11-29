# Returns a plotly graph

import plotly.graph_objs as go

def plot(df, name, color):
    return go.Scatter(x=list(df['Datetime']),
                      y=list(df['Value']),
                      mode='markers',
                      #marker_symbol='circle-open',
                      marker_color=color,
                      opacity=0.4,
                      name=name)