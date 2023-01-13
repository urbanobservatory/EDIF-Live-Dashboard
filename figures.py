import plotly.graph_objects as go
import pandas as pd

import layouts
import run
import graphCustomisation
import allValues

def indicators(df):

    n_sources = df['Location'].nunique()
    n_sensors = df['ID'].nunique()
    n_records = len(df.index)
    average = df["Value"].mean()

    variable = df['Variable'].iloc[0]
    units = df['Units'].iloc[0]

    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            title = 'Data Sources',
            mode = "number",
            value = n_sources,
            delta = {'position': "top", 'reference': 320},
            domain = {'row': 0, 'column': 0}
        )
    )

    fig.add_trace(
        go.Indicator(
            title = 'Active Streams',
            mode = "number",
            value = n_sensors,
            delta = {'position': "top", 'reference': 320},
            domain = {'row': 0, 'column': 1}
        )
    )

    fig.add_trace(
        go.Indicator(
            title = 'Number of Records',
            mode = "number",
            value = n_records,
            delta = {'position': "top", 'reference': 320},
            domain = {'row': 1, 'column': 0}
        )
    )

    fig.add_trace(
        go.Indicator(
            title = 'Average Value',
            mode = "number",
            value = average,
            # number = {'suffix': ' '+units},
            delta = {'position': "top", 'reference': 320},
            domain = {'row': 1, 'column': 1}
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
                    color='#ccccdc'
                )
            )
        )

    fig.update_layout(
        layouts.graph(variable, units)
    )

    return fig


def suspectTable(src, location, variables):
    l = []
    for variable in variables:
        d = run.run(src, location, variable)
        l.append(d['suspect_dataframe'])
    df = pd.concat(l)
    df = df.drop_duplicates(subset=['ID', 'Datetime'], keep='last')
    df = df.loc[:, ["ID", "Datetime", "Variable", "Value", "Units"]]  
    return df.to_dict('records')


def alertsTable(src, locations, variables):
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