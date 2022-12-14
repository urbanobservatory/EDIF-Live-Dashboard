# EDIF-Live-Dashboard
## Installation and Run
Install requirements:

    pip install dash pandas plotly dotenv requests numpy

Run: 
    
    python app.py

Access Port:

    http://127.0.0.1:8050/

<br>

## UDX Onboarding Status

| Variable         | Units              | Newcastle    | Manchester   | Birmingham  |
| ---------------- | ------------------ | ------------ | ------------ | ----------- |
| PM2.5            | μgm⁻³              | Working      | Working      | Working     |
| Temperature      | °C                 | Working      | Unavailable  | Working     |
| Traffic Flow     | Number of Vehicles | Working      | Working      | Unavailable |
| Black Carbon     | ngm⁻³              | Unintegrated | Working      | Unavailable |
| Nitric Oxide     | μgm⁻³              | Unintegrated | Unavailable  | Working     |
| Ozone            | μgm⁻³              | Unintegrated | Unavailable  | Working     |
| Nitrogen Dioxide | μgm⁻³              | Unintegrated | Unavailable  | Working     |
| PM1              | μgm⁻³              | Unintegrated | Unavailable  | Working     |
| PM10             | μgm⁻³              | Unintegrated | Unavailable  | Working     |
| Humidity         | %                  | Unintegrated | Unavailable  | Working     |
| Pressure         | Pa                 | Unintegrated | Unavailable  | Working     |


<br>

### To Add:
- [] Number of sensors online etc.
- [] Map of all locations
- [] Baseline historical data - monthly averages over the past n years
- [] Dropdown to switch between observatories

<br>

### To Do:
- [] Fill in empty lines for suspect and alert tables to keep them the same size
- [] Error handling if no data is available for selected period
- [] On refresh only request data which isn't already available, and remove data older than limit - look into traces (https://plotly.com/python/creating-and-updating-figures/#adding-traces)