import pandas as pd
import netCDF4 as nc
import numpy as np
import math
import itertools
import os
from statistics import mean
from utility.calc.to_uv import convert_uv

BAND_A_B_LIM = 4500
BAND_B_C_LIM = 6000
BAND_C_D_LIM = 8000

class DataWrapper:

    def __init__(self,df):
        """
        Initializes the DataWrapper

        Can provide a pandas DataFrame, in which case it will be used. Can also
        provide a string path to the session directory.

        Parameters:
        df(string/DataFrame): Path of session or a pandas DataFrame

        Returns:
        The newly created data object
        """

        # If provided a DataFrame, use that one
        if type(df) == pd.DataFrame:
            self.df = df

        # If provided a string, use it as the directory of a session
        elif type(df) == str:

            # Check if it is a ABCD session or an SX session
            self.is_abcd = ("Observables" in os.listdir(f"{df}/")) and (
                "QualityCode_bS.nc" not in os.listdir(f"{df}/Observables/"))
            self.is_sx = not self.is_abcd
            
            if self.is_abcd:
                self.df = find_datapoints_abcd(df)
            else:
                self.df = find_datapoints_sx(df)
    
    def __len__(self):
        # Get the amount of rows (data points) in the data object
        return len(self.df.index.to_list())
    
    def get(self, source="", baseline="", station="", ignored_stations=[], bands=None, copy=False):
        """
        Get a new DataWrapper from the old DataWrapper that match a given source,
        baseline, station and/or ignored station.

        Parameters:
        source(string): The B1950 name of the source to find
        baseline(string/list): The baseline to search for, on the form "name/name" or as a list of station names
        stations(string): The name of a station to search for
        ignored_stations(list): A list with the names of the stations to ignore
        copy(boolean): If the it should be a deep copy of the old DataFrame

        Returns:
        A DataWrapper that match the given criteria
        """
        return DataWrapper(self.get_df(source=source, baseline=baseline, station=station, ignored_stations=ignored_stations, bands=bands, copy=copy))
    
    def get_df(self, source="", baseline="", station="", ignored_stations=[], bands=None, copy=False):
        """
        Get a new DataFrame from the DataWrapper that match a given source,
        baseline, station and/or ignored station.

        Parameters:
        source(string): The B1950 name of the source to find
        baseline(string/list): The baseline to search for, on the form "name/name" or as a list of station names
        stations(string): The name of a station to search for
        ignored_stations(list): A list with the names of the stations to ignore
        copy(boolean): If the it should be a deep copy of the old DataFrame

        Returns:
        A DataFrame that match the given criteria
        """
        if copy:
            df = self.df.copy(deep=True)
        else:
            df = self.df
        
        # Find all rows that contain the selected source
        if source:
            df = df.loc[(df.Source == source)]
        
        # Find all rows that contains the specified baseline
        if baseline:
            if type(baseline) == str:
                station1 = baseline.split("/")[0]
                station2 = baseline.split("/")[1]
            if type(baseline) == list:
                station1 = baseline[0]
                station2 = baseline[1]
            
            df = df.loc[((df.Station1 == station1) & (df.Station2 == station2)) |
                        ((df.Station1 == station2) & (df.Station2 == station1))]
            
        # Find all rows that include the specified station
        if station:
            df = df.loc[(df.Station1 == station) | (df.Station2 == station)] 
        
        # Find all rows that don't contain the stations in ignored_stations
        for station in ignored_stations:
            df = df.loc[(df.Station1 != station) & (df.Station2 != station)]
    
        if not bands == None:
            if type(bands) != list:
                bands = [bands]
            band_letters = []
            for band in bands:
                band_letters.append(["A","B","C","D","S","X"][band])
            df = df.loc[df.band.isin(band_letters)]

        return df

    def get_source_dict(self):
        """
        Creates a dictionary mapping every source to a list of stations that have 
        data for that source. 

        The keys of the dictionary are the names of the sources. The values are
        dictionaries that contain the keys "stations" and "observations". The
        value of "stations" is a dictionary with the names of the stations as
        keys and the number of observations from that station as value. The
        value of "observations" is the total number of observations for that
        source.

        Parameters:
        No parameters

        Returns:
        d (dict): Dictionary mapping every source to a list of stations that have 
        data for that source.

        """
        d = {}
        for _, row in self.df.iterrows():
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
        
        if self.is_abcd:
            num_bands = 4
        else:
            num_bands = 2

        for source in d:
            d[source]["observations"] = int(d[source]["observations"]/num_bands)

            for station in d[source]["stations"]:
                d[source]["stations"][station] = int(d[source]["stations"][station]/num_bands)

        return d
    
    def iterrows(self):
        """
        Gives an iterable for the DataFrame that goes through each row (or
        "point") in the data

        Parameters:
        No parameter

        Returns:
        Iterable
        """
        return self.df.iterrows()
    

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
    if h < 10:
        h = f"0{h}"
    if m < 10:
        m = f"0{m}"
    return f"{time[0]}/{time[1]}/{time[2]}-{h}:{m}"

def is_float(v):
    # Tests if a variable can be converted to a float
    try:
        float(v)
        return True
    except:
        return False

def find_datapoints_abcd(dir, save_to_csv=False):
    """
    Finds all information about all observations, for the A, B, C and D bands

    Parameter:
    dir(string): The source directory
    save_to_csv(boolean): If the DataFrame should be saved as a .csv file

    Returns:
    The DataFrame containing the information
    """
    if dir[-1] != '/':
        dir += '/'

    # Import datasets
    baseline_ds = nc.Dataset(f'{dir}Observables/Baseline.nc')
    timeutc_ds = nc.Dataset(f'{dir}Observables/TimeUTC.nc')
    source_ds = nc.Dataset(f'{dir}Observables/Source.nc')
    channel_info = nc.Dataset(f'{dir}Observables/ChannelInfo_bX.nc')
    snr_info = nc.Dataset(f'{dir}Observables/SNR_bX.nc')
    corrinfo = nc.Dataset(f'{dir}Observables/CorrInfo-difx_bX.nc')
    quality_code_ds = nc.Dataset(f'{dir}Observables/QualityCode_bX.nc')
    ref_freq_ds = nc.Dataset(f'{dir}Observables/RefFreq_bX.nc')
    uv_ds = nc.Dataset(f'{dir}ObsDerived/UVFperAsec_bX.nc')

    # Find source
    source = []
    for elem in np.ma.getdata(source_ds["Source"]).tolist():
        source.extend([bytes_to_string(elem)]*4)

    num_observations = int(len(source)/4)

    # Find time
    time = []
    for elem in np.ma.getdata(timeutc_ds["YMDHM"]):
        time.extend([time_to_string(elem)]*4)
    second = []
    for elem in np.ma.getdata(timeutc_ds["Second"]):
        second.extend([elem]*4)

    # Find stations
    stat1 = []
    stat2 = []
    for elem in np.ma.getdata(baseline_ds["Baseline"]).tolist():
        stat1.extend([bytes_to_string(elem[0]).replace(" ", "")]*4)
        stat2.extend([bytes_to_string(elem[1]).replace(" ", "")]*4)

    # Find frequency for each channel
    A_channels = []
    B_channels = []
    C_channels = []
    D_channels = []
    if is_float(channel_info["ChannelFreq"][0]):
        frequency_matrix = [np.ma.getdata(
            channel_info["ChannelFreq"]).tolist()]*num_observations

    else:
        frequency_matrix = np.ma.getdata(channel_info["ChannelFreq"]).tolist()

    for frequencies in frequency_matrix:
        if type(frequencies) == float:
            frequencies = [frequencies]
        A_channels.append(
            list(filter(lambda f: f > 0 and f < BAND_A_B_LIM, frequencies)))
        B_channels.append(
            list(filter(lambda f: f > BAND_A_B_LIM and f < BAND_B_C_LIM, frequencies)))
        C_channels.append(
            list(filter(lambda f: f > BAND_B_C_LIM and f < BAND_C_D_LIM, frequencies)))
        D_channels.append(
            list(filter(lambda f: f > BAND_C_D_LIM, frequencies)))

    # Find frequency for each band
    A_freq = list(map(lambda l: mean(l) if l != [] else None, A_channels))
    B_freq = list(map(lambda l: mean(l) if l != [] else None, B_channels))
    C_freq = list(map(lambda l: mean(l) if l != [] else None, C_channels))
    D_freq = list(map(lambda l: mean(l) if l != [] else None, D_channels))

    # Find elevation and azimuth
    stations = list(set(stat1 + stat2))
    time_sec_list = list(map(lambda t, s: f"{t}:{s}", time, second))
    stat_time_df = pd.DataFrame(
        {"stat1": stat1, "stat2": stat2, "time": time_sec_list})

    AzEl_dict = {}
    for station in stations:
        if station not in os.listdir(dir):
            continue

        AzEl_ds = nc.Dataset(f'{dir}{station}/AzEl.nc')

        current_df = stat_time_df[(stat_time_df.stat1 == station) | (
            stat_time_df.stat2 == station)]
        current_df = current_df.drop_duplicates(subset=["time"])

        El = list(map(lambda row: row[0], AzEl_ds["ElTheo"]))
        Az = list(map(lambda row: row[0], AzEl_ds["AzTheo"]))
        station_dict = {}

        for _, row in current_df.iterrows():
            station_dict[row.time] = {"El": El.pop(0), "Az": Az.pop(0)}

        AzEl_dict[station] = station_dict

    El1 = list(
        map(lambda stat, t, s: AzEl_dict[stat][f"{t}:{s}"]["El"], stat1, time, second))
    Az1 = list(
        map(lambda stat, t, s: AzEl_dict[stat][f"{t}:{s}"]["Az"], stat1, time, second))
    El2 = list(
        map(lambda stat, t, s: AzEl_dict[stat][f"{t}:{s}"]["El"], stat2, time, second))
    Az2 = list(
        map(lambda stat, t, s: AzEl_dict[stat][f"{t}:{s}"]["Az"], stat2, time, second))

    # Find SNR
    chanamp = np.ma.getdata(channel_info['ChanAmpPhase'])
    snr = np.ma.getdata(snr_info['SNR']).tolist()

    A_SNR = []
    B_SNR = []
    C_SNR = []
    D_SNR = []

    for i in range(num_observations):

        amp = chanamp[i, :, 0]
        phase = chanamp[i, :, 1]

        cosines = list(
            map(lambda a, p: a*math.cos(math.radians(p)), amp, phase))
        sines = list(map(lambda a, p: a*math.sin(math.radians(p)), amp, phase))

        # Count the number of data points in each channel which don't equal 0
        N_A = len(A_channels[i])
        N_B = len(B_channels[i])
        N_C = len(C_channels[i])
        N_D = len(D_channels[i])
        M = N_A + N_B + N_C + N_D

        T = math.sqrt(pow(sum(cosines), 2)+pow(sum(sines), 2))
        A = math.sqrt(pow(sum(cosines[0:N_A]), 2)+pow(sum(sines[0:N_A]), 2))
        B = math.sqrt(
            pow(sum(cosines[N_A:N_A+N_B]), 2)+pow(sum(sines[N_A:N_A+N_B]), 2))
        C = math.sqrt(
            pow(sum(cosines[N_A+N_B:N_A+N_B+N_C]), 2)+pow(sum(sines[N_A+N_B:N_A+N_B+N_C]), 2))
        D = math.sqrt(
            pow(sum(cosines[N_A+N_B+N_C:M]), 2)+pow(sum(sines[N_A+N_B+N_C:M]), 2))

        curr_A_SNR = A/T*snr[i]*math.sqrt(M/N_A) if N_A != 0 else 0
        A_SNR.append(curr_A_SNR)

        curr_B_SNR = B/T*snr[i]*math.sqrt(M/N_B) if N_B != 0 else 0
        B_SNR.append(curr_B_SNR)

        curr_C_SNR = C/T*snr[i]*math.sqrt(M/N_C) if N_C != 0 else 0
        C_SNR.append(curr_C_SNR)

        curr_D_SNR = D/T*snr[i]*math.sqrt(M/N_D) if N_D != 0 else 0
        D_SNR.append(curr_D_SNR)

    # Find bandwidth
    bw_per_band = np.ma.getdata(channel_info["SampleRate"]).tolist()[0]/2

    A_bw = list(map(lambda ch: bw_per_band*len(ch), A_channels))
    B_bw = list(map(lambda ch: bw_per_band*len(ch), B_channels))
    C_bw = list(map(lambda ch: bw_per_band*len(ch), C_channels))
    D_bw = list(map(lambda ch: bw_per_band*len(ch), D_channels))

    # Find integration time
    int_time = list(np.repeat(np.ma.getdata(corrinfo["EffectiveDuration"]).tolist(), 4))

    # Find quality code
    qualcode = list(np.repeat(np.ma.getdata(quality_code_ds["QualityCode"]).tolist(), 4))

    # Find u and v
    uv_data = np.ma.getdata(uv_ds['UVFperAsec']).tolist()
    u_l = list(map(lambda u: u[0]*206264.81, uv_data))
    v_l = list(map(lambda v: v[1]*206264.81, uv_data))

    # Find reference frequency
    ref_freq = np.ma.getdata(ref_freq_ds["RefFreq"]).tolist()*num_observations*4

    # Find u and v for each band
    A_u, A_v = list(zip(*list(map(lambda u,v,o_f,n_f: convert_uv(u,v,o_f,n_f),u_l,v_l,ref_freq,A_freq))))
    B_u, B_v = list(zip(*list(map(lambda u,v,o_f,n_f: convert_uv(u,v,o_f,n_f),u_l,v_l,ref_freq,B_freq))))
    C_u, C_v = list(zip(*list(map(lambda u,v,o_f,n_f: convert_uv(u,v,o_f,n_f),u_l,v_l,ref_freq,C_freq))))
    D_u, D_v = list(zip(*list(map(lambda u,v,o_f,n_f: convert_uv(u,v,o_f,n_f),u_l,v_l,ref_freq,D_freq))))    

    # Zip zip
    freq = list(itertools.chain(*zip(A_freq, B_freq, C_freq, D_freq)))
    SNR = list(itertools.chain(*zip(A_SNR, B_SNR, C_SNR, D_SNR)))
    bw = list(itertools.chain(*zip(A_bw, B_bw, C_bw, D_bw)))
    u = list(itertools.chain(*zip(A_u, B_u, C_u, D_u)))
    v = list(itertools.chain(*zip(A_v, B_v, C_v, D_v)))

    band = ["A", "B", "C", "D"] * num_observations

    print(len(time))
    print(len(second))
    print(len(source))
    print(len(stat1))
    print(len(stat2))
    print(len(band))
    print(len(El1))
    print(len(freq))
    print(len(SNR))
    print(len(bw))
    print(len(int_time))
    print(len(qualcode))
    print(len(u))

    # Collect everything into a dataframe
    df = pd.DataFrame({"YMDHM": time,
                       "Second": second,
                       "Source": source,
                       "Station1": stat1,
                       "Station2": stat2,
                       "band": band,
                       "El1": El1,
                       "Az1": Az1,
                       "El2": El2,
                       "Az2": Az2,
                       "freq": freq,
                       "SNR": SNR,
                       "bw": bw,
                       "int_time": int_time,
                       "Q_code": qualcode,
                       "u": u,
                       "v": v})

    # Sort out rows with too low quality
    df = df.loc[(df.Q_code.astype(int) > 5)]

    df.reset_index(inplace=True)

    if save_to_csv:
        datapoints_csv = f"Generated from vgosDB: {dir.split('/')[-2]}\n" + df.to_csv(
            index=False)
        with open("data/derived/datapoints.csv", "w") as file:
            file.write(datapoints_csv)

    return df

def find_datapoints_sx(dir, save_to_csv=False):
    """
    Finds all information about all observations, for the S and X bands

    Parameter:
    dir(string): The source directory
    save_to_csv(boolean): If the DataFrame should be saved as a .csv file

    Returns:
    The DataFrame containing the information
    """
    if dir[-1] != '/':
        dir += '/'

    # Import datasets
    baseline_ds = nc.Dataset(f'{dir}Observables/Baseline.nc')
    timeutc_ds = nc.Dataset(f'{dir}Observables/TimeUTC.nc')
    source_ds = nc.Dataset(f'{dir}Observables/Source.nc')
    quality_code_s_ds = nc.Dataset(f'{dir}Observables/QualityCode_bS.nc')
    quality_code_x_ds = nc.Dataset(f'{dir}Observables/QualityCode_bX.nc')
    uv_s_ds = nc.Dataset(f'{dir}ObsDerived/UVFperAsec_bS.nc') 
    uv_x_ds = nc.Dataset(f'{dir}ObsDerived/UVFperAsec_bX.nc')
    channel_info_s = nc.Dataset(f'{dir}Observables/ChannelInfo_bS.nc')
    channel_info_x = nc.Dataset(f'{dir}Observables/ChannelInfo_bX.nc')
    snr_info_s = nc.Dataset(f'{dir}Observables/SNR_bS.nc')
    snr_info_x = nc.Dataset(f'{dir}Observables/SNR_bX.nc')
    corrinfo = nc.Dataset(f'{dir}Observables/CorrInfo-difx_bS.nc') # Might need one for each

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
        stat1.append(bytes_to_string(elem[0]).replace(" ", ""))
        stat2.append(bytes_to_string(elem[1]).replace(" ", ""))

    # Find quality code
    qualcode_s = list(bytes_to_string(np.ma.getdata(
        quality_code_s_ds["QualityCode"]).tolist()))
    qualcode_x = list(bytes_to_string(np.ma.getdata(
        quality_code_x_ds["QualityCode"]).tolist()))
    
    # Find u and v
    uv_data_s = np.ma.getdata(uv_s_ds['UVFperAsec']).tolist()
    uv_data_x = np.ma.getdata(uv_x_ds['UVFperAsec']).tolist()

    u_s = list(map(lambda u: u[0]*206264.81, uv_data_s))
    v_s = list(map(lambda v: v[1]*206264.81, uv_data_s))
    
    u_x = list(map(lambda u: u[0]*206264.81, uv_data_x))
    v_x = list(map(lambda v: v[1]*206264.81, uv_data_x))

    # Find SNR
    S_SNR = np.ma.getdata(snr_info_s["SNR"]).tolist()
    X_SNR = np.ma.getdata(snr_info_x["SNR"]).tolist()
    
    # Find integration time
    int_time = np.ma.getdata(corrinfo["EffectiveDuration"]).tolist()

    # Find bandwidth
    N_S = len(np.ma.getdata(channel_info_s["ChannelFreq"]))
    N_X = len(np.ma.getdata(channel_info_x["ChannelFreq"]))

    bw_per_band_s = np.ma.getdata(channel_info_s["SampleRate"]).tolist()[0]/2
    bw_per_band_x = np.ma.getdata(channel_info_x["SampleRate"]).tolist()[0]/2

    S_bw = [N_S*bw_per_band_s]*len(time)
    X_bw = [N_X*bw_per_band_x]*len(time)

    # Collect everything into a dataframe
    df = pd.DataFrame({"YMDHM": time,
                       "Second": second,
                       "Source": source,
                       "Station1": stat1,
                       "Station2": stat2,
                       "Q_code_S": qualcode_s,
                       "Q_code_X": qualcode_x,
                       "S_u": u_s,
                       "S_v": v_s,
                       "X_u": u_x,
                       "X_v": v_x,
                       "S_SNR": S_SNR,
                       "X_SNR": X_SNR,
                       "S_bw": S_bw,
                       "X_bw": X_bw,
                       "int_time": int_time})

    # Sort out rows with too low quality
    df = df.loc[(df.Q_code_S.astype(int) > 5)]
    df = df.loc[(df.Q_code_X.astype(int) > 5)]

    df.reset_index(inplace=True)

    if save_to_csv:
        datapoints_csv = f"Generated from vgosDB: {dir.split('/')[-2]}\n" + df.to_csv(
            index=False)
        with open("data/derived/datapoints.csv", "w") as file:
            file.write(datapoints_csv)

    return df