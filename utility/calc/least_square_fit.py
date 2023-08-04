from math import sqrt, log, e
import requests
import re
import numpy as np
from utility.wrappers.data_wrapper import DataWrapper
from utility.wrappers.source_model_wrapper import SourceModelWrapper
import os

def least_square_fit(data, model, config):
    """
    Fits the SEFD values of the selected band so they match with the model

    Will modify the provided config. Even though the data can contain more than
    one band, the function can only fit for one band. Can only fit the SEFD
    values for one source.

    Parameters:
    data(DataWrapper): All data points to consider
    model(dict/SourceModelWrapper): The model of the source
    config(StationsConfigWrapper): Contains the SEFD values of the stations

    Returns:
    No returns
    """
    if type(model) != dict:
        model = {data.get_df().Source.iloc[0]:model}

    SNR_meas_list = []
    SNR_pred_list = []
    station_list = []
    bands = list(set(data.get_df().band.tolist()))

    for band in bands:
        for _, point in data.iterrows():
            if point.Source not in model:
                continue

            # Add all stations to station_list
            if point.Station1 not in station_list: 
                station_list.append(point.Station1)
                
            if point.Station2 not in station_list: 
                station_list.append(point.Station2)
            
            SEFD1 = config.get_SEFD(point.Station1,band)
            SEFD2 = config.get_SEFD(point.Station2,band)
            
            # Get all the measured SNRs
            SNR_meas = point.SNR
            SNR_bit_meas = SNR_meas / sqrt(2*point.int_time*point.bw)
            SNR_meas_list.append(SNR_bit_meas)

            # Get all the predicted SNRs
            u = point.u
            v = point.v
            
            flux_pred = model[point.Source].get_flux(u,v)
            SNR_bit_pred = 0.617502*flux_pred*sqrt(1/(SEFD1*SEFD2))
            SNR_pred_list.append(SNR_bit_pred)

        # Add 2 new columns to dataframe
        data = DataWrapper(data.get_df().assign(SNR_meas=SNR_meas_list).assign(SNR_pred=SNR_pred_list))

        num_stations = len(station_list)
        
        N = []
        B = []

        for i in range(num_stations):
            N_i = []
            for j in range(num_stations):
                if i==j:
                    N_ij = len(data.get(stations=station_list[i]))
                else:
                    N_ij = len(data.get(baselines=[[station_list[i],station_list[j]]]))
                N_i.append(N_ij)
            N.append(N_i)

            B_i = 0
            for _, point in data.get(stations=station_list[i]).iterrows():
                B_i += log(point.SNR_pred/point.SNR_meas)
            B.append([B_i])

        N = np.mat(N)
        B = np.mat(B)
        P = (np.linalg.inv(N)*B).tolist()
        A = list(map(lambda p: e**(2*p[0]),P))

        # Update the SEFD values with the correction factor
        for i in range(len(A)):
            station_SEFD = config.get_SEFD(station_list[i], band)
            config.set_SEFD(station_list[i], band, station_SEFD*A[i])
    
    return

def model_source_map(data, dir):

    sources = list(map(lambda b1950_name: get_j2000_name(b1950_name), list(set(data.get_df().Sources.tolist()))))
    source_fits_dict = {}
    files = os.listdir(dir)
    
    for source in sources:
        for file in files:
            if source in file: 
                source_fits_dict[source] = SourceModelWrapper(f"{dir}/{file}")
                break
    return source_fits_dict

def get_j2000_name(b1950_name):
    base_url = f"http://astrogeo.org/cgi-bin/imdb_get_source.csh"
    params = {
        "source_name": b1950_name
    }

    response = requests.get(base_url,params=params)
    page = response.text

    j2000_name = re.findall(r'J\d\d\d\d[+-]\d\d\d\d',page)[0]
    return j2000_name
