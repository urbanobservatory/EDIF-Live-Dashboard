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

def udx(variable, df, locations, loc):
    if variable == 'pm25' or variable == 'intensity':
        df = df.loc[df['suspectReading.value'] == False]
        sus_df = df.loc[df['suspectReading.value'] == True]

    elif variable == 'temperature':
        df = df.loc[df[variable+'.suspectReading'] == False]
        sus_df = df.loc[df[variable+'.suspectReading'] == True]

    if sus_df.empty:
        sus_df = pd.DataFrame.from_dict({"id":['None'], "dateObserved.value":['-'], "Variable":[variable], "Value":['-'], "Units":['-']})

    sus_df = sus_df.drop_duplicates(subset=['id', 'dateObserved.value'], keep='last')

    #TODO: Figure out the below on how to concatenate previous suspects
    # suspects = []
    # suspects.append(sus_df)

    # if 'suspect_dataframe' in locations[loc]: 
    #     suspects.append(locations[loc]['suspect_dataframe'])

    # if len(suspects) > 1:
    #     suspects = pd.concat(suspects).drop_duplicates().reset_index(drop=True)
    # else:
    #     suspects = suspects[0]

    # sus_df = suspects.drop_duplicates(subset=['id', 'dateObserved.value'], keep='last')

    return df, sus_df