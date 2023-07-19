import pandas as pd


def find_index(source="", df="", baseline="", ignored_stations=[]):
    """
    Find all rows in a datapoints.csv that match a given source and/or baseline

    Gives the indices of the matching rows, excluding the rows that either
    contains one of the ignored stations or that has a Quality Code of 5 or less

    Parameters:
    source(string): The B1950 name of the source to find
    baseline(string): The baseline to search for, on the form "name/name"
    ignored_stations(list): A list with the names of the stations to ignore

    Returns:
    A list of indices of rows in datapoints.csv that match the given source and baseline.
    """
    # df = pd.read_csv("data/derived/datapoints.csv", skiprows=1)

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
