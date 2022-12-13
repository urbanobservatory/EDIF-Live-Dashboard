# Returns dataframe of suspect readings

import pandas as pd

def run(variable, df):
    ok_df = df.loc[df['Suspect Reading'] == False]
    sus_df = df.loc[df['Suspect Reading'] == True]

    if sus_df.empty:
        sus_df = pd.DataFrame.from_dict({"ID":['None'], "Datetime":['-'], "Variable":[variable], "Value":['-'], "Units":['-']})

    return ok_df, sus_df