# Returns dataframe of suspect readings
#TODO: Should only need to drop duplicates a single time and make sure to use reset_index=True

import pandas as pd

def uo(variable, df, dict_all):
    suspects = []
    if 'suspect_dataframe' in dict_all: suspects.append(dict_all['suspect_dataframe'])
    for i, l in enumerate(df['data.'+variable]):
        ds = pd.DataFrame(l)
        ds = ds[ds['Flagged as Suspect Reading'] == True]
        ds = ds.drop('Flagged as Suspect Reading', axis=1)
        suspects.append(ds)
    # if len(suspects) > 1:
    #     pd.concat(suspects).drop_duplicates().reset_index(drop=True)
    # else:
    #     suspects = suspects[0]
    return pd.concat(suspects).drop_duplicates().reset_index(drop=True)

def udx(variable, df, dict_all):
    suspects = []
    if 'suspect_dataframe' in dict_all: suspects.append(dict_all['suspect_dataframe'])
    if variable == 'pm25' or variable == 'intensity':
        suspects.append(df.loc[df['suspectReading.value']==True])
    elif variable == 'temperature':
        suspects.append(df.loc[df[variable+'.suspectReading']==True])
    if len(suspects) > 1:
        suspects = pd.concat(suspects).drop_duplicates().reset_index(drop=True)
    else:
        suspects = suspects[0]
    return suspects.drop_duplicates(subset=['id', 'dateObserved.value'], keep='last')