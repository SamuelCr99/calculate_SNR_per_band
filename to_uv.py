from math import sin, cos, radians, asin, acos, pi

def ElAz_to_RAdec(el,az,lat,lon):
    """
    Converts elevation and azimuth to right ascension and declination

    Parameters:
    el (float): Elevation in radians
    az (float): Azimuth in radians
    lat (float): Latitude in radians
    lon (float): Longitude in radians

    Returns:
    RA (float): Right ascension in radians
    dec (float): Declination in radians
    
    """

    dec = asin(sin(lat)*sin(el) + cos(lat)*cos(el)*cos(az))

    RA1 = acos(-(sin(el)*cos(lat)*cos(lon) - cos(el)*cos(az)*sin(lat)*cos(lon) - cos(el)*sin(az)*sin(lon))/cos(dec))
    RA2 = 2*pi-RA1
    RA = [RA1,RA2]

    f = lambda h: abs(sin(el)*cos(lat)*sin(lon) - cos(el)*cos(az)*sin(lat)*sin(lon) - cos(el)*sin(az)*cos(lon) - cos(dec)*sin(h))

    a = [f(RA1),f(RA2)]
    i  = a.index(min(a))

    return RA[i],dec

def ElAz_to_HAdec(el,az,lat):
    """
    Converts elevation and azimuth to hour angle and declination

    Parameters:
    el (float): Elevation in radians
    az (float): Azimuth in radians
    lat (float): Latitude in radians

    Returns:
    HA (float): Hour angle in radians
    dec (float): Declination in radians
    """

    dec = asin(sin(lat)*sin(el) + cos(lat)*cos(el)*cos(az))

    HA1 = acos((cos(lat)*sin(el) - sin(lat)*cos(el)*cos(az))/cos(dec))
    HA2 = 2*pi-HA1
    HA = [HA1,HA2]

    f = lambda h: abs(-cos(el)*sin(az)-cos(dec)*sin(h))

    a = [f(HA1),f(HA2)]
    i  = a.index(min(a))

    return HA[i], dec

def to_uv(lon,lat,X1,Y1,Z1,X2,Y2,Z2,el,az,freq,alg=0):
    """
    Convert a set of coordinates to u-v coordinates

    Paramters:
    lon(float): Longitude of one station
    lat(float): Latitude of one station
    X1(float): X-coordinate of one station
    Y1(float): Y-coordinate of one station
    Z1(float): Z-coordinate of one station
    X2(float): X-coordinate of another station
    Y2(float): Y-coordinate of another station
    Z2(float): Z-coordinate of another station
    el(float): Elevation of one station
    az(float): Azimuth of one station
    freq(float): Frequency of the band. Used to normalize vectors
    alg(int): Algorithm to use. Either 0 or 1

    Returns:
    u(float): u-coordinate
    v(float): v-coordinate
    """

    omega = 299792458/freq
    X1,Y1,Z1,X2,Y2,Z2 = X1/omega,Y1/omega,Z1/omega,X2/omega,Y2/omega,Z2/omega

    X = X1-X2
    Y = Y1-Y2
    Z = Z1-Z2
    
    if alg == 0:
        RA,dec = ElAz_to_RAdec(el,az,lat,-lon)
        u = -X*sin(RA) - Y*cos(RA)
        v = X*sin(dec)*cos(RA) - Y*sin(dec)*sin(RA) + Z*cos(dec)
    else:
        HA,dec = ElAz_to_HAdec(el,az,lat)
        RA = HA + lon
        u = X*sin(RA) -Y*cos(RA)
        v = -X*cos(RA) + Y*sin(RA) + Z*cos(dec)

    return u,v

def convert_uv(u,v,orig_freq,new_freq):
    # Rescales u-v coordinates from one frequency to another
    orig_omega = 299792458/orig_freq
    new_omega = 299792458/new_freq

    return u*orig_omega/new_omega, v*orig_omega/new_omega

if __name__ == '__main__':
    to_uv(radians(-76.83), radians(39.02), radians(140.22), radians(36.21), 0.873, 6.202)