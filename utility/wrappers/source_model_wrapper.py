from QuasarModel.tools import get_image_from_path as get_image
from QuasarModel.source_model import SourceModel as sm
from astropy.io import fits
from math import radians, pi, e, sin, cos, sqrt

class SourceModelWrapper:

    def __init__(self, path, scale=1, flux_scale=1):
        data = fits.open(path)[0]
        print(path)
        self.delta_u = radians(data.header["CDELT1"])
        self.delta_v = radians(data.header["CDELT2"])
        self.scale = scale
        self.flux_scale = flux_scale

        image = get_image(path)
        _, _, _, self.gauss_list = sm().process(image)

    def get_flux(self,u,v):
        u = -self.delta_u*u/self.scale
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

        return abs(flux)/self.flux_scale
    
    def set_flux_scale(self, source, stations, data, band, ignored_stations):
        # Find the datapoints with the specified source
        data = data.get(source=source,ignored_stations=ignored_stations)
        df = data.get_df()
        
        band_letter = ["A","B","C","D","S","X"][band]

        SNR_meas_list = []
        SNR_pred_list = []
        station_list = []

        for _, point in df.iterrows():
            
            # Make sure all stations are added to station_list
            if point.Station1 not in station_list: 
                station_list.append(point.Station1)
                
            if point.Station2 not in station_list: 
                station_list.append(point.Station2)
                
            SNR_meas = point[f"{band_letter}_SNR"]
            SNR_bit_meas = SNR_meas / sqrt(2*point.int_time*point[f"{band_letter}_bw"])
            SNR_meas_list.append(SNR_bit_meas)

            SEFD1 = float(stations.loc[stations["name"] == point.Station1][f"{band_letter}_SEFD"].iloc[0])
            SEFD2 = float(stations.loc[stations["name"] == point.Station2][f"{band_letter}_SEFD"].iloc[0])

            flux_pred = self.get_flux(point.u,point.v)
            SNR_bit_pred = 0.617502*flux_pred*sqrt(1/(SEFD1*SEFD2))
            SNR_pred_list.append(SNR_bit_pred)
        
        self.flux_scale = sum(list(map(lambda p,m: p/m, SNR_pred_list, SNR_meas_list)))/len(SNR_pred_list)