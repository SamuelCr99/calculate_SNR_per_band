from QuasarModel.tools import get_image_from_path as get_image
from QuasarModel.source_model import SourceModel as sm
import matplotlib.pyplot as plt
from astropy.io import fits
from math import radians

image = get_image("fits/J0029-0113_S_2004_04_30_yyk_map.fits")
# image = get_image("fits/J0022+0608_S_2018_11_18_pet_map.fits")
org, mdl, anl, gauss_list = sm().process(image)

gaussian = gauss_list[0]

# Test 1

# us = list(range(512))*512
# vs = list(range(512))*512
# vs.sort()
# flux = list(map(lambda u,v: gaussian.get_fourier_transform_value(u,v,scale_factor=512), us, vs))

# plt.scatter(vs,us,c=flux)
# plt.colorbar()
# plt.show()

# Test 2

data = fits.open("fits/J0211-0145_C_2019_07_24_pet_map.fits")[0]

# CRPIX1: Reference point in pixels for RA
# CRVAL1: Reference point in degrees for RA
# CDELT1: How many degrees of difference there are between pixels for RA
# CRPIX2: Reference point in pixels for dec
# CRVAL2: Reference point in degrees for dec
# CDELT2: How many degrees of difference there are between pixels for dec
ref_pix_RA = data.header["CRPIX1"]
ref_val_RA = data.header["CRVAL1"]
delta_RA = data.header["CDELT1"]
ref_pix_dec = data.header["CRPIX2"]
ref_val_dec = data.header["CRVAL2"]
delta_dec = data.header["CDELT2"]

# x = 0
# y = 0

# RA = ref_val_RA + (x - ref_pix_RA) * delta_RA
# dec = ref_val_dec + (y - ref_pix_dec) * delta_dec

# print(radians(RA), radians(dec))

# Test 3

xs = list(range(512))*512
ys = xs.copy()
ys.sort()

flux = list(map(lambda x, y: abs(
    gaussian.get_fourier_transform_value(x, y, scale_factor=512)), xs, ys))

RA = list(map(lambda x: radians(ref_val_RA + (x - ref_pix_RA) * delta_RA), xs))
dec = list(map(lambda y: radians(ref_val_dec + (y - ref_pix_dec) * delta_dec), ys))

plt.scatter(RA, dec, c=flux)
plt.colorbar()
plt.show()
