import netCDF4 as nc
from to_uv import ElAz_to_HAdec
import math


def print_information():
    print(f'Azimuth for GGAO12M: {azimuthG[v][0]}')
    print(f'Elevation for GGAO12M: {elevationG[v][0]}')
    print(f'Latitude for GGAO12M: {latitudeG}')

    print(f'Azimuth for ISHIOKA: {azimuthI[w][0]}')
    print(f'Elevation for ISHIOKA: {elevationI[w][0]}')
    print(f'Latitude for ISHIOKA: {latitudeI}')


ggao12mDS = nc.Dataset('data/GGAO12M/AzEl_V001.nc', 'r')
# ggao12mDS = nc.Dataset('data/KOKEE12M/AzEl_V001.nc', 'r')
ishiokaDS = nc.Dataset('data/ISHIOKA/AzEl_V001.nc', 'r')

ggao12mTimeDS = nc.Dataset('data/GGAO12M/TimeUTC.nc', 'r')
# ggao12mTimeDS = nc.Dataset('data/KOKEE12M/TimeUTC.nc', 'r')
ishiokaTimeDS = nc.Dataset('data/ISHIOKA/TimeUTC.nc', 'r')

v = 19
w = 9
print(ggao12mTimeDS['YMDHM'][v], ggao12mTimeDS['Second'][v])
print('----------------')
print(ishiokaTimeDS['YMDHM'][w], ishiokaTimeDS['Second'][w])


azimuthG = ggao12mDS['AzTheo']
azimuthI = ishiokaDS['AzTheo']

elevationG = ggao12mDS['ElTheo']
elevationI = ishiokaDS['ElTheo']


latitudeG = math.radians(39.02)
# latitudeG = math.radians(22.13)
latitudeI = math.radians(36.21)

print_information()



print(ElAz_to_HAdec(elevationG[v][0],azimuthG[v][0],latitudeG))
print(ElAz_to_HAdec(elevationI[w][0],azimuthI[w][0],latitudeI))

