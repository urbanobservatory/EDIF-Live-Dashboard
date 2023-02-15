def variables():
    return {
        'Temperature': {
            'request-variable': 'temperature',
            'units': '°C',
            'colorscale': 'reds'
        },
        'Humidity': {
            'request-variable': 'relativeHumidity',
            'units': '%',
            'colorscale': 'Jet'
        },
         'Pressure': {
             'request-variable': 'atmosphericPressure',
             'units': 'Pa',
             'colorscale': 'YlGnBu'
         },
        'PM2.5': {
            'request-variable': 'pm25',
            'units': 'μgm⁻³',
            'colorscale': 'reds'
        },
        'Traffic Flow': {
            'request-variable': 'intensity',
            'units': 'vehicles/min',
            'colorscale': 'bluered'
        },
        'Black Carbon': {
            'request-variable': 'bc',
            'units': 'ngm⁻³',
            'colorscale': 'Blackbody'
        },
        'Nitric Oxide': {
            'request-variable': 'no',
            'units': 'ppb',
            'colorscale': 'Viridis'
        },
        'Ozone': {
            'request-variable': 'o3',
            'units': 'μgm⁻³',
            'colorscale': 'Blues'
        },
        'Nitrogen Dioxide': {
            'request-variable': 'no2',
            'units': 'μgm⁻³',
            'colorscale': 'RdBu'
        },
        'PM1': {
            'request-variable': 'pm1',
            'units': 'μgm⁻³',
            'colorscale': 'reds'
        },
        'PM10': {
            'request-variable': 'pm10',
            'units': 'μgm⁻³',
            'colorscale': 'reds'
        },
        'PM4': {
            'request-variable': 'pm4',
            'units': 'μgm⁻³',
            'colorscale': 'reds'
        },
        'Sulfur Dioxide': {
            'request-variable': 'so2',
            'units': 'ppm', #TODO: OR PPB ???
            'colorscale': 'Plasma'
        }
    }

def unit_lookup():
    unit_l = {}
    for var_name,var_info in variables().items():
        unit_l[var_info['request-variable']] = var_name
    return unit_l
def UDXsources():
    return {
        # UDX Organisation
        'Newcastle Urban Observatory': {
            # Data Source
            'Newcastle-UO': {
                # Stream name
                'PM2.5': [
                    # Included variables
                    'PM2.5',
                    'PM10',
                ],
                'Traffic-Flow': ['Traffic Flow'],
                'Weather': [
                    'Temperature',
                    'Humidity',
                    'Pressure'
                ]
            },
        'Sheffield-UF': {
                'Air-Quality': [
                    'PM10',
                    'PM2.5',
                    'Ozone',
                    'Nitric Oxide',
                    'Nitrogen Dioxide',
                    'PM1',
                    'PM4',
                    'Sulfur Dioxide'
                ],
                'Traffic-Flow': ['Traffic Flow'],
                'Weather': [
                    'Temperature',
                    'Humidity'
                ]
            }
        },
        'Manchester Urban Observatory': {
            'Manchester-UO': {
                'PM2.5': ['PM2.5'],
                'Traffic-Flow': ['Traffic Flow'],
                'Black-Carbon': ['Black Carbon']
            }
        },
        'Birmingham Urban Observatory': {
            'Zephyr': {
                'PM2.5': [
                    'Temperature',
                    'Traffic Flow',
                    'Nitric Oxide',
                    'Ozone',
                    'Nitrogen Dioxide',
                    'PM1',
                    'PM2.5',
                    'PM10',
                    'Humidity',
                    # 'Pressure'
                ]
            },
            'BCC': {},
            'TfWM': {}
        },
        'Cranfield': {
            'Cranfield': {
                'Air-Quality': [
                    # 'Pressure',
                    # 'CO',
                    # 'Humidity',
                    # 'NO',
                    # 'NO2',
                    # 'NOx',
                    # 'O3',
                    'PM10',
                    'PM2.5',
                    # 'PM4',
                    # 'Temperature'
                ]
            }
        }
    }