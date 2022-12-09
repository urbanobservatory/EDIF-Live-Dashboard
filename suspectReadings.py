# Returns dataframe of suspect readings
#TODO: Should only need to drop duplicates a single time and make sure to use reset_index=True

import pandas as pd

def run(variable, df):
    df = df.loc[df['Suspect Reading'] == False]
    sus_df = df.loc[df['Suspect Reading'] == True]

    if sus_df.empty:
        sus_df = pd.DataFrame.from_dict({"ID":['None'], "Datetime":['-'], "Variable":[variable], "Value":['-'], "Units":['-']})

    sus_df = sus_df.drop_duplicates(subset=['ID', 'Datetime'], keep='last')

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