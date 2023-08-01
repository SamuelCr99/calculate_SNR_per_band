from math import sqrt, log, e
import numpy as np
from utility.wrappers.data_wrapper import DataWrapper

def least_square_fit(source, model, config, data, band, ignored_stations):
    
    # Find the datapoints with the specified source
    data = data.get(source=source,ignored_stations=ignored_stations)
    
    band_letter = ["A","B","C","D","S","X"][band]

    SNR_meas_list = []
    SNR_pred_list = []
    station_list = []

    for _, point in data.iterrows():
        
        # Make sure all stations are added to station_list
        if point.Station1 not in station_list: 
            station_list.append(point.Station1)
            
        if point.Station2 not in station_list: 
            station_list.append(point.Station2)
        
        SEFD1 = config.get_SEFD(point.Station1,band)
        SEFD2 = config.get_SEFD(point.Station2,band)
            
        SNR_meas = point[f"{band_letter}_SNR"]
        SNR_bit_meas = SNR_meas / sqrt(2*point.int_time*point[f"{band_letter}_bw"])
        SNR_meas_list.append(SNR_bit_meas)

        u = getattr(point,f"{band_letter}_u")
        v = getattr(point,f"{band_letter}_v")

        flux_pred = model.get_flux(u,v)
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
                N_ij = len(data.get(station=station_list[i]))
            else:
                N_ij = len(data.get(baseline=[station_list[i],station_list[j]]))
            N_i.append(N_ij)
        N.append(N_i)

        B_i = 0
        for _, point in data.get(station=station_list[i]).iterrows():
            B_i += log(point.SNR_pred/point.SNR_meas)
        B.append([B_i])

    N = np.mat(N)
    B = np.mat(B)
    P = (np.linalg.inv(N)*B).tolist()
    A = list(map(lambda p: e**(2*p[0]),P))

    for i in range(len(A)):
        station_SEFD = config.get_SEFD(station_list[i], band)
        config.set_SEFD(station_list[i], band, station_SEFD*A[i])
    
    return