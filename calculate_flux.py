import netCDF4 as nc
import pandas as pd
from math import sqrt

corr_info = nc.Dataset(f'data/Observables/CorrInfo-difx_bX.nc', 'r')

integration_times = corr_info['EffectiveDuration']
SEFD1_times = []
SEFD2_times = []
c = 1
flux_values = []
SNR_values = []
BW = 1


for i in range(len(integration_times)):
    # flux_values.append(SNR_values[i]*sqrt(SEFD1_times[i]*SEFD2_times[i])/
    #                    sqrt(2*integration_times[i]*BW))


    pass

