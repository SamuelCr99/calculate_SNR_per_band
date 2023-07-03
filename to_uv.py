import math

def ElAz_to_HAdec(el,az,lat):
    dec = math.asin(math.sin(lat)*math.sin(el) + math.cos(lat)*math.cos(el)*math.cos(az))

    #HA1 = math.asin((-math.cos(el)*math.sin(az))/math.cos(dec))
    HA1 = math.acos((math.cos(lat)*math.sin(el) - math.sin(lat)*math.cos(el)*math.cos(az))/ math.cos(dec))
    HA2 = -HA1
    if HA2 > math.pi:
        HA2 -= 2*math.pi
    if HA2 < -math.pi:
        HA2 += 2*math.pi

    HA = [HA1,HA2]

    #f = lambda h: abs(math.cos(lat)*math.sin(el) - math.sin(lat)*math.cos(el)*math.cos(az) - math.cos(dec)*math.cos(h))
    f = lambda h: -math.cos(el)*math.sin(az)-math.cos(dec)*math.sin(h)

    a = [f(HA1),f(HA2)]
    i  = a.index(min(a))

    return math.degrees(HA[i]),math.degrees(dec)
    

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
    
    _,theta,phi = to_spherical(dx,dy,dz)

    HA = phi
    dec = math.pi/2 - theta

    return HA,dec

def to_uv(something):
    # First, get all of these nice variables
    D_lambda = 0
    lat1 = 0
    lon1 = 0
    lat2 = 0
    lon2 = 0
    el = 0
    az = 0

    h,d = baseline_direction(lat1,lon1,lat2,lon2)
    H,delta = ElAz_to_HAdec(el,az,lat1)

    u = D_lambda*math.cos(d)*math.sin(H-h)
    v = D_lambda*(math.sin(d)*math.cos(delta)-math.cos(d)*math.sin(delta)*math.cos(H-h))

    return u,v