import pandas as pd


def find_station_matches():
    """
    Creates a dictionary mapping every source to a list of stations that have 
    data for that source. 

    Parameters:
    No parameters

    Returns:
    d (dict): Dictionary mapping every source to a list of stations that have 
    data for that source.

    """
    df = pd.read_csv('data/derived/datapoints.csv',
                     skiprows=1)[['Station1', 'Station2', 'Source']]

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


if __name__ == '__main__':
    d = find_station_matches()


