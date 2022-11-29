# Returns a plotly map

def uo(df):
    return [dict(
        type = 'scattermapbox', #'scattergeo',
        locationmode = 'country names',
        lon = df['Sensor Centroid Longitude.0'],
        lat = df['Sensor Centroid Latitude.0'],
        text = df['text'],
        mode = 'markers',
        marker = dict(
            size = df['Value'],
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
                title="μgm⁻³"
            )
        ))]

def udx(variable, df):
    return [dict(
        type = 'scattermapbox', #'scattergeo',
        locationmode = 'country names',
        lon = df['location.value.coordinates'].str[0],
        lat = df['location.value.coordinates'].str[1],
        text = df['text'],
        mode = 'markers',
        marker = dict(
            size = df['Value'],
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
                title="μgm⁻³"
            )
        ))]