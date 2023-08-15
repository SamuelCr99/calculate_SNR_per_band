from utility.QuasarModelImg.source_model import SourceModel as SourceModelImg
from utility.QuasarModelRaw.source_model import SourceModel as SourceModelRaw
from astropy.io import fits
from math import radians, pi, e, sin, cos, sqrt

class SourceModelWrapper:

    def __init__(self, path, scale_uv=1, scale_flux=1, model="img"):

        self.model = model
        self.name = path.split("/")[-1].split("\\")[-1].split(".")[0]

        if model == "img":
            data = fits.open(path)[0]
            self.delta_u = radians(data.header["CDELT1"])
            self.delta_v = radians(data.header["CDELT2"])
            sm = SourceModelImg()
        elif model == "raw":
            self.delta_u = 1
            self.delta_v = 1
            sm = SourceModelRaw()
        
        self.scale_uv = scale_uv
        self.scale_flux = scale_flux

        self.gauss_list = sm.process(path)

    def get_flux(self,u,v):
        u = self.delta_u*u/self.scale_uv
        v = self.delta_v*v/self.scale_uv

        # if self.model == "img":
        #     u,v = (v,u)

        flux = 0
        for gaussian in self.gauss_list:
            a = gaussian.a
            b = gaussian.b
            t = gaussian.theta
            x0 = gaussian.x0
            y0 = gaussian.y0
            A = gaussian.amp

            flux += A*pi/sqrt(a*b)*e**(-2*pi*1j*(x0*u+y0*v) -pi**2/a*(u*cos(t)+v*sin(t))**2 -pi**2/b*(v*cos(t)-u*sin(t))**2)

        return abs(flux)/self.scale_flux
    
    def set_flux_scale(self, config, data):
        self.scale_flux = 1

        SNR_meas_list = []
        SNR_pred_list = []
        station_list = []

        for _, point in data.iterrows():
            
            # Make sure all stations are added to station_list
            if point.Station1 not in station_list: 
                station_list.append(point.Station1)
                
            if point.Station2 not in station_list: 
                station_list.append(point.Station2)
                
            SNR_meas = point.SNR
            SNR_bit_meas = SNR_meas / sqrt(2*point.int_time*point.bw)
            SNR_meas_list.append(SNR_bit_meas)

            SEFD1 = config.get_SEFD(point.Station1,point.band)
            SEFD2 = config.get_SEFD(point.Station2,point.band)

            u = point.u
            v = point.v

            flux_pred = self.get_flux(u,v)
            SNR_bit_pred = 0.617502*flux_pred*sqrt(1/(SEFD1*SEFD2))
            SNR_pred_list.append(SNR_bit_pred)
        
        self.scale_flux = sum(list(map(lambda p,m: p/m, SNR_pred_list, SNR_meas_list)))/len(SNR_pred_list)