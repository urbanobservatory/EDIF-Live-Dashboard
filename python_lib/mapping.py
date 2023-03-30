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
    'Newcastle_Urban_Observatory': {
      # Data Source
      'Newcastle-UO': {
        # Stream name
        'PM2.5': {
          # Included variables
          'variables': [
            'PM2.5',
            'PM10',
          ],
          # Stream request parameters
          'parameters': {
            'per-page-limit': 1000,
            'offset-step': 1
          }
        },
        'Traffic-Flow': {
          'variables': [
            'Traffic Flow'
          ],
          'parameters': {
            'per-page-limit': 1,
            'offset-step': 100
          }
        },
        'Weather': {
          'variables': [
            'Temperature',
            'Humidity',
            'Pressure'
          ],
          'parameters': {
            'per-page-limit': 1,
            'offset-step': 100
          }
        }
      },
      'Sheffield-UF': {
        'Air-Quality': {
          'variables': [
            'PM10',
            'PM2.5',
            'Ozone',
            'Nitric Oxide',
            'Nitrogen Dioxide',
            'PM1',
            'PM4',
            'Sulfur Dioxide'
          ],
          'parameters': {
            'per-page-limit': 1000,
            'offset-step': 1
          }
        },
        'Traffic-Flow': {
          'variables': [
            'Traffic Flow'
          ],
          'parameters': {
            'per-page-limit': 1000,
            'offset-step': 1
          }
        },
        'Weather': {
          'variables': [
            'Temperature',
            'Humidity'
          ],
          'parameters': {
            'per-page-limit': 1000,
            'offset-step': 1
          }
        }
      }
    },
    'Manchester_Urban_Observatory': {
      'Manchester-UO': {
        'PM2.5': {
          'variables': [
            'PM2.5'
          ],
          'parameters': {
            'per-page-limit': 1000,
            'offset-step': 1
          },
        },
        'Traffic-Flow': {
          'variables': [
            'Traffic Flow'
          ],
          'parameters': {
            'per-page-limit': 1000,
            'offset-step': 1
          }
        },
        'Black-Carbon': {
          'variables': [
            'Black Carbon'
          ],
          'parameters': {
            'per-page-limit': 1000,
            'offset-step': 1
          }
        }
      }
    },
    'Birmingham_Urban_Observatory': {
      'Zephyr': {
        'Air-Quality': {
          'variables': [
            'Temperature',
            'Nitric Oxide',
            'Ozone',
            'Nitrogen Dioxide',
            'PM1',
            'PM2.5',
            'PM10',
            'Humidity',
            'Pressure'
          ],
          'parameters': {
            'per-page-limit': 1000,
            'offset-step': 1
          }
        }
      },
      'TfWM': {
        'Air-Quality': {
          'variables': [
            'Carbon Monoxide',
            'Nitric Oxide',
            'Ozone',
            'Nitorgen Dioxide',
            'PM1',
            'Sulfur Dioxide',
            'PM2.5',
            'PM100'
          ],
          'parameters': {
            'per-page-limit': 1000,
            'offset-step': 1
          }
        },
        'Weather': {
          'variables': [
            'Temperature',
            'Humidity',
            'Pressure'
          ],
          'parameters': {
            'per-page-limit': 1000,
            'offset-step': 1
          }
        },
        'Traffic-Flow': {
          'variables':[
            'Traffic Flow'
          ],
          'parameters': {
            'per-page-limit': 1000,
            'offset-step': 1
          }
        }
      }
    },
    'Hull_City_Council': {
      'Hull-City-Council': {
        'Air-Quality': {
          'variables': [
            'Nitric Oxide',
            'Ozone',
            'Nitrogen Dioxide',
            'PM1',
            'PM10',
            'PM2.5',
            'Temperature',
            'Humidity',
            'Pressure'
          ],
          'parameters': {
            'per-page-limit': 1,
            'offset-step': 100
          }
        },
        'Traffic-Flow': {
          'variables': [
            'Traffic Flow'
          ],
          'parameters': {
            'per-page-limit': 1,
            'offset-step': 100
          }
        }
      }
    },
    'Cranfield': {
      'Cranfield': {
        'Air-Quality': {
          'variables': [
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
          ],
          'parameters': {
            'per-page-limit': 1000,
            'offset-step': 1
          }
        }
      }
    }
  }