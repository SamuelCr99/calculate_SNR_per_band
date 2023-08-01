from math import sqrt


def calculate_flux(point, config, bands=[0, 1, 2, 3]):
    """
    Calculates the flux of an observation.

    Parameters:
    point(Series): The row describing the data point
    config(StationsConfigWrapper): A config containing all stations
    bands(int/list): The band/s to use (A=0, B=1...)

    Returns:
    list[float]: A list of the calculated fluxes for each band
    """

    # Change bands to a list if it was only given as a integer
    if not isinstance(bands, list):
        bands = [bands]

    # Constants to use
    int_time = point.int_time
    C = 0.617502
    stat1 = point.Station1
    stat2 = point.Station2

    flux = []

    for band in bands:
        band_letter = ["A","B","C","D","S","X"][band]

        # Band-specific constants to use
        SNR = point[f"{band_letter}_SNR"]
        band_width = point[f"{band_letter}_bw"]
        SEFD1 = config.get_SEFD(stat1,band)
        SEFD2 = config.get_SEFD(stat2,band)

        # Equation for flux density
        flux.append((SNR * sqrt(SEFD1 * SEFD2)) /
                    (C * sqrt(2*int_time*band_width)) if band_width != 0 else 0)

    return flux
