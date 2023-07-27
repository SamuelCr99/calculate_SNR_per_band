import pandas as pd
import mplcursors
import matplotlib.pyplot as plt
from math import sqrt
from find_index import find_index
from to_uv import convert_uv
from calculate_flux import calculate_flux
from init import find_datapoints

def plot_source(source, data, station_information, source_model = None, highlighted_stations = [], baseline="", ignored_stations=[], bands=[0, 1, 2, 3], return_coords = False):
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

    CMAP = "jet"

    ### Generate data ###

    # Change bands to a list if it was only given as a integer
    if not isinstance(bands, list):
        bands = [bands]

    # Find all observations that match the given criteria
    matches = find_index(
        source=source, df=data, baseline=baseline, ignored_stations=ignored_stations)
    
    baselines = []
    baselines2 = []
    coords_u = []
    coords_v = []
    flux = []
    ratio = []
    highlighted_u = []
    highlighted_v = []
    highlighted_flux = []
    highlighted_matches = []

    for band in bands:
        for point in matches:

            # For the A, B, C and D bands
            if band in [0,1,2,3]:
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

            # For the S and X bands
            else:
                band_letter = ["S","X"][band-4]
                u, v = data[f"{band_letter}_u"].iloc[point], data[f"{band_letter}_v"].iloc[point]

                coords_u.extend([u, -u])
                coords_v.extend([v, -v])

            # Calculate the flux at that point
            curr_flux = calculate_flux(point, data, station_information, band)
            flux.extend(curr_flux*2)

            if source_model:
                curr_ratio = source_model.get_flux(u,v)/curr_flux
                ratio.extend([curr_ratio]*2)

            # Find the baseline of that point
            baselines.extend(
                [f'{data.Station1.iloc[point]}-{data.Station2.iloc[point]} {list(map(lambda x: round(x,3), curr_flux))}']*2)
            
            if source_model:
                baselines2.extend(
                    [f'{data.Station1.iloc[point]}-{data.Station2.iloc[point]} {list(map(lambda x: round(x,3), curr_ratio))}']*2)


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

    if return_coords:
        with open(f"uv-flux{band_letter.capitalize()}.csv", "w") as file: 
            file.write(f"u,v,{band_letter}_flux\n")
            for u, v, f in zip(coords_u, coords_v, flux):
                file.write(f"{u},{v},{f}")
                file.write("\n")
        return coords_u, coords_v, flux
    
    ### Flux density (meas.) ###

    # Create figure and plot
    figure1 = plt.figure(0)
    figure1.clf()
    uv_plot = plt.scatter(coords_u, coords_v, c=flux, marker=".", vmin=0, cmap=CMAP)

    if len(highlighted_u):
        plt.scatter(highlighted_u,highlighted_v, marker='*', c = highlighted_flux, vmin=0, vmax=max(flux), s=50, cmap=CMAP)
    plt.colorbar(label="Flux density")

    # Adds arrows and annotations to all points
    uv_cursor = mplcursors.cursor(
        uv_plot, hover=mplcursors.HoverMode.Transient)
    uv_cursor.connect(
        "add", lambda sel: sel.annotation.set_text(baselines[sel.index]))
    
    # Add text
    plt.xlabel("U [fringes/radian]")
    plt.ylabel("V [fringes/radian]")
    bands_letters = list(map(lambda b: ["A","B","C","D","S","X"][b], bands))
    plt.figtext(
        0.95, 0.5, f'Number of points in plot: {len(coords_u)}', va="center", ha='center', rotation=90)
    plt.title(
        f"UV coordinates for source {source} for band{'s'*(len(bands)>1)} {', '.join(bands_letters)}")

    ### Flux density (pred.) ###

    if source_model and flux:
        figure2 = plt.figure(1)
        figure2.clf()

        num_points = 100
        max_u = max(coords_u)
        max_v = max(coords_v)

        coords_u_im = list(map(lambda u: (u/((num_points-1)/2)-1)*max_u, range(num_points)))
        coords_v_im = list(map(lambda v: (v/((num_points-1)/2)-1)*max_v, range(num_points)))

        u_delta = (coords_u_im[1] - coords_u_im[0])/2
        v_delta = (coords_v_im[1] - coords_v_im[0])/2

        extent = [coords_u_im[0]-u_delta, coords_u_im[-1]+u_delta, coords_v_im[0]-v_delta, coords_v_im[-1]+v_delta]

        flux_pred = []
        for i in range(num_points):
            row = []
            for j in range(num_points):
                row.append(source_model.get_flux(coords_u_im[i],coords_v_im[j]))
            flux_pred.append(row)
        
        plt.imshow(flux_pred, extent=extent, vmin=0, cmap=CMAP)
        plt.colorbar(label="Flux density")

         # Add text
        plt.xlabel("U [fringes/radian]")
        plt.ylabel("V [fringes/radian]")

    ### Flux density ratio ###

    if source_model:
        figure3 = plt.figure(2)
        figure3.clf()

        highlighted_ratio = list(map(lambda u,v,f: source_model.get_flux(u,v)/f, highlighted_u, highlighted_v, highlighted_flux))

        uv_plot = plt.scatter(coords_u, coords_v, c=ratio, marker=".", vmin=0, vmax=2, cmap=CMAP)

        if len(highlighted_u):
            plt.scatter(highlighted_u,highlighted_v, marker='*', c = highlighted_ratio, vmin=0, vmax=max(ratio), s=50, cmap=CMAP)
        plt.colorbar(label="Flux density ratio")

        # Adds arrows and annotations to all points
        uv_cursor = mplcursors.cursor(
            uv_plot, hover=mplcursors.HoverMode.Transient)
        uv_cursor.connect(
            "add", lambda sel: sel.annotation.set_text(baselines2[sel.index]))
        
        # Add text
        plt.xlabel("U [fringes/radian]")
        plt.ylabel("V [fringes/radian]")
        bands_letters = list(map(lambda b: ["A","B","C","D","S","X"][b], bands))
        plt.figtext(
            0.95, 0.5, f'Number of points in plot: {len(coords_u)}', va="center", ha='center', rotation=90)
        plt.title(
            f"UV coordinates for source {source} for band{'s'*(len(bands)>1)} {', '.join(bands_letters)}")

    ### Distance ###

    distance = list(map(lambda u, v: sqrt(u**2+v**2), coords_u, coords_v))
    highlighted_distance = list(map(lambda u, v: sqrt(u**2+v**2), highlighted_u, highlighted_v))

    # Create distance plot
    figure4 = plt.figure(3)
    figure4.clf()

    # Colors to use for the bands
    base_colors = ['blue', 'green', 'yellow', 'red', 'purple', 'orange']

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
            [], [], c=base_colors[b], label=f'Band {["A","B","C","D","S","X"][b]}'), bands)))

if __name__ == '__main__':
    station_information = pd.read_csv('data/derived/stations.csv')
    source = "0133+476"
    session_path = 'data/sessions/session1/'
    data = find_datapoints(session_path)

    plot_source(source, data, station_information=station_information, bands=[0])
    plt.show()