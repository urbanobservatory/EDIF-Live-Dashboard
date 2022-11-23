# Returns dataframe of suspect readings

import pandas as pd

def uo(variable, df):
    suspects = []
    for i, l in enumerate(df['data.'+variable]):
        ds = pd.DataFrame(l)
        ds = ds[ds['Flagged as Suspect Reading'] == True]
        ds = ds.drop('Flagged as Suspect Reading', axis=1)
        suspects.append(ds)
    suspect_df = pd.concat(suspects).drop_duplicates().reset_index(drop=True)
    return suspect_df

def udx(variable, df):
    #TODO: This
    pass