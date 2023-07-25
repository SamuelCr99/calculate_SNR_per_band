def find_index(source="", df="", baseline="", ignored_stations=[]):
    """
    Find all rows in a DataFrame that match a given source and/or baseline

    Gives the indices of the matching rows, excluding the rows that contains one
    of the ignored stations.

    Parameters:
    source(string): The B1950 name of the source to find
    df(DataFrame): A Pandas DataFrame to search through
    baseline(string): The baseline to search for, on the form "name/name"
    ignored_stations(list): A list with the names of the stations to ignore

    Returns:
    A list of indices of rows that match the given source and baseline.
    """
    
    # Find all rows that don't contain the stations in ignored_stations
    for station in ignored_stations:
        df = df.loc[(df.Station1 != station) & (df.Station2 != station)]

    # Find all rows that contains the specified baseline
    if baseline:
        station1 = baseline.split("/")[0]
        station2 = baseline.split("/")[1]
        df = df.loc[(df['Station1'] == station1) &
                    (df['Station2'] == station2)]

    # Find all rows that contain the selected source
    if source:
        df = df.loc[(df.Source == source)]

    return df.index.tolist()
