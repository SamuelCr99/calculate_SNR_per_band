import netCDF4 as nc
import pandas as pd
import numpy as np
from statistics import mean
import math
import os

BAND_A_B_LIM = 4500
BAND_B_C_LIM = 6000
BAND_C_D_LIM = 8000

def bytes_to_string(bytes):
    # Converts a list of byte characters to a string
    string = ""
    for byte in bytes:
        string += byte.decode("utf-8")
    return string

def time_to_string(time):
    # Converts YMDHM time list to a nicely formatted string
    h = time[3]
    m = time[4]
    if h<10: h = f"0{h}"
    if m<10: m = f"0{m}"
    return f"{time[0]}/{time[1]}/{time[2]}-{h}:{m}"

def find_datapoints(dir):
    """
    Finds all information about all observations

    It finds the time, seconds, source, stations in the baseline, elevation and
    azimuth for both stations, the frequency of each band (A, B, C & D) and the
    total frequency, the SNR for each band and the total SNR, the bandwidth for
    each band and the integration time of the observation. It saves this to a
    CSV file.

    Parameter:
    dir(string): The source directory

    Returns:
    No return values!
    """

    # Import datasets
    baseline_ds = nc.Dataset(f'{dir}Observables/Baseline.nc')
    timeutc_ds = nc.Dataset(f'{dir}Observables/TimeUTC.nc')
    source_ds = nc.Dataset(f'{dir}Observables/Source.nc')
    channel_info = nc.Dataset(f'{dir}Observables/ChannelInfo_bX.nc')
    ref_freq_ds = nc.Dataset(f'{dir}Observables/RefFreq_bX.nc')
    snr_info = nc.Dataset(f'{dir}Observables/SNR_bX.nc')
    corrinfo = nc.Dataset(f'{dir}Observables/CorrInfo-difx_bX.nc')

    # Find source
    source = []
    for elem in np.ma.getdata(source_ds["Source"]).tolist():
        source.append(bytes_to_string(elem))
    
    # Find time
    time = []
    for elem in np.ma.getdata(timeutc_ds["YMDHM"]):
        time.append(time_to_string(elem))
    second = []
    for elem in np.ma.getdata(timeutc_ds["Second"]):
        second.append(elem)
    
    # Find stations
    stat1 = []
    stat2 = []
    for elem in np.ma.getdata(baseline_ds["Baseline"]).tolist():
        stat1.append(bytes_to_string(elem[0]).replace(" ",""))
        stat2.append(bytes_to_string(elem[1]).replace(" ",""))

    # Find frequency for each channel
    A_channels = []
    B_channels = []
    C_channels = []
    D_channels = []
    for frequencies in np.ma.getdata(channel_info["ChannelFreq"]).tolist():
            A_channels.append(list(filter(lambda f: f>0 and f<BAND_A_B_LIM,frequencies)))
            B_channels.append(list(filter(lambda f: f>BAND_A_B_LIM and f<BAND_B_C_LIM,frequencies)))
            C_channels.append(list(filter(lambda f: f>BAND_B_C_LIM and f<BAND_C_D_LIM,frequencies)))
            D_channels.append(list(filter(lambda f: f>BAND_C_D_LIM,frequencies)))
    
    # Find frequency for each band
    A_freq = list(map(lambda l: mean(l), A_channels))
    B_freq = list(map(lambda l: mean(l), B_channels))
    C_freq = list(map(lambda l: mean(l), C_channels))
    D_freq = list(map(lambda l: mean(l), D_channels))

    tot_freq = ref_freq_ds["RefFreq"][0]
    tot_freq *= len(time)

    # Find elevation and azimuth
    stations = pd.read_csv(f'{dir}stations.csv')
    time_sec_list = list(map(lambda t,s: f"{t}:{s}",time,second))
    stat_time_df = pd.DataFrame({"stat1": stat1, "stat2": stat2, "time": time_sec_list})

    AzEl_dict = {}
    for station in stations.name:
        if station not in os.listdir(dir):
            continue

        AzEl_ds = nc.Dataset(f'{dir}{station}/AzEl.nc')

        current_df = stat_time_df[(stat_time_df.stat1 == station) | (stat_time_df.stat2 == station)]
        current_df = current_df.drop_duplicates(subset=["time"])

        El = list(map(lambda row: row[0], AzEl_ds["ElTheo"]))
        Az = list(map(lambda row: row[0], AzEl_ds["AzTheo"]))
        station_dict = {}

        for _, row in current_df.iterrows():
            station_dict[row.time] = {"El": El.pop(0), "Az": Az.pop(0)}

        AzEl_dict[station] = station_dict

    El1 = list(map(lambda stat,t,s: AzEl_dict[stat][f"{t}:{s}"]["El"], stat1, time, second))
    Az1 = list(map(lambda stat,t,s: AzEl_dict[stat][f"{t}:{s}"]["Az"], stat1, time, second))
    El2 = list(map(lambda stat,t,s: AzEl_dict[stat][f"{t}:{s}"]["El"], stat2, time, second))
    Az2 = list(map(lambda stat,t,s: AzEl_dict[stat][f"{t}:{s}"]["Az"], stat2, time, second))

    # Find SNR
    chanamp = np.ma.getdata(channel_info['ChanAmpPhase'])
    snr = np.ma.getdata(snr_info['SNR']).tolist()

    A_SNR = []
    B_SNR = []
    C_SNR = []
    D_SNR = []

    for i in range(len(stat1)):
    
        amp = chanamp[i,:,0]
        phase = chanamp[i,:,1]

        cosines = list(map(lambda a,p: a*math.cos(math.radians(p)),amp,phase))
        sines = list(map(lambda a,p: a*math.sin(math.radians(p)),amp,phase))

        # Count the number of data points in each channel which don't equal 0
        N_A = len(A_channels[i])
        N_B = len(B_channels[i])
        N_C = len(C_channels[i])
        N_D = len(D_channels[i])
        M = N_A + N_B + N_C + N_D

        T = math.sqrt(pow(sum(cosines),2)+pow(sum(sines),2))
        A = math.sqrt(pow(sum(cosines[0:N_A]),2)+pow(sum(sines[0:N_A]),2))
        B = math.sqrt(pow(sum(cosines[N_A:N_A+N_B]),2)+pow(sum(sines[N_A:N_A+N_B]),2))
        C = math.sqrt(pow(sum(cosines[N_A+N_B:N_A+N_B+N_C]),2)+pow(sum(sines[N_A+N_B:N_A+N_B+N_C]),2))
        D = math.sqrt(pow(sum(cosines[N_A+N_B+N_C:M]),2)+pow(sum(sines[N_A+N_B+N_C:M]),2))

        A_SNR.append(A/T*snr[i]*math.sqrt(M/N_A))
        B_SNR.append(B/T*snr[i]*math.sqrt(M/N_B))
        C_SNR.append(C/T*snr[i]*math.sqrt(M/N_C))
        D_SNR.append(D/T*snr[i]*math.sqrt(M/N_D))

    # Find bandwidth
    A_bw = list(map(lambda ch: 32*len(ch), A_channels))
    B_bw = list(map(lambda ch: 32*len(ch), B_channels))
    C_bw = list(map(lambda ch: 32*len(ch), C_channels))
    D_bw = list(map(lambda ch: 32*len(ch), D_channels))

    # Find integration time
    int_time = np.ma.getdata(corrinfo["EffectiveDuration"]).tolist()

    # Collect everything into a dataframe
    df = pd.DataFrame({"YMDHM": time,
                       "Second": second,
                       "Source": source,
                       "Station1": stat1,
                       "Station2": stat2,
                       "El1": El1,
                       "Az1": Az1,
                       "El2": El2,
                       "Az2": Az2,
                       "A_freq": A_freq,
                       "B_freq": B_freq,
                       "C_freq": C_freq,
                       "D_freq": D_freq,
                       "tot_freq": tot_freq,
                       "A_SNR": A_SNR,
                       "B_SNR": B_SNR,
                       "C_SNR": C_SNR,
                       "D_SNR": D_SNR,
                       "tot_SNR": snr,
                       "A_bw": A_bw,
                       "B_bw": B_bw,
                       "C_bw": C_bw,
                       "D_bw": D_bw,
                       "int_time": int_time})

    df.to_csv("data/datapoints.csv",index=False)


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

    station_sefds = pd.read_csv('data/equip.cat', delim_whitespace=True)[['Antenna', 'X_SEFD', 'S_SEFD']]
    station_locations = pd.read_csv('data/position.cat', delim_whitespace=True)[['Name','X', 'Y', 'Z', 'Lat','Lon']]
    joined_df = pd.merge(station_locations, station_sefds, left_on='Name', right_on='Antenna')
    joined_df = joined_df.drop(columns=['Antenna'])
    
    joined_df = joined_df.rename(columns={'Name': 'name', 'X': 'x', 'Y': 'y', 'Z': 'z', 'Lon': 'lon', 'Lat': 'lat'})
    
    # Write to csv file
    joined_df.to_csv('data/stations.csv', index=False)


if __name__ == '__main__':
    find_stations()
    find_datapoints("data/sessions/session1/")