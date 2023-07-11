import pandas as pd


def find_index_of_source_baseline(source, baseline):
    """
    Find all rows in datapoints.csv that match a given source and baseline.

    Parameters:
    source(string): The source to find
    baseline(string): The baseline to find

    Returns:
    A list of indices of rows in datapoints.csv that match the given source and baseline.
    """
    df = pd.read_csv("data/derived/datapoints.csv", skiprows=1)
    station1 = baseline.split("/")[0]
    station2 = baseline.split("/")[1]
    return df.loc[(df.Source == source) & (df['Station1'] == station1) & (df['Station2'] == station2) & (df.Q_code > 5)].index.tolist()


def find_index_of_source(source):
    """
    Find all rows in datapoints.csv that match a given source.

    Parameters:
    source(string): The source to find

    Returns:
    A list of indices of rows in datapoints.csv that match the given source and baseline.
    """
    df = pd.read_csv("data/derived/datapoints.csv", skiprows=1)
    return df.loc[(df.Source == source) & (df.Q_code > 5)].index.tolist()


def find_index_of_source_ignore_stations(source, ignore):
    """
    Find all rows in datapoints.csv that match a given source.

    Parameters:
    source(string): The source to find

    Returns:
    A list of indices of rows in datapoints.csv that match the given source and baseline.
    """
    df = pd.read_csv("data/derived/datapoints.csv", skiprows=1)

    # Find all rows that don't contain the stations in ignore
    for station in ignore:
        df = df.loc[(df.Station1 != station) & (df.Station2 != station)]

    return df.loc[(df.Source == source) & (df.Q_code > 5)].index.tolist()


if __name__ == '__main__':
    source = "1803+784"
    baseline = "GGAO12M/ISHIOKA"
    matching_stations = find_index_of_source_baseline(source, baseline)
    print(matching_stations)
