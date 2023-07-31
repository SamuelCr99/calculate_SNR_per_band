import pandas as pd
import os

def find_stations():
    """
    Finds stations, their coordinates and their SEFD

    Combines two lists, one with coordinates and one with SEFD, matching on
    station name. Saves to a CSV file.

    Parameter:
    dir(string): The source directory

    Returns:
    No return values!
    """

    station_sefds = pd.read_csv(
        'data/standard/equip.cat', delim_whitespace=True)[['Antenna', 'X_SEFD', 'S_SEFD']]

    station_sefds['A_SEFD'] = station_sefds['S_SEFD']
    station_sefds['B_SEFD'] = station_sefds['X_SEFD']
    station_sefds['C_SEFD'] = station_sefds['X_SEFD']
    station_sefds['D_SEFD'] = station_sefds['X_SEFD']

    station_locations = pd.read_csv(
        'data/standard/position.cat', delim_whitespace=True)[['Name', 'X', 'Y', 'Z', 'Lat', 'Lon']]
    joined_df = pd.merge(station_locations, station_sefds,
                         left_on='Name', right_on='Antenna')
    joined_df = joined_df.drop(columns=['Antenna'])

    joined_df = joined_df.rename(
        columns={'Name': 'name', 'X': 'x', 'Y': 'y', 'Z': 'z', 'Lon': 'lon', 'Lat': 'lat'})

    joined_df["selected"] = [1]*len(joined_df["name"])

    # Write to csv file
    data_folders = os.listdir('data/')
    if 'derived' not in data_folders:
        os.mkdir('data/derived')

    joined_df.to_csv("data/derived/stations.csv", index=False)