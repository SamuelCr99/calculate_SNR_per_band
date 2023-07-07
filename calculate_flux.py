import pandas as pd
from math import sqrt


def calculate_flux(index):
    # This can be changed to return 8 values at once
    general_data = pd.read_csv('data/datapoints.csv')

    int_time = general_data.int_time.iloc[index]
    C = 1#general_data.C.iloc[index]
    SEFD1 = 1#general_data.SEFD1.iloc[index]
    SEFD2 = 1#general_data.SEFD2.iloc[index]

    A_SNR = general_data.A_SNR.iloc[index]
    A_band_width = general_data.A_bw.iloc[index]*10**6
    A_flux = A_SNR * sqrt(SEFD1 * SEFD2) / (C * sqrt(2*int_time*A_band_width))

    B_SNR = general_data.B_SNR.iloc[index]
    B_band_width = general_data.B_bw.iloc[index]*10**6
    B_flux = B_SNR * sqrt(SEFD1 * SEFD2) / (C * sqrt(2*int_time*B_band_width))

    C_SNR = general_data.C_SNR.iloc[index]
    C_band_width = general_data.C_bw.iloc[index]*10**6
    C_flux = C_SNR * sqrt(SEFD1 * SEFD2) / (C * sqrt(2*int_time*C_band_width))

    D_SNR = general_data.D_SNR.iloc[index]
    D_band_width = general_data.D_bw.iloc[index]*10**6
    D_flux = D_SNR * sqrt(SEFD1 * SEFD2) / (C * sqrt(2*int_time*D_band_width))

    return [A_flux, B_flux, C_flux, D_flux, A_flux, B_flux, C_flux, D_flux]



if __name__ == '__main__':
    calculate_flux(0, 0)