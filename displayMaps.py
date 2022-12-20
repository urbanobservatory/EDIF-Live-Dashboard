# Returns customised plotly maps

import graphCustomisation

def map(variable, units, df):
    return [dict(
        type = 'scattermapbox', #'scattergeo',
        locationmode = 'country names',
        lon = df['Longitude'],
        lat = df['Latitude'],
        text = df['text'],
        mode = 'markers',
        marker = dict(
            size = 10, #df['Value'],
            opacity = 0.8,
            reversescale = False,
            autocolorscale = False,
            symbol = 'circle',
            line = dict(
                width=1,
                color='rgba(102, 102, 102)'
            ),
            colorscale = "Reds", #Blackbody,Bluered,Blues,Cividis,Earth,Electric,Greens,Greys,Hot,Jet,Picnic,Portland,Rainbow,RdBu,Reds,Viridis,YlGnBu,YlOrRd
            cmin = 0,
            color = df['Value'],
            cmax = df['Value'].max(),
            colorbar=dict(
                title=units
            )
        ))]

def run(location, variable, units, df):
    df['text'] = df['ID']+', '+df['Value'].astype(str)+units
    df, color = graphCustomisation.customise(df, variable, location)
    return map(variable, units, df)