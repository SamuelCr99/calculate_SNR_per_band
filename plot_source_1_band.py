import matplotlib.pyplot as plt
from find_index import find_index_of_source_baseline, find_index_of_source, find_index_of_source_ignore_stations
from to_uv import convert_uv
import pandas as pd
import netCDF4 as nc
import numpy as np
from calculate_flux import calculate_flux
from math import sqrt

FIG_COUNT = 1

def plot_source(source, baseline, dir, ignored_stations, band):
    """
    Plots uv coordinates of a source at a given baseline.

    Parameters:
    source(string): The source to plot
    baseline(string): Baseline to observe the source at

    Returns:
    No return values!
    """

    global FIG_COUNT

    if dir[-1] != '/': dir += '/'

    ref_freq = np.ma.getdata(nc.Dataset(
        f'{dir}Observables/RefFreq_bX.nc', 'r')["RefFreq"]).tolist()[0]
    uv_data = np.ma.getdata(nc.Dataset(
        f'{dir}ObsDerived/UVFperAsec_bX.nc', 'r')['UVFperAsec']).tolist()
    data = pd.read_csv("data/derived/datapoints.csv", skiprows=1)
    station_data = pd.read_csv('data/derived/stations.csv')

    # baseline_matches = find_index_of_source_baseline(source, baseline)
    # baseline_matches = find_index_of_source(source)
    baseline_matches = find_index_of_source_ignore_stations(source, ignored_stations)

    coords_u = []
    coords_v = []
    flux = []

    for point in baseline_matches:
        u_orig, v_orig = uv_data[point][0]*206264.81, uv_data[point][1]*206264.81

        if band == 0: freq = data.A_freq.iloc[point]
        elif band == 1: freq = data.B_freq.iloc[point]
        elif band == 2: freq = data.C_freq.iloc[point]
        elif band == 3: freq = data.D_freq.iloc[point]

        u, v = convert_uv(u_orig, v_orig, ref_freq, freq)

        coords_u.extend([u, -u])
        coords_v.extend([v, -v])

        flux.extend(calculate_flux(point, data, station_data, band))

    # Only dots
    plt.figure(FIG_COUNT)
    FIG_COUNT += 1
    plt.scatter(coords_u, coords_v, c=flux, marker=".")
    plt.xlabel("U [lambda]")
    plt.ylabel("V [lambda]")
    plt.colorbar()
    plt.figtext(
        0.95, 0.5, f'Number of points in plot: {len(coords_u)}', va="center", ha='center', rotation=90)
    plt.title(f"UV coordinates for source {source} for band {chr(ord('A')+band)}")

    distance = list(map(lambda u,v: sqrt(u**2+v**2),coords_u,coords_v))
    plt.figure(FIG_COUNT)
    FIG_COUNT += 1
    plt.scatter(distance,flux, marker=".", c='black')
    plt.xlabel("sqrt(U^2+V^2) [lambda])")
    plt.ylabel("Flux")
    plt.title(f"Flux vs. sqrt(U^2+V^2) for band {chr(ord('A')+band)}")
    plt.show(block=False)


if __name__ == '__main__':
    source = "1803+784"
    baseline = "GGAO12M/ISHIOKA"
    session_path = 'data/sessions/session1/'

    if "/" not in session_path:
        session_path = f"data/sessions/{session_path}/"
    elif session_path[-1] != "/":
        session_path += "/"

    plot_source(source, baseline, session_path, [], 0)