# EDIF-Live-Dashboard
Install requirements:

    pip install dash pandas plotly dotenv requests numpy

run: 
    
    python app.py

To Do:
- Error handling if no data is available for selected period
- On refresh only request data which isn't already available, and remove data older than limit - look into traces (https://plotly.com/python/creating-and-updating-figures/#adding-traces)
- Add dropdown to switch between observatories