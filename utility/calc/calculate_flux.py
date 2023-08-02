from math import sqrt


def calculate_flux(point, config):
    """
    Calculates the flux of an observation.

    Parameters:
    point(Series): The row describing the data point
    config(StationsConfigWrapper): A config containing all stations

    Returns:
    flux [int]: Flux density at the given point
    """

    # Constants to use
    int_time = point.int_time
    C = 0.617502
    stat1 = point.Station1
    stat2 = point.Station2

    band = point.band

    # Band-specific constants to use
    SNR = point.SNR
    band_width = point.bw
    SEFD1 = config.get_SEFD(stat1,band)
    SEFD2 = config.get_SEFD(stat2,band)

    # Equation for flux density
    return ((SNR * sqrt(SEFD1 * SEFD2)) / (C * sqrt(2*int_time*band_width)) if band_width != 0 else 0)

