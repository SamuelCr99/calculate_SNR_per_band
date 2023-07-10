import matplotlib.pyplot as plt
from find_index import find_index_of_source_baseline, find_index_of_source
from to_uv import convert_uv
import pandas as pd
import netCDF4 as nc
import numpy as np
from calculate_flux import calculate_flux
import time
from math import sqrt



def plot_source(source, baseline, dir):
    """
    Plots uv coordinates of a source at a given baseline.

    Parameters:
    source(string): The source to plot
    baseline(string): Baseline to observe the source at

    Returns:
    No return values!
    """

    start = time.time()

    ref_freq = np.ma.getdata(nc.Dataset(
        f'{dir}Observables/RefFreq_bX.nc', 'r')["RefFreq"]).tolist()[0]
    uv_data = np.ma.getdata(nc.Dataset(
        f'{dir}ObsDerived/UVFperAsec_bX.nc', 'r')['UVFperAsec']).tolist()
    data = pd.read_csv("data/derived/datapoints.csv", skiprows=1)
    station_data = pd.read_csv('data/derived/stations.csv')

    baseline_matches = find_index_of_source_baseline(source, baseline)
    baseline_matches = find_index_of_source(source)

    coords_u = []
    coords_v = []
    flux = []

    for point in baseline_matches:
        u_orig, v_orig = uv_data[point][0]*206264.81, uv_data[point][1]*206264.81

        A_freq = data.A_freq.iloc[point]
        B_freq = data.B_freq.iloc[point]
        C_freq = data.C_freq.iloc[point]
        D_freq = data.D_freq.iloc[point]

        u_A, v_A = convert_uv(u_orig, v_orig, ref_freq, A_freq)
        u_B, v_B = convert_uv(u_orig, v_orig, ref_freq, B_freq)
        u_C, v_C = convert_uv(u_orig, v_orig, ref_freq, C_freq)
        u_D, v_D = convert_uv(u_orig, v_orig, ref_freq, D_freq)

        coords_u.extend([u_A, u_B, u_C, u_D, -u_A, -u_B, -u_C, -u_D])
        coords_v.extend([v_A, v_B, v_C, v_D, -v_A, -v_B, -v_C, -v_D])
        

        flux.extend(calculate_flux(point, data, station_data))

    # Only dots
    print(f"Time taken: {time.time() - start} seconds")

    plt.figure(1)
    plt.scatter(coords_u, coords_v, c=flux, marker=".")
    plt.figtext(
        0.95, 0.5, f'Number of points in plot: {len(coords_u)}', va="center", ha='center', rotation=90)

    distance = list(map(lambda u,v: sqrt(u**2+v**2),coords_u,coords_v))
    plt.figure(2)
    plt.scatter(distance,flux, marker=".")
    
    plt.show()


if __name__ == '__main__':
    source = "1803+784"
    baseline = "GGAO12M/ISHIOKA"
    session_path = 'data/sessions/session1/'

    if "/" not in session_path:
        session_path = f"data/sessions/{session_path}/"
    elif session_path[-1] != "/":
        session_path += "/"

    plot_source(source, baseline, session_path)
