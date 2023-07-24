from QuasarModel.tools import get_image_from_path as get_image
from QuasarModel.source_model import SourceModel as sm
from astropy.io import fits
from math import radians, pi, e, sin, cos, sqrt

class SourceModel2:

    def __init__(self, path, scale=pi):
        data = fits.open(path)[0]
        print(path)
        self.delta_u = radians(data.header["CDELT1"])
        self.delta_v = radians(data.header["CDELT2"])
        self.scale = scale

        image = get_image(path)
        _, _, _, self.gauss_list = sm().process(image)

    def get_flux(self,u,v):
        u = self.delta_u*u/self.scale
        v = self.delta_v*v/self.scale

        flux = 0
        for gaussian in self.gauss_list:
            a = gaussian.a
            b = gaussian.b
            t = gaussian.theta
            x0 = gaussian.x0
            y0 = gaussian.y0
            A = gaussian.amp

            flux += A*pi/sqrt(a*b)*e**(-2*pi*1j*(x0*u+y0*v) -pi**2/a*(u*cos(t)+v*sin(t))**2 -pi**2/b*(v*cos(t)-u*sin(t))**2)
        
        return abs(flux)