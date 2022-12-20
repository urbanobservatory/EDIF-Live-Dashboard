import plotly.graph_objects as go
import pandas as pd

import displayCard
import displayGauge
import displayMaps
import layouts
import run

def indicators(src, locations, variables_a, variable_b, domain_a, domain_b, domain_c, units_b):
    fig = go.Figure()

    sensors, records, temperatures = 0, 0, []

    location_names = []
    for location in locations:
        for variable_a in variables_a:
            try:
                data_a = run.run(src, location, variable_a)
                if data_a['status'] == 'Offline':
                    continue
                if location not in location_names:
                    location_names.append(location)
                sensors += data_a['sensors']
                records += data_a['records']
            except:
                continue
    fig.add_trace(displayCard.run(location, sensors, domain_a, 'Active Sensors'))
    fig.add_trace(displayCard.run(location, records, domain_c, 'Number of Records'))

    for location in locations:
        try:
            data_b = run.run(src, location, variable_b)
            temperatures.append(round(data_b['latest_readings']['Value'].mean(), 1))
        except:
            continue
    temperature = sum(temperatures) / len(temperatures)
    display_gauge = displayGauge.run(src, location, variable_b, units_b, temperature, domain_b)
    fig.add_trace(display_gauge[0])

    fig.update_layout(layouts.indicators(location_names, variables_a))

    return fig


def pm25Graph(src, locations, variable, units):
    fig = go.Figure()

    location_names = []
    for location in locations:
        try:
            data = run.run(src, location, variable, units)
            if data['status'] == 'Offline':
                continue
            location_names.append(location)
            for graph in data['display_graphs']:
                fig.add_trace(graph)
        except:
            continue

    fig.update_layout(layouts.graph(src, location_names, variable, units))

    return fig


def trafficFlowGraph(src, locations, variable, units):
    fig = go.Figure()

    location_names = []
    for location in locations:
        try:
            data = run.run(src, location, variable, units)
            if data['status'] == 'Offline':
                continue
            location_names.append(location)
            for graph in data['display_graphs']:
                fig.add_trace(graph)
        except:
            continue

    fig.update_layout(layouts.graph(src, location_names, variable, units))

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


def map(src, locations, variable, units):
    l = []
    for location in locations:
        data = run.run(src, location, variable, units)
        l.append(data['latest_readings'])
    df = pd.concat(l)
    display_maps = displayMaps.run(location, variable, units, df)
    layout = layouts.map(src, locations, variable)
    return dict(data=display_maps, layout=layout)