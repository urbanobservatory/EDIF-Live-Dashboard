# Returns a list of data frames for all sensor values for a given variable

def run(df):
    sensor_dfs=[]
    id_list = list(dict.fromkeys(list(df['ID'])))
    grouped = df.groupby(df['ID'])
    for i in id_list:
        sensor_dfs.append(grouped.get_group(i))
    return sensor_dfs