from math import sin, cos, radians, asin, acos, pi

def ElAz_to_RAdec(el,az,lat,lon):
    dec = asin(sin(lat)*sin(el) + cos(lat)*cos(el)*cos(az))

    HA1 = acos(-(sin(el)*cos(lat)*cos(lon) - cos(el)*cos(az)*sin(lat)*cos(lon) - cos(el)*sin(az)*sin(lon))/cos(dec))
    HA2 = 2*pi-HA1
    HA = [HA1,HA2]

    f = lambda h: abs(sin(el)*cos(lat)*sin(lon) - cos(el)*cos(az)*sin(lat)*sin(lon) - cos(el)*sin(az)*cos(lon) - cos(dec)*sin(h))

    a = [f(HA1),f(HA2)]
    i  = a.index(min(a))

    return HA[i],dec

def ElAz_to_HAdec(el,az,lat):
    dec = asin(sin(lat)*sin(el) + cos(lat)*cos(el)*cos(az))

    HA1 = acos((cos(lat)*sin(el) - sin(lat)*cos(el)*cos(az))/cos(dec))
    HA2 = 2*pi-HA1
    HA = [HA1,HA2]

    f = lambda h: abs(-cos(el)*sin(az)-cos(dec)*sin(h))

    a = [f(HA1),f(HA2)]
    i  = a.index(min(a))

    return HA[i], dec

def to_uv(lon,lat,X1,Y1,Z1,X2,Y2,Z2,el,az,freq,alg=0):
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

if __name__ == '__main__':
    to_uv(radians(-76.83), radians(39.02), radians(140.22), radians(36.21), 0.873, 6.202)