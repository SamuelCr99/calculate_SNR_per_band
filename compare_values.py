import netCDF4 as nc
from to_uv import ElAz_to_HAdec, ElAz_to_HAdec2
import math

def normalize_angle(angle):
    while angle > 2*math.pi:
        ha1 -= 2*math.pi

    while angle < 0:
        angle += 2*math.pi
    return angle



def print_information():
    print(f'Azimuth for GGAO12M: {azimuthG[v][0]}')
    print(f'Elevation for GGAO12M: {elevationG[v][0]}')
    print(f'Latitude for GGAO12M: {latitudeG}')

    print(f'Azimuth for ISHIOKA: {azimuthI[w][0]}')
    print(f'Elevation for ISHIOKA: {elevationI[w][0]}')
    print(f'Latitude for ISHIOKA: {latitudeI}')

    print(f'Azimuth for KOKEE12M: {azimuthK[u][0]}')
    print(f'Elevation for KOKEE12M: {elevationK[u][0]}')
    print(f'Latitude for KOKEE12M: {latitudeK}')


ggao12mDS = nc.Dataset('data/GGAO12M/AzEl_V001.nc', 'r')
kokee12mDS = nc.Dataset('data/KOKEE12M/AzEl_V001.nc', 'r')
ishiokaDS = nc.Dataset('data/ISHIOKA/AzEl_V001.nc', 'r')

ggao12mTimeDS = nc.Dataset('data/GGAO12M/TimeUTC.nc', 'r')
kokee12mTimeDS = nc.Dataset('data/KOKEE12M/TimeUTC.nc', 'r')
ishiokaTimeDS = nc.Dataset('data/ISHIOKA/TimeUTC.nc', 'r')

v = 0
w = 0
u = 0
print(ggao12mTimeDS['YMDHM'][v], ggao12mTimeDS['Second'][v])
print('----------------')
print(kokee12mTimeDS['YMDHM'][w], kokee12mTimeDS['Second'][w])
print('----------------')
print(ishiokaTimeDS['YMDHM'][u], ishiokaTimeDS['Second'][u])


azimuthG = ggao12mDS['AzTheo']
azimuthK = kokee12mDS['AzTheo']
azimuthI = ishiokaDS['AzTheo']


elevationG = ggao12mDS['ElTheo']
elevationK = kokee12mDS['ElTheo']
elevationI = ishiokaDS['ElTheo']

latitudeG = math.radians(39.02)
latitudeK = math.radians(22.13)
latitudeI = math.radians(36.21)

longitudeG = math.radians(76.83)
longitudeK = math.radians(159.66)
longitudeI = math.radians(-140.22)
# longitudeI = math.radians(-219.78)

ha1, dec1 = ElAz_to_HAdec(elevationG[v][0],azimuthG[v][0],latitudeG)
ha2, dec2 = ElAz_to_HAdec(elevationK[w][0],azimuthK[w][0],latitudeK)
ha3, dec3 = ElAz_to_HAdec(elevationI[u][0],azimuthI[u][0],latitudeI)

ha1 += longitudeG
ha2 += longitudeK
ha3 += longitudeI

ha1 = normalize_angle(ha1)
ha2 = normalize_angle(ha2)
ha3 = normalize_angle(ha3)

print(ha1, ha2, ha3)