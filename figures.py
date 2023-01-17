import plotly.graph_objects as go
import pandas as pd

import layouts
import graphCustomisation
import allValues
import mapping

def indicators(df):

    min_row = df[df.Value == df.Value.min()]
    max_row = df[df.Value == df.Value.max()]

    variable = df['Variable'].iloc[0]
    units = df['Units'].iloc[0]

    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            title = 'Data Sources',
            mode = "number",
            value = df['Location'].nunique(),
            delta = {'position': "top", 'reference': 320},
            domain = {'row': 0, 'column': 0}
        )
    )

    fig.add_trace(
        go.Indicator(
            title = 'Active Streams',
            mode = "number",
            value = df['ID'].nunique(),
            delta = {'position': "top", 'reference': 320},
            domain = {'row': 0, 'column': 1}
        )
    )

    fig.add_trace(
        go.Indicator(
            title = 'Number of Records',
            mode = "number",
            value = len(df.index),
            delta = {'position': "top", 'reference': 320},
            domain = {'row': 0, 'column': 2}
        )
    )

    fig.add_trace(
        go.Indicator(
            title = 'Average Value',
            mode = "number",
            value = df['Value'].mean(),
            # number = {'suffix': ' '+units},
            delta = {'position': "top", 'reference': 320},
            domain = {'row': 1, 'column': 0}
        )
    )

    fig.add_trace(
        go.Indicator(
            title = 'Minimum Value',
            mode = "number",
            value = min_row['Value'].iloc[0],
            # number = {'suffix': min_row['ID'].iloc[0]},
            delta = {'position': "top", 'reference': 320},
            domain = {'row': 1, 'column': 1}
        )
    )

    fig.add_trace(
        go.Indicator(
            title = 'Maximum Value',
            mode = "number",
            value = max_row['Value'].iloc[0],
            delta = {'position': "top", 'reference': 320},
            domain = {'row': 1, 'column': 2}
        )
    )

    fig.update_layout(
        layouts.indicators(variable),
        transition_duration=500
    )

    return fig


def scatter_all(df):

    variable = df['Variable'].iloc[0]
    units = df['Units'].iloc[0]
    df, colorscales = graphCustomisation.customise(df, variable)

    fig = go.Figure()

    # Lines also included if number of sensors below limit
    if df['ID'].nunique() > 10:
        fig.add_trace(
            go.Scatter(
                x=list(df['Datetime']),
                y=list(df['Value']),
                text=df['ID']+': '+df['Value'].astype(str)+' '+units,
                mode='markers',
                marker=dict(
                    # marker_symbol='circle-open',
                    color=df['Value'],
                    # opacity=0.5,
                    colorscale=colorscales[variable],
                    showscale=False,
                    colorbar=dict(
                        title=units,
                        orientation='v'
                    )
                )
            )
        )

    else:
        sensor_dfs = allValues.run(df)

        for df in sensor_dfs:
            fig.add_trace(
                go.Scatter(
                    x=list(df['Datetime']),
                    y=list(df['Value']),
                    text=df['ID']+': '+df['Value'].astype(str)+units,
                    mode='lines+markers'
                )
            )

    fig.update_layout(
        layouts.graph(variable, units), 
        transition_duration=500
    )

    return fig


def scatter_hover(df):

    variable = df['Variable'].iloc[0]
    units = df['Units'].iloc[0]
    df, colorscales = graphCustomisation.customise(df, variable)

    fig = go.Figure()

    sensor_dfs = allValues.run(df)

    for df in sensor_dfs:
        fig.add_trace(
            go.Scatter(
                x=list(df['Datetime']),
                y=list(df['Value']),
                text=df['ID']+': '+df['Value'].astype(str)+units,
                mode='lines+markers',
                marker=dict(
                    color='#00CC96'
                )
            )
        )

    fig.update_layout(
        layouts.graph(variable, units)
    )

    return fig


def histogram(df):

    variable = df['Variable'].iloc[0]
    units = df['Units'].iloc[0]

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            x = df['Value'],
            # opacity=0.7,
            marker_color='#00CC96' #'indianred'
        )
    )

    fig.update_layout(
        layouts.histogram(variable, units),
        transition_duration=500,
    )

    return fig


def suspectTable(df):
    variable = df['Variable'].iloc[0]
    units = df['Units'].iloc[0]

    if 'Suspect Reading' in df:
        df = df.loc[df['Suspect Reading'] == True]

    if 'Suspect Reading' not in df or df.empty:
        df = pd.DataFrame.from_dict({"ID":['None'], "Datetime":['-'], "Variable":[variable], "Value":['-'], "Units":[units]})
    
    return df.to_dict('records')


def healthTable(df):
    variable = df['Variable'].iloc[0]
    units = df['Units'].iloc[0]

    source_map = mapping.sources()
    sources = []

    for source in source_map:
        if variable in source_map[source]:
            sources.append(source)

    min_date = df['Datetime'].min()
    max_date = df['Datetime'].max()

    l = []
    for source in sources:
        if df['Location'].str.contains(source).any():
            l.append(f'{source} {variable} Stream is Online')
        else:
            l.append(f'{source} {variable} Stream is Offline')

    df = pd.DataFrame({f'Alerts for {min_date} - {max_date}':l})

    return df.to_dict('records')


def map(df, map_selection): #, map_relayout):

    variable = df['Variable'].iloc[0]
    units = df['Units'].iloc[0]
    df['text'] = df['ID']+': '+df['Value'].astype(str)+' '+units
    df, colorscales = graphCustomisation.customise(df, variable)

    fig = go.Figure()

    fig.add_trace(
        go.Scattermapbox(
            lon = df['Longitude'],
            lat = df['Latitude'],
            text = df['text'],
            mode = 'markers',
            marker = go.scattermapbox.Marker(
                size=15,
                opacity=0.8,
                symbol = 'circle',
                colorscale = colorscales[variable], 
                #cmin = 0,
                showscale = True,
                color = df['Value'],
                cmax = df['Value'].max(),
                colorbar=dict(
                    title=units,
                    orientation='h'
                )
            )
        )
    )

    fig.update_layout(
        layouts.map(variable, map_selection), #, map_relayout),
        transition_duration=500
    )

    return fig