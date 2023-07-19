import pandas as pd
import mplcursors
import matplotlib.pyplot as plt
from math import sqrt
from find_index import find_index
from to_uv import convert_uv
from calculate_flux import calculate_flux
from init import find_datapoints

FIG_COUNT = 1


def plot_source(source, data, station_information, baseline="", ignored_stations=[], bands=[0, 1, 2, 3]):
    """
    Plots uv coordinates of a source

    Can select for specific baseline or specific bands. Can also exclude
    specific stations.

    Parameters:
    source(string): The source to plot
    data(DataFrame): The DataFrame to search through
    station_information(): A DataFrame containing information about the stations
    baseline(string): Baseline to observe the source at
    ignored_stations(list): A list of stations to ignore
    bands(list): The bands to consider (A=0, B=1...)

    Returns:
    No return values!
    """

    global FIG_COUNT

    ### Generate data ###

    # Change bands to a list if it was only given as a integer
    if not isinstance(bands, list):
        bands = [bands]

    # Find all observations that match the given criteria
    matches = find_index(
        source=source, df=data, baseline=baseline, ignored_stations=ignored_stations)
    
    baselines = []
    coords_u = []
    coords_v = []
    flux = []

    for band in bands:
        for point in matches:
            u_orig, v_orig = data.u.iloc[point], data.v.iloc[point]
            ref_freq = data.ref_freq.iloc[point]

            # Get the frequency of the band
            if band == 0:
                freq = data.A_freq.iloc[point]
            elif band == 1:
                freq = data.B_freq.iloc[point]
            elif band == 2:
                freq = data.C_freq.iloc[point]
            elif band == 3:
                freq = data.D_freq.iloc[point]
                
            if freq == None: 
                continue

            # Convert the old coordinates to the ones for the given band
            u, v = convert_uv(u_orig, v_orig, ref_freq, freq)

            coords_u.extend([u, -u])
            coords_v.extend([v, -v])

            # Calculate the flux at that point
            curr_flux = calculate_flux(point, data, station_information, band)
            flux.extend(curr_flux*2)

            # Find the baseline of that point
            baselines.extend(
                [f'{data.Station1.iloc[point]}-{data.Station2.iloc[point]} {list(map(lambda x: round(x,3), curr_flux))}']*2)

    # Remove NaN values
    coords_u = [u for u in coords_u if u == u]
    coords_v = [v for v in coords_v if v == v]

    # Make sure we are plotting something
    if len(coords_u) == 0 or len(coords_v) == 0:
        return "no_data_found"

    ### Scatter plot ###

    # Create figure and plot
    plt.figure(FIG_COUNT)
    FIG_COUNT += 1
    uv_plot = plt.scatter(coords_u, coords_v, c=flux, marker=".")

    # Adds arrows and annotations to all points
    uv_cursor = mplcursors.cursor(
        uv_plot, hover=mplcursors.HoverMode.Transient)
    uv_cursor.connect(
        "add", lambda sel: sel.annotation.set_text(baselines[sel.index]))
    
    # Add text
    plt.xlabel("U [lambda]")
    plt.ylabel("V [lambda]")
    plt.colorbar()
    bands_letters = list(map(lambda b: chr(ord('A')+b), bands))
    plt.figtext(
        0.95, 0.5, f'Number of points in plot: {len(coords_u)}', va="center", ha='center', rotation=90)
    plt.title(
        f"UV coordinates for source {source} for band{'s'*(len(bands)>1)} {', '.join(bands_letters)}")

    distance = list(map(lambda u, v: sqrt(u**2+v**2), coords_u, coords_v))

    ### Distance plot ###

    # Create distance plot
    plt.figure(FIG_COUNT)
    FIG_COUNT += 1

    # Colors to use for the bands
    base_colors = ['red', 'blue', 'green', 'yellow']

    # If there are multiple bands shown they should be color coded
    if len(bands) > 1:
        colors = sum(
            list(map(lambda b: [base_colors[b]]*2*len(matches), bands)), [])
    else:
        colors = "black"
    
    # Plot
    distance_plot = plt.scatter(distance, flux, marker=".", c=colors)
    
    # Adds arrows and annotations to the points
    distance_cursor = mplcursors.cursor(
        distance_plot, hover=mplcursors.HoverMode.Transient)
    distance_cursor.connect(
        "add", lambda sel: sel.annotation.set_text(baselines[sel.index]))
    
    # Add text
    plt.xlabel("sqrt(U^2+V^2) [lambda]")
    plt.ylabel("Flux density")
    plt.title(
        f"Flux density vs. sqrt(U^2+V^2) for band{'s'*(len(bands)>1)} {', '.join(bands_letters)}")
    
    # If multiple bands are plotted there need the be a legend to explain different
    # colors
    if len(bands) > 1:
        # Create empty scatter plots so the legend will be added correctly
        plt.legend(handles=list(map(lambda b: plt.scatter(
            [], [], c=base_colors[b], label=f'Band {chr(ord("A")+b)}'), bands)))

    # Show the plots
    plt.show(block=False)


if __name__ == '__main__':
    station_information = pd.read_csv('data/derived/stations.csv')
    source = "0016+731"
    session_path = 'data/sessions/19JUL24XA/'
    data = find_datapoints(session_path)

    plot_source(source, data, station_information=station_information, bands=3)
    plt.show()
