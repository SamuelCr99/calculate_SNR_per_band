import pandas as pd
from math import sqrt, degrees


def calculate_flux(index, general_data, station_data):
    """
    Calculates the flux of a source at a given index in the data/datapoints.csv file.

    Pramaeters:
    index (int): The index of the source in the data/datapoints.csv file.

    Returns:
    list[float]: A list of the calculated fluxes for each band for the source at the given index.

    """

    int_time = general_data.int_time.iloc[index]
    C = 1  # Currently assume C is always equal to 1

    stat1 = general_data.Station1.iloc[index]
    stat2 = general_data.Station2.iloc[index]

    SEFD1_X = float(
        station_data.X_SEFD.loc[station_data.name == stat1].iloc[0])
    SEFD2_X = float(
        station_data.X_SEFD.loc[station_data.name == stat2].iloc[0])
    SEFD1_S = float(
        station_data.S_SEFD.loc[station_data.name == stat1].iloc[0])
    SEFD2_S = float(
        station_data.S_SEFD.loc[station_data.name == stat2].iloc[0])

    A_SNR = general_data.A_SNR.iloc[index]
    A_band_width = general_data.A_bw.iloc[index]*10**6
    A_flux = A_SNR * sqrt(SEFD1_S * SEFD2_S) / (C * sqrt(2*int_time*A_band_width))

    B_SNR = general_data.B_SNR.iloc[index]
    B_band_width = general_data.B_bw.iloc[index]*10**6
    B_flux = B_SNR * sqrt(SEFD1_X * SEFD2_X) / (C * sqrt(2*int_time*B_band_width))

    C_SNR = general_data.C_SNR.iloc[index]
    C_band_width = general_data.C_bw.iloc[index]*10**6
    C_flux = C_SNR * sqrt(SEFD1_X * SEFD2_X) / (C * sqrt(2*int_time*C_band_width))

    D_SNR = general_data.D_SNR.iloc[index]
    D_band_width = general_data.D_bw.iloc[index]*10**6
    D_flux = D_SNR * sqrt(SEFD1_X * SEFD2_X) / (C * sqrt(2*int_time*D_band_width))

    return [A_flux, B_flux, C_flux, D_flux, A_flux, B_flux, C_flux, D_flux]