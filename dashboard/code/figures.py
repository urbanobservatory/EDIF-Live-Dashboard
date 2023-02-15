import plotly.graph_objects as go
import pandas as pd

import layouts
import graphCustomisation
import allValues
from dash_data import mapping

align_position = 'left'

def indicatorsA(df):

    variable = df['Variable'].iloc[0]
    units = df['Units'].iloc[0]

    df = graphCustomisation.customise(df, variable)

    min_row = df[df.Value == df.Value.min()]
    max_row = df[df.Value == df.Value.max()]

    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            title = {
                'text': 'Data Sources',
                'align': align_position},
            mode = "number",
            value = df['Source'].nunique(),
            delta = {'position': "top", 'reference': 320},
            domain = {'row': 0, 'column': 0},
            align = align_position
        )
    )

    fig.add_trace(
        go.Indicator(
            title = {
                'text': 'Active Streams',
                'align': align_position},
            mode = "number",
            value = df['ID'].nunique(),
            delta = {'position': "top", 'reference': 320},
            domain = {'row': 0, 'column': 1},
            align = align_position
        )
    )

    fig.add_trace(
        go.Indicator(
            title = {
                'text': 'Number of Records',
                'align': align_position},
            mode = "number",
            value = len(df.index),
            delta = {'position': "top", 'reference': 320},
            domain = {'row': 0, 'column': 2},
            align = align_position
        )
    )

    fig.update_layout(
        layouts.indicators(variable),
        transition_duration=500
    )

    return fig


def indicatorsB(df):

    variable = df['Variable'].iloc[0]
    units = df['Units'].iloc[0]

    df = graphCustomisation.customise(df, variable)

    min_row = df[df.Value == df.Value.min()]
    max_row = df[df.Value == df.Value.max()]

    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            title = {
                'text': 'Average Value',
                'align': align_position},
            mode = "number",
            value = df['Value'].mean(),
            number = {'suffix': ' '+units},
            delta = {'position': "top", 'reference': 320},
            domain = {'row': 0, 'column': 0},
            align = align_position
        )
    )

    fig.add_trace(
        go.Indicator(
            title = {
                'text': 'Minimum Value',
                'align': align_position},
            mode = "number",
            value = min_row['Value'].iloc[0],
            number = {'suffix': ' '+units},
            delta = {'position': "top", 'reference': 320},
            domain = {'row': 0, 'column': 1},
            align = align_position
        )
    )

    fig.add_trace(
        go.Indicator(
            title = {
                'text': 'Maximum Value',
                'align': align_position},
            mode = "number",
            value = max_row['Value'].iloc[0],
            number = {'suffix': ' '+units},
            delta = {'position': "top", 'reference': 320},
            domain = {'row': 0, 'column': 2},
            align = align_position
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
    if units == None:
        units = ''


    df = graphCustomisation.customise(df, variable)

    variable_map = mapping.variables()
    colorscale = variable_map[variable]['colorscale']

    fig = go.Figure()

    # Lines also included if number of sensors below limit
    if df['ID'].nunique() > 5:
        fig.add_trace(
            go.Scatter(
                x = list(df['Datetime']),
                y = list(df['Value']),
                text = df['ID'].astype(str)+': '+df['Value'].astype(str)+' '+units,
                mode ='markers',
                marker = {
                    # 'marker_symbol': 'circle-open',
                    'color': df['Value'],
                    # 'opacity': 0.5,
                    'colorscale': colorscale,
                    'showscale': False,
                    'colorbar': {
                        'title': units,
                        'orientation': 'v'
                    }
                }
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
        layouts.scatterAll(variable, units), 
        transition_duration=500
    )

    return fig


def scatter_hover(df):
    variable = ''
    if len(df['Variable']) > 0:
        variable = df['Variable'].iloc[0]
    units = ''
    if len(df['Units']) > 0:
        units = df['Units'].iloc[0]

    df = graphCustomisation.customise(df, variable)

    variable_map = mapping.variables()
    colorscale = variable_map[variable]['colorscale']

    fig = go.Figure()

    sensor_dfs = allValues.run(df)

    for df in sensor_dfs:
        fig.add_trace(
            go.Scatter(
                x = list(df['Datetime']),
                y = list(df['Value']),
                text = df['ID'].astype(str)+': '+df['Value'].astype(str)+units,
                mode = 'lines+markers',
                marker = {
                    'color': '#ccccdc' #'#00CC96'
                }
            )
        )

    fig.update_layout(
        layouts.scatterHover(variable, units)
    )

    return fig


def scatter3D(df):
    variable = df['Variable'].iloc[0]
    units = df['Units'].iloc[0]

    df = graphCustomisation.customise(df, variable)

    fig = go.Figure()

    sources = df['Source'].unique()

    for source in sources:
        df2 = df.loc[df['Source'] == source]

        fig.add_trace(
            go.Scatter3d(
                x = df2['Datetime'],
                y = df2['Source'],
                z = df2['Value'],
                text = df['ID'].astype(str)+': '+df['Value'].astype(str)+' '+units,
                mode = 'markers',
                marker = {
                    'size': 2
                }
            )
        )

        # fig.add_trace(
        #     go.Scatter3d(
        #         x = df['Period'],
        #         y = df['Traffic_Flow_values'],
        #         z = df['Variable_values'],
        #         mode = 'lines+markers',
        #         marker = {
        #             'size': 5,
        #             # 'marker_symbol': 'circle-open',
        #             'color': df['Variable_values'],
        #             # 'opacity': 0.5,
        #             'showscale': True,
        #             # 'colorbar': {
        #             #     #'title': units,
        #             #     'orientation': 'v'
        #             # }
        #         }
        #     )
        # )
    
    fig.update_layout(
        layouts.scatter3d(variable, units)
    )

    return fig


def boxPlot(df):
    variable = df['Variable'].iloc[0]
    units = df['Units'].iloc[0]

    df = graphCustomisation.customise(df, variable)

    fig = go.Figure()

    sources = df['Source'].unique()

    for source in sources:
        df2 = df.loc[df['Source'] == source]

        fig.add_trace(
            go.Box(
                y = df2['Value'],
                name = source,
                boxpoints = False,
            )
        )

    fig.update_layout(
        layouts.boxplot(variable, units),
        transition_duration=500,
    )
    
    return fig


def histogram(df):

    variable = df['Variable'].iloc[0]
    units = df['Units'].iloc[0]

    df = graphCustomisation.customise(df, variable)

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            x = df['Value'],
            # opacity=0.7,
            marker_color='#ccccdc' #'#00CC96' #'indianred'
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

    source_map = mapping.UDXsources()
    sources = []

    for organisation in source_map:
        for source in source_map[organisation]:
            for stream in source_map[organisation][source]:
                if variable in source_map[organisation][source][stream]:
                    sources.append(source)

    min_date = df['Datetime'].min()
    max_date = df['Datetime'].max()

    l = []
    for source in sources:
        if df['Source'].str.contains(source).any():
            l.append(f'{source} {variable} Stream is Online')
        else:
            l.append(f'{source} {variable} Stream is Offline')

    # df = pd.DataFrame({f'Alerts for {min_date} - {max_date}':l})
    df = pd.DataFrame({'Alert': l})

    return df.to_dict('records')


def map(df, map_selection): #, map_relayout):

    variable = df['Variable'].iloc[0]
    units = df['Units'].iloc[0]

    df = graphCustomisation.customise(df, variable)

    df['text'] = df['ID'].astype(str)+': '+df['Value'].astype(str)+' '+units
    df = graphCustomisation.customise(df, variable)

    variable_map = mapping.variables()
    colorscale = variable_map[variable]['colorscale']

    fig = go.Figure()

    fig.add_trace(
        go.Scattermapbox(
            lon = df['Longitude'],
            lat = df['Latitude'],
            text = df['text'],
            mode = 'markers',
            marker = go.scattermapbox.Marker(
                size=15,
                opacity=0.6,
                symbol = 'circle',
                colorscale = colorscale, 
                #cmin = 0,
                showscale = True,
                color = df['Value'],
                cmax = df['Value'].max(),
                colorbar = {
                    'title': units,
                    'orientation': 'h'
                }
            )
        )
    )

    fig.update_layout(
        layouts.map(variable, map_selection), #, map_relayout),
        transition_duration=500
    )

    return fig