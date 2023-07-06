import pandas as pd
from to_uv import to_uv
import netCDF4 as nc
import numpy as np
from math import radians

uv_data = nc.Dataset(f'data/ObsDerived/UVFperAsec_bX.nc', 'r')
ref_freq_ds = nc.Dataset(f'data/Observables/RefFreq_bX.nc', 'r')
uv_mes = np.ma.getdata(uv_data['UVFperAsec'])
all_data = pd.read_csv("data/datapoints.csv")
stations = pd.read_csv("data/stations.csv")

i = 0
data = all_data.iloc[i]

ref_freq = np.ma.getdata(ref_freq_ds["RefFreq"]).tolist()[i]
el = data.El1
az = data.Az1
A_freq = data.A_freq
B_freq = data.B_freq
C_freq = data.C_freq
D_freq = data.D_freq
tot_freq = data.tot_freq

station = stations[stations.name == data.Station1]
station.reset_index(inplace=True)
lon = station.lon[0]
lat = station.lat[0]
x1 = station.x[0]
y1 = station.y[0]
z1 = station.z[0]

station2 = stations[stations.name == data.Station2]
station2.reset_index(inplace=True)
x2 = station2.x[0]
y2 = station2.y[0]
z2 = station2.z[0]

print(uv_mes[i])
u_theo,v_theo = to_uv(-radians(lon), radians(lat), x1, y1, z1, x2, y2, z2, el, az, ref_freq*10**6)
print(uv_mes[i][0]*206264.81, uv_mes[i][1]*206264.81)
print(u_theo,v_theo)