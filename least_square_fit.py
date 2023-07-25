from math import sqrt, log, e
import numpy as np

def least_square_fit(source, model, stations, data, band):
    
    data = data.loc[data.Source == source].copy(deep=True)
    band_letter = ["A","B","C","D","S","X"][band]

    SNR_meas_list = []
    SNR_pred_list = []
    station_list = []

    for _, point in data.iterrows():
        if point.Station1 not in station_list: 
            station_list.append(point.Station1)
            
        if point.Station2 not in station_list: 
            station_list.append(point.Station2)
            
        SNR_meas = point[f"{band_letter}_SNR"]
        SNR_bit_meas = SNR_meas / sqrt(2*point.int_time*point[f"{band_letter}_bw"])
        SNR_meas_list.append(SNR_bit_meas)

        SEFD1 = float(stations.loc[stations["name"] == point.Station1][f"{band_letter}_SEFD"].iloc[0])
        SEFD2 = float(stations.loc[stations["name"] == point.Station2][f"{band_letter}_SEFD"].iloc[0])

        flux_pred = model.get_flux(point.u,point.v)
        SNR_bit_pred = 1*flux_pred*sqrt(1/(SEFD1*SEFD2))
        SNR_pred_list.append(SNR_bit_pred)

    data["SNR_meas"] = SNR_meas_list
    data["SNR_pred"] = SNR_pred_list

    flux_scale = sum(list(map(lambda p,m: p/m, SNR_pred_list, SNR_meas_list)))/len(SNR_meas_list)
    SNR_pred_list = list(map(lambda snr: snr/flux_scale, SNR_pred_list))

    num_stations = len(station_list)
    
    N = []
    B = []

    for i in range(num_stations):
        N_i = []
        for j in range(num_stations):
            if i==j:
                N_ij = len(data.loc[(data.Station1 == station_list[i]) | (data.Station2 == station_list[i])])
            else:
                N_ij = len(data.loc[((data.Station1 == station_list[i]) & (data.Station2 == station_list[j])) | ((data.Station1 == station_list[j]) & (data.Station2 == station_list[i]))])

            N_i.append(N_ij)
        N.append(N_i)

        B_i = 0
        for _, point in data.loc[(data.Station1 == station_list[i]) | (data.Station2 == station_list[i])].iterrows():
            B_i += log(point.SNR_pred/point.SNR_meas)
        B.append([B_i])

    N = np.mat(N)
    B = np.mat(B)
    P = (np.linalg.inv(N)*B).tolist()
    A = list(map(lambda p: e**(2*p[0]),P))

    for i in range(len(A)):
        station_SEFD = float(stations.loc[stations.name == station_list[i],f"{band_letter}_SEFD"].iloc[0])
        stations.loc[stations.name == station_list[i],f"{band_letter}_SEFD"] = station_SEFD*A[i]

    
    return