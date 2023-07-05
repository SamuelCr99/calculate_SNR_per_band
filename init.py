import netCDF4 as nc
import pandas as pd
import os

def bytes_to_string(bytes):
    string = ""
    for byte in bytes:
        string += byte.decode("utf-8")
    return string

def time_to_string(time):
    h = time[3]
    m = time[4]
    if h<10: h = f"0{h}"
    if m<10: m = f"0{m}"
    return f"{time[0]}/{time[1]}/{time[2]}-{h}:{m}"

def find_datapoints(dir):
    # time, source, station1, station2, el1, az1, el2, az2
    baseline_ds = nc.Dataset(f'{dir}Observables/Baseline.nc')
    timeutc_ds = nc.Dataset(f'{dir}Observables/TimeUTC.nc')
    source_ds = nc. Dataset(f'{dir}Observables/Source.nc')

    stat1 = []
    stat2 = []

    stations = pd.read_csv(f'{dir}stations.csv')
    AzEl_stations = {}
    for station in stations.name:
        El = []
        Az = []
        AzEl_ds = nc.Dataset(f'{dir}{station}/AzEl.nc')
        for row in AzEl_ds["ElTheo"]:
            El.append(row[0])
        for row in AzEl_ds["AzTheo"]:
            Az.append(row[0])
        AzEl = [El,Az]
        AzEl_stations[station] = AzEl

    

def find_stations(dir):
    # name, x, y, z, lat, lon
    xyz = nc.Dataset(f'{dir}Apriori/Station.nc')
    stations = []
    station_xyz = xyz['AprioriStationXYZ'][:]
    stations = list(xyz['AprioriStationList'][:].astype(str))
    for i, _ in enumerate(stations):
        stations[i] = ''.join(stations[i])

    df = pd.DataFrame(columns=['station', 'x', 'y', 'z', 'lat', 'lon'])
    df['station'] = stations
    df['x'] = station_xyz[:,0]
    df['y'] = station_xyz[:,1]
    df['z'] = station_xyz[:,2]
    print(df)

        

if __name__ == '__main__':
    find_stations('data/')