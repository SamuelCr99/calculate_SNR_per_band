import pandas as pd
import mplcursors
import matplotlib.pyplot as plt
from math import sqrt
from find_index import find_index
from to_uv import convert_uv
from calculate_flux import calculate_flux
from init import find_datapoints

def plot_source(source, data, station_information, highlighted_stations = [], baseline="", ignored_stations=[], bands=[0, 1, 2, 3]):
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
    highlighted_u = []
    highlighted_v = []
    highlighted_flux = []
    highlighted_matches = []

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


            if len(highlighted_stations) == 1 and (data.Station1.iloc[point] in highlighted_stations or data.Station2.iloc[point] in highlighted_stations):
                if point not in highlighted_matches: highlighted_matches.append(point)
                highlighted_u.extend([u,-u])
                highlighted_v.extend([v,-v])
                highlighted_flux.extend(curr_flux*2)

            elif data.Station1.iloc[point] in highlighted_stations and data.Station2.iloc[point] in highlighted_stations: 
                if point not in highlighted_matches: highlighted_matches.append(point)
                highlighted_u.extend([u,-u])
                highlighted_v.extend([v,-v])
                highlighted_flux.extend(curr_flux*2)

    # Remove NaN values
    coords_u = [u for u in coords_u if u == u]
    coords_v = [v for v in coords_v if v == v]

    ### Scatter plot ###

    # Create figure and plot
    figure1 = plt.figure(0)
    figure1.clf()
    uv_plot = plt.scatter(coords_u, coords_v, c=flux, marker=".", vmin=0, cmap='jet')

    if len(highlighted_u):
        plt.scatter(highlighted_u,highlighted_v, marker='*', c = highlighted_flux, vmin=0, vmax=max(flux), s=50, cmap='jet')
    plt.colorbar(label="Flux density")

    # Adds arrows and annotations to all points
    uv_cursor = mplcursors.cursor(
        uv_plot, hover=mplcursors.HoverMode.Transient)
    uv_cursor.connect(
        "add", lambda sel: sel.annotation.set_text(baselines[sel.index]))
    
    # Add text
    plt.xlabel("U [fringes/radian]")
    plt.ylabel("V [fringes/radian]")
    bands_letters = list(map(lambda b: chr(ord('A')+b), bands))
    plt.figtext(
        0.95, 0.5, f'Number of points in plot: {len(coords_u)}', va="center", ha='center', rotation=90)
    plt.title(
        f"UV coordinates for source {source} for band{'s'*(len(bands)>1)} {', '.join(bands_letters)}")

    ### Distance plot ###
    distance = list(map(lambda u, v: sqrt(u**2+v**2), coords_u, coords_v))
    highlighted_distance = list(map(lambda u, v: sqrt(u**2+v**2), highlighted_u, highlighted_v))

    # Create distance plot
    figure2 = plt.figure(1)
    figure2.clf()

    # Colors to use for the bands
    base_colors = ['blue', 'green', 'yellow', 'red']

    # If there are multiple bands shown they should be color coded
    if len(bands) > 1:
        colors = sum(
            list(map(lambda b: [base_colors[b]]*2*len(matches), bands)), [])
        highlighted_colors = sum(
            list(map(lambda b: [base_colors[b]]*2*len(highlighted_matches), bands)), [])
    else:
        colors = "black"
        highlighted_colors = "black"
    # Plot
    distance_plot = plt.scatter(distance, flux, marker=".", c=colors)
    if len(highlighted_u):
        plt.scatter(highlighted_distance,highlighted_flux, marker='*', s=50, c=highlighted_colors)
    
    # Adds arrows and annotations to the points
    distance_cursor = mplcursors.cursor(
        distance_plot, hover=mplcursors.HoverMode.Transient)
    distance_cursor.connect(
        "add", lambda sel: sel.annotation.set_text(baselines[sel.index]))
    
    # Add text
    plt.xlabel("sqrt(U^2+V^2) [fringes/radian]")
    plt.ylabel("Flux density")
    plt.title(
        f"Flux density vs. sqrt(U^2+V^2) for band{'s'*(len(bands)>1)} {', '.join(bands_letters)}")
    
    # If multiple bands are plotted there need the be a legend to explain different
    # colors
    if len(bands) > 1:
        # Create empty scatter plots so the legend will be added correctly
        plt.legend(handles=list(map(lambda b: plt.scatter(
            [], [], c=base_colors[b], label=f'Band {chr(ord("A")+b)}'), bands)))
    
    # return figure1, figure2


if __name__ == '__main__':
    station_information = pd.read_csv('data/derived/stations.csv')
    source = "1803+784"
    session_path = 'data/sessions/session1/'
    data = find_datapoints(session_path)

    plot_source(source, data, station_information=station_information, bands=[0,1,2,3], highlighted_stations=["WESTFORD", "ISHIOKA"])
    plt.show()
