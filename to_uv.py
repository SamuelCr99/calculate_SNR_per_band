import math
import sys
from math import sin, cos, radians

def ElAz_to_HAdec2(el,az,lat,lon):
    dec = math.asin(math.sin(lat)*math.sin(el) + math.cos(lat)*math.cos(el)*math.cos(az))

    #HA1 = math.asin((-math.cos(el)*math.sin(az))/math.cos(dec))
    HA1 = math.acos(-(sin(el)*cos(lat)*cos(lon) - cos(el)*cos(az)*sin(lat)*cos(lon) - cos(el)*sin(az)*sin(lon))/cos(dec))
    HA2 = -HA1
    if HA2 > math.pi:
        HA2 -= 2*math.pi
    if HA2 < -math.pi:
        HA2 += 2*math.pi

    HA = [HA1,HA2]

    #f = lambda h: abs(math.cos(lat)*math.sin(el) - math.sin(lat)*math.cos(el)*math.cos(az) - math.cos(dec)*math.cos(h))
    f = lambda h: sin(el)*cos(lat)*sin(lon) - cos(el)*cos(az)*sin(lat)*sin(lon) - cos(el)*sin(az)*cos(lon) - cos(dec)*sin(h)

    a = [f(HA1),f(HA2)]
    i  = a.index(min(a))

    return math.degrees(HA[i]),math.degrees(dec)

def ElAz_to_HAdec(el,az,lat):
    # print(f'elevation: {el}')
    # print(f'azimuth: {az}')
    # print(f'latitude: {lat}')

    # el = math.radians(el)
    # az = math.radians(az)

    dec = math.asin(math.sin(lat)*math.sin(el) + math.cos(lat)*math.cos(el)*math.cos(az))

    HA1 = math.acos((math.cos(lat)*math.sin(el) - math.sin(lat)*math.cos(el)*math.cos(az))/ math.cos(dec))
    HA2 = -HA1
    if HA2 > math.pi:
        HA2 -= 2*math.pi
    if HA2 < -math.pi:
        HA2 += 2*math.pi

    HA = [HA1,HA2]

    f = lambda h: abs(-math.cos(el)*math.sin(az)-math.cos(dec)*math.sin(h))

    a = [f(HA1),f(HA2)]
    i  = a.index(min(a))

    return HA[i], dec
    

def to_spherical(x,y,z):
    # Turns cartesian coordinates to spherical. Theta goes from 0 to pi and
    # phi goes from -pi to pi
    if z == 0:
        theta = math.pi/2
    else:
        theta = math.atan(math.sqrt(x**2+y**2)/abs(z))
        if z < 0:
            theta = math.pi - theta
    if x == 0:
        if y > 0:
            phi = math.pi/2
        else:
            phi = -math.pi/2
    else:
        phi = math.atan(y/x)
        if x < 0:
            phi += math.pi
    
    while theta < 0:
        theta += 2*math.pi
    while theta > math.pi:
        theta -= 2*math.pi
    while phi < -math.pi:
        phi += 2*math.pi
    while phi > math.pi:
        phi -= 2*math.pi
    
    r = math.sqrt(x**2+y**2+z**2)

    return r,theta,phi

def to_cartesian(r,theta,phi):
    x = r*math.sin(theta)*math.cos(phi)
    y = r*math.sin(theta)*math.sin(phi)
    z = r*math.cos(theta)
    return x,y,z

def baseline_direction(lat1,lon1,lat2,lon2):

    x1,y1,z1 = to_cartesian(1,math.pi/2-lat1,lon1)
    x2,y2,z2 = to_cartesian(1,math.pi/2-lat2,lon2)

    dx = x2-x1
    dy = y2-y1
    dz = z2-z1

    if dz < 0:
        dx = -dx
        dy = -dy
        dz = -dz
    
    return dx,dy,dz

def to_uv(lon1,lat1,lon2,lat2,el,az):
    X,Y,Z = baseline_direction(lat1,lon1,lat2,lon2)
    H,delta = ElAz_to_HAdec(el,az,lat1)

    u = X*sin(H) + Y*cos(H)
    v = -X*cos(H) + Y*sin(H) + Z/math.tan(delta)

    return u,v

if __name__ == '__main__':
    to_uv(radians(-76.83), radians(39.02), radians(140.22), radians(36.21), 0.873, 6.202)