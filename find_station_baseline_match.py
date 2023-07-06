import pandas as pd
import math
import netCDF4 as nc
import numpy as np
from to_uv import to_uv


def compare_time(row_time, db_time, row_second, db_second):
    if row_second != db_second:
        return False

    row_time = row_time.replace('-', '/')
    row_time = row_time.replace(':', '/')
    row_time = row_time.split('/')
    row_time = [int(i) for i in row_time]
    row_time[0] += 2000

    for i in range(len(row_time)):
        if row_time[i] != db_time[i]:
            return False
    return True



# Read in the data
df = pd.read_csv('dump.txt', delim_whitespace=True, skiprows=4)
matching_rows = df.loc[(df['BASELINE'] == 'GGAO12M/ISHIOKA') & (df['SOURCE'] == '1803+784')]
matching_rows.reset_index(drop=True, inplace=True)

ggao12mDS = nc.Dataset('data/GGAO12M/AzEl_V001.nc', 'r')
ggao12mTimeDS = nc.Dataset('data/GGAO12M/TimeUTC.nc', 'r')
uv_data = nc.Dataset(f'data/ObsDerived/UVFperAsec_bX.nc', 'r')
uv_mes = np.ma.getdata(uv_data['UVFperAsec'])

lines_to_write = ['u,v']

for _, row in matching_rows.iterrows():
    for i in range(len(ggao12mTimeDS['YMDHM'])):
        time_stamp = ggao12mTimeDS['YMDHM'][i]
        if compare_time(row['YMDHM'], time_stamp, row['SECOND'], ggao12mTimeDS['Second'][i]):
            u, v = uv_mes[i][0]*206264.81, uv_mes[i][1]*206264.81
            lines_to_write.append(f'{u},{v}')

with open('ggao12m_baseline_match.txt', 'w') as f:
    for line in lines_to_write:
        f.write(f'{line}\n')