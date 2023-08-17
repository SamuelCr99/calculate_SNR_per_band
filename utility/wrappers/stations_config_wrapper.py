import pandas as pd
import os
import netCDF4 as nc
import numpy as np

CONFIG_PATH = "data/derived/config.csv"

class StationsConfigWrapper:

    def __init__(self, session_dir="", path=""):
        self.session_dir = session_dir
        self.path = path if path else CONFIG_PATH

        try:
            self.df = pd.read_csv(self.path)
        except:
            create_config(self.session_dir, self.path)
            self.df = pd.read_csv(self.path)
            
        self.df_copy = self.df.copy(deep=True)
    
    def save(self, path=""):
        save_path = self.path if path == "" else path
        self.df.to_csv(save_path, index=False)
        self.df_copy = self.df.copy(deep=True)

    def restore(self):
        self.df = self.df_copy.copy(deep=True)
    
    def delete(self):
        if self.session_dir:
            create_config(self.session_dir, self.path)
            self.df = pd.read_csv(self.path)
            self.df_copy = self.df.copy(deep=True)

    def has_changed(self):
        return not self.df.equals(self.df_copy)

    def get_SEFD(self, station, band):
        if type(band) == int:
            band = ["A","B","C","D","S","X"][band]
        sefd_col = f"{band}_SEFD"
        return float(self.df.loc[self.df.name == station,sefd_col].iloc[0])
    
    def set_SEFD(self, station, band, sefd):
        if type(band) == int:
            band = ["A","B","C","D","S","X"][band]
        sefd_col = f"{band}_SEFD"
        self.df.loc[self.df.name == station,sefd_col] = max(round(float(sefd),1),1)

    def select(self, station):
        self.df.loc[self.df.name == station,"selected"] = 1

    def deselect(self, station):
        self.df.loc[self.df.name == station,"selected"] = 0
    
    def is_selected(self, station):
        return self.df.loc[self.df.name == station,"selected"].iloc[0]

    def toggle(self, station):
        if self.is_selected(station):
            self.deselect(station)
            return False
        else:
            self.select(station)
            return True
    
    def get_deselected_stations(self):
        return self.df.loc[self.df["selected"] == 0]["name"].to_list()

def create_config(session_dir, path):
    """
    Finds stations and their SEFD

    Parameter:
    No parameters!

    Returns:
    No return values!
    """
    if session_dir[-1] != '/': session_dir += '/'
    station_list_path = f"{session_dir}Apriori/Station.nc"
    station_array = np.ma.getdata(nc.Dataset(station_list_path)["AprioriStationList"]).tolist()
    station_list = list(map(lambda stat: bytes_to_string(stat), station_array))

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
    joined_df = joined_df.drop(columns=['Antenna','X','Y','Z','Lat','Lon'])

    joined_df = joined_df.rename(
        columns={'Name': 'name'})

    joined_df["selected"] = [1]*len(joined_df["name"])
    
    joined_df = joined_df.loc[joined_df.name.isin(station_list)]

    # Write to csv file
    if path == CONFIG_PATH:
        data_folders = os.listdir('data/')
        if 'derived' not in data_folders:
            os.mkdir('data/derived')

    joined_df.to_csv(path, index=False)

def bytes_to_string(bytes):
    # Converts a list of byte characters to a string
    string = ""
    for byte in bytes:
        char = byte.decode("utf-8")
        if char != " ": string += char
    return string