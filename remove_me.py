from QuasarModel.tools import get_image_from_path as get_image
from QuasarModel.source_model import SourceModel
from math import pi,e,sqrt,cos,sin,radians
from astropy.io import fits

#path = "data/fits/J0136+4751_S_2021_01_27_pet_map.fits"

# path = "data/fits/J1800+7828_S_2020_11_18_pet_map.fits"
# path = "data/fits/J2230+6946_S_2021_07_07_pet_map.fits"
# path = "data/fits/J0102+5824_S_2021_07_07_pet_map.fits"
# path = "data/fits/J1419+5423_S_2021_01_27_pet_map.fits"
path = "data/fits/J0617+5701_S_2017_09_06_pet_map.fits"

img = get_image(path)
raw = fits.open(path)[0]

flux_int = raw.header["FLUX_INT"]
total = sum(sum(img))
img = img*flux_int/total
# ref_pix = raw.header["CRPIX3"]
# ref_val = raw.header["CRVAL3"]
# ref_delta = raw.header["CDELT3"]

ref_delta_RA = raw.header["CDELT1"]
ref_delta_dec = raw.header["CDELT2"]

# print("Ref pix: ", ref_pix)
# print("Ref val: ", ref_val)
# print("Ref delta: ", ref_delta)

# k = ref_delta
# m = ref_val - ref_delta*ref_pix

# img = k*img + m

_,_,_,gauss_list = SourceModel().process(img)
gaussian = gauss_list[0]

a = gaussian.a
b = gaussian.b
t = gaussian.theta
x0 = gaussian.x0
y0 = gaussian.y0
A = gaussian.amp

flux = lambda u,v,: A*pi/sqrt(a*b)*e**(-2*pi*1j*(x0*u+y0*v) -pi**2/a*(u*cos(t)+v*sin(t))**2 -pi**2/b*(v*cos(t)-u*sin(t))**2)

print("Source:", path.split("/")[-1].split("_")[0], "for the S band on date", "/".join(path.split("/")[-1].split("_")[2:5]))
print("Angular spacing in RA (radians):", radians(ref_delta_RA))
print("Angular spacing in dec (radians):", radians(ref_delta_dec))
print("Sum of intensity of all pixels:", sum(sum(img)))
print("(Absolute-)Value of central point after FFT:", abs(flux(0,0)))
if(len(gauss_list)>1):
    print("WARNING - More than one gaussian available")
print("Gaussian:")
print("\ta =", a)
print("\tb =", b)
print("\ttheta =", t)
print("\tx0 =", x0)
print("\ty0 =", y0)
print("\tamp =", A)

# print("Amp: ", A)
# print("Flux at center:", abs(flux(0,0)))
# print(flux_int)