from QuasarModel.tools import get_image_from_path as get_image
from QuasarModel.source_model import SourceModel as sm
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from astropy.io import fits
from math import radians,sin,cos,sqrt,pi,e
from plot_source import plot_source
from init import find_datapoints

# image = get_image("data/fits/J0029-0113_S_2004_04_30_yyk_map.fits")
# image = get_image("data/fits/J0022+0608_S_2018_11_18_pet_map.fits")
# data = fits.open("data/fits/J0022+0608_S_2018_11_18_pet_map.fits")[0]
# data = fits.open("data/fits/J0211-0145_C_2019_07_24_pet_map.fits")[0]
image = get_image("data/fits/J0136+4751_S_2021_01_27_pet_map.fits")
data = fits.open("data/fits/J0136+4751_S_2021_01_27_pet_map.fits")[0]
org, mdl, anl, gauss_list = sm().process(image)

gaussian = gauss_list[0]

a = gaussian.a
b = gaussian.b
t = gaussian.theta
x0 = gaussian.x0
y0 = gaussian.y0
A = gaussian.amp

delta_RA = radians(data.header["CDELT1"])
delta_dec = radians(data.header["CDELT2"])

num_points = 100

print(delta_RA)
print(delta_dec)
print(b)
print(image.shape[0])

# u_ls = list(map(lambda i: (i-num_points/2)/(num_points/2)*10**8, range(num_points)))*num_points
# v_ls = list(map(lambda i: (i-num_points/2)/(num_points/2)*10**8, range(num_points)))*num_points
# v_ls.sort()

# Get the measued values
station_information = pd.read_csv('data/derived/stations.csv')
source = "0133+476"
session_path = 'data/sessions/session1/'
data = find_datapoints(session_path)
u_mes, v_mes, flux_mes = plot_source(source, data, station_information=station_information, bands=[0], return_coords=True)

u_mod = list(map(lambda u: delta_RA*u, u_mes))
v_mod = list(map(lambda v: delta_dec*v, v_mes))

flux_pred = list(map(lambda u,v: abs(A*pi/sqrt(a*b)*e**(-2*pi*1j*(x0*u+y0*v) -pi**2/a*(u*cos(t)+v*sin(t))**2 -pi**2/b*(v*cos(t)-u*sin(t))**2)), u_mod, v_mod))
flux_ratio = list(map(lambda mes, pred: pred/mes, flux_mes, flux_pred))

s = 0
for p, m in zip(flux_pred, flux_mes):
    s += p/m

print(s/len(flux_pred))


plt.scatter(u_mes, v_mes,c=flux_ratio, s = 10)#, norm=matplotlib.colors.LogNorm())
plt.colorbar()
plt.show()

# num_points = 100
# u_ls = list(map(lambda i: (i-num_points/2)/(num_points/2), range(num_points)))*num_points
# v_ls = list(map(lambda i: (i-num_points/2)/(num_points/2), range(num_points)))*num_points
# v_ls.sort()

# Test 1

# us = list(range(512))*512
# vs = list(range(512))*512
# vs.sort()
# flux = list(map(lambda u,v: gaussian.get_fourier_transform_value(u,v,scale_factor=512), us, vs))

# plt.scatter(vs,us,c=flux)
# plt.colorbar()
# plt.show()

# Test 2

# data = fits.open("data/fits/J0211-0145_C_2019_07_24_pet_map.fits")[0]

# CRPIX1: Reference point in pixels for RA
# CRVAL1: Reference point in degrees for RA
# CDELT1: How many degrees of difference there are between pixels for RA
# CRPIX2: Reference point in pixels for dec
# CRVAL2: Reference point in degrees for dec
# CDELT2: How many degrees of difference there are between pixels for dec
# ref_pix_RA = data.header["CRPIX1"]
# ref_val_RA = data.header["CRVAL1"]
# delta_RA = data.header["CDELT1"]
# ref_pix_dec = data.header["CRPIX2"]
# ref_val_dec = data.header["CRVAL2"]
# delta_dec = data.header["CDELT2"]

# x = 0
# y = 0

# RA = ref_val_RA + (x - ref_pix_RA) * delta_RA
# dec = ref_val_dec + (y - ref_pix_dec) * delta_dec

# print(radians(RA), radians(dec))

# Test 3

# xs = list(range(512))*512
# ys = xs.copy()
# ys.sort()

# flux = list(map(lambda x, y: abs(
#     gaussian.get_fourier_transform_value(x, y, scale_factor=512)), xs, ys))

# RA = list(map(lambda x: radians(ref_val_RA + (x - ref_pix_RA) * delta_RA), xs))
# dec = list(map(lambda y: radians(ref_val_dec + (y - ref_pix_dec) * delta_dec), ys))

# plt.scatter(RA, dec, c=flux)
# plt.colorbar()
# plt.show()

# Test 4

#l = list(map(lambda x: radians(ref_val_RA + (x - ref_pix_RA) * delta_RA), xs))

# a=0.5
# b=2
# A=1
# x0=0
# y0=0
# t=pi/4

# num_points = 100
# u_ls = list(map(lambda i: (i-num_points/2)/(num_points/2), range(num_points)))*num_points
# v_ls = list(map(lambda i: (i-num_points/2)/(num_points/2), range(num_points)))*num_points
# v_ls.sort()

# flux = list(map(lambda u,v: abs(A*pi/sqrt(a*b)*e**(-2*pi*1j*(x0*u+y0*v) -pi**2/a*(u*cos(t)+v*sin(t))**2 -pi**2/b*(v*cos(t)-u*sin(t))**2)), u_ls, v_ls))

# plt.figure()
# plt.scatter(u_ls,v_ls,c=flux)
# plt.show()