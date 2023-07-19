import matplotlib.pyplot as plt
from find_index import find_index
from to_uv import convert_uv
import pandas as pd
import netCDF4 as nc
import numpy as np
from calculate_flux import calculate_flux
from math import sqrt
import mplcursors
from init import find_datapoints

FIG_COUNT = 1

def plot_source(source, data,baseline="",station_information = "", ignored_stations=[], bands=[0,1,2,3]):
    """
    Plots uv coordinates of a source at a given baseline.

    Parameters:
    source(string): The source to plot
    baseline(string): Baseline to observe the source at

    Returns:
    No return values!
    """

    global FIG_COUNT

    baseline_matches = find_index(source=source, df=data, baseline=baseline, ignored_stations=ignored_stations)
    baselines = []

    coords_u = []
    coords_v = []
    flux = []

    if not isinstance(bands, list):
        bands = [bands]

    for band in bands:
        for point in baseline_matches:
            u_orig, v_orig = data.u.iloc[point], data.v.iloc[point]
            ref_freq = data.ref_freq.iloc[point]

            if band == 0: freq = data.A_freq.iloc[point]
            elif band == 1: freq = data.B_freq.iloc[point]
            elif band == 2: freq = data.C_freq.iloc[point]
            elif band == 3: freq = data.D_freq.iloc[point]

            u, v = convert_uv(u_orig, v_orig, ref_freq, freq)

            coords_u.extend([u, -u])
            coords_v.extend([v, -v])

            curr_flux = calculate_flux(point, data, station_information, band)
            flux.extend(curr_flux*2)
            baselines.extend([f'{data.Station1.iloc[point]}-{data.Station2.iloc[point]} {list(map(lambda x: round(x,3), curr_flux))}']*2)
    coords_u = [u for u in coords_u if u == u]
    coords_v = [v for v in coords_v if v == v]
    if len(coords_u) == 0 or len(coords_v) == 0:
        return "no_data_found"

    # Only dots
    plt.figure(FIG_COUNT)
    FIG_COUNT += 1
    uv_plot = plt.scatter(coords_u, coords_v, c=flux, marker=".")
    uv_cursor = mplcursors.cursor(uv_plot,hover=mplcursors.HoverMode.Transient)

    uv_cursor.connect(
        "add", lambda sel: sel.annotation.set_text(baselines[sel.index]))
    plt.xlabel("U [lambda]")
    plt.ylabel("V [lambda]")
    plt.colorbar()
    bands_letters = list(map(lambda b: chr(ord('A')+b), bands))
    plt.figtext(
        0.95, 0.5, f'Number of points in plot: {len(coords_u)}', va="center", ha='center', rotation=90)
    plt.title(f"UV coordinates for source {source} for band{'s'*(len(bands)>1)} {', '.join(bands_letters)}")

    distance = list(map(lambda u,v: sqrt(u**2+v**2),coords_u,coords_v))
    plt.figure(FIG_COUNT)
    FIG_COUNT += 1
    base_colors = ['red', 'blue', 'green', 'yellow']
    if len(bands) > 1:
        colors = sum(list(map(lambda b: [base_colors[b]]*2*len(baseline_matches), bands)),[])
    else:
        colors = "black"
    flux_density_plot = plt.scatter(distance,flux, marker=".", c=colors)
    flux_cursor = mplcursors.cursor(flux_density_plot,hover=mplcursors.HoverMode.Transient)
    flux_cursor.connect(
        "add", lambda sel: sel.annotation.set_text(baselines[sel.index]))
    plt.xlabel("sqrt(U^2+V^2) [lambda]")
    plt.ylabel("Flux density")
    plt.title(f"Flux density vs. sqrt(U^2+V^2) for band{'s'*(len(bands)>1)} {', '.join(bands_letters)}")
    if len(bands) > 1:
        plt.legend(handles=list(map(lambda b: plt.scatter([],[], c=base_colors[b], label=f'Band {chr(ord("A")+b)}'), bands)))
    plt.show(block=False) 


if __name__ == '__main__':
    station_information = pd.read_csv('data/derived/stations.csv')
    source = "0016+731"
    session_path = 'data/sessions/19JUL24XA/'
    data = find_datapoints(session_path)

    plot_source(source, data, station_information=station_information,bands=3)
    plt.show()