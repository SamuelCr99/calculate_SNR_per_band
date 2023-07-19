import pandas as pd


def find_station_matches(df):
    """
    Creates a dictionary mapping every source to a list of stations that have 
    data for that source. 

    Parameters:
    No parameters

    Returns:
    d (dict): Dictionary mapping every source to a list of stations that have 
    data for that source.

    """
    d = {}
    for _, row in df.iterrows():
        source = row['Source']
        station1 = row['Station1']
        station2 = row['Station2']

        if source not in d:
            d[source] = {'stations': {},
                         'observations': 0}

        if station1 not in d[source]['stations']:
            d[source]['stations'][station1] = 0
        d[source]['stations'][station1] += 1

        if station2 not in d[source]['stations']:
            d[source]['stations'][station2] = 0
        d[source]['stations'][station2] += 1

        d[source]['observations'] += 1

    return d



