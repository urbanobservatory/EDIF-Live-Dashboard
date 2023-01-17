def variables():
    return {
        'Temperature': {
            'request-variable': 'temperature',
            'units': '°C'
        },
        'Humidity': {
            'request-variable': 'humidity',
            'units': '%'
        },
        'Pressure': {
            'request-variable': 'pressure',
            'units': 'Pa'
        },
        'PM2.5': {
            'request-variable': 'pm25',
            'units': 'μgm⁻³'
        },
        'Traffic Flow': {
            'request-variable': 'intensity',
            'units': 'Vehicles'
        },
        'Black Carbon': {
            'request-variable': 'bc',
            'units': 'ngm⁻³'
        },
        'Nitric Oxide': {
            'request-variable': 'no',
            'units': 'μgm⁻³'
        },
        'Ozone': {
            'request-variable': 'o3',
            'units': 'μgm⁻³'
        },
        'Nitrogen Dioxide': {
            'request-variable': 'no2',
            'units': 'μgm⁻³'
        },
        'PM1': {
            'request-variable': 'pm1',
            'units': 'μgm⁻³'
        },
        'PM10': {
            'request-variable': 'pm10',
            'units': 'μgm⁻³'
        }
    }

def sources():
    return {
        'NewcastleUO': [
            'PM2.5',
            'Traffic Flow',
            'Temperature'
        ],
        'ManchesterUO': [
            'PM2.5',
            'Traffic Flow',
            'Black Carbon'
        ],
        'BirminghamUO': [
            'PM2.5',
            'Temperature',
            'Traffic Flow',
            'Nitric Oxide',
            'Ozone',
            'Nitrogen Dioxide',
            'PM1',
            'PM10',
            'Humidity',
            'Pressure'
        ]
    }