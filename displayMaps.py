# Returns customised plotly maps

import graphCustomisation
import map

def uo(variable, df):
    df['text'] = df['Sensor Name']+', '+df['Value'].astype(str)+' μgm⁻³'
    df, color = graphCustomisation.uo(df, variable)
    return map.uo(df)

def udx(variable, df):
    #TODO: This
    pass