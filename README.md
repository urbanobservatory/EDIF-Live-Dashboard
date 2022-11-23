# EDIF-Live-Dashboard
Pip install requirements:

    dash, pandas, plotly, dotenv

run: 
    
    python app.py

To Do:
- Error handling if no data is available for selected period
- Auto update after n minutes - Test
- On refresh only request data which isn't already available, and remove data older than limit - look into traces (https://plotly.com/python/creating-and-updating-figures/#adding-traces)
- Error handling if data isn't available - don't want the app to crash
- Reference units from something rather than hard coding
- Scale map points relative to smallest and largest values with min and max sizes
- Could add a slider to maps to show changes over time - need to group and average data by day (https://plotly.com/python/bubble-maps/#reference)
- Put logos in banner
- Add dropdown to switch between observatories