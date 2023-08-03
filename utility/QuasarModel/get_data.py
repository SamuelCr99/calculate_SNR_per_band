from astropy.io import fits
from math import radians

def get_data(source_path):
    file = fits.open(source_path)
    table = file[1]
    data = table.data

    x = []
    y = []
    intensity = []
    for row in data:
        x.append(radians(row[1]))
        y.append(radians(row[2]))
        intensity.append(row[0])

    return x,y,intensity