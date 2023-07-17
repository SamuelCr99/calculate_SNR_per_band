from math import sqrt


def calculate_flux(index, general_data, station_data, bands=[0,1,2,3]):
    """
    Calculates the flux of a source at a given index in the data/datapoints.csv file.

    Parameters:
    index (int): The index of the source in the data/datapoints.csv file.

    Returns:
    list[float]: A list of the calculated fluxes for each band for the source at the given index.

    """
    if not isinstance(bands, list):
        bands = [bands]

    int_time = general_data.int_time.iloc[index]
    C = 1  # Currently assume C is always equal to 1

    stat1 = general_data.Station1.iloc[index]
    stat2 = general_data.Station2.iloc[index]

    SEFD1_X = float(
        station_data.X_SEFD.loc[station_data.name == stat1].iloc[0])
    SEFD2_X = float(
        station_data.X_SEFD.loc[station_data.name == stat2].iloc[0])
    SEFD1_S = float(
        station_data.S_SEFD.loc[station_data.name == stat1].iloc[0])
    SEFD2_S = float(
        station_data.S_SEFD.loc[station_data.name == stat2].iloc[0])

    flux = []

    for band in bands:
        if band == 0:
            SEFD1 = SEFD1_S
            SEFD2 = SEFD2_S
        else:
            SEFD1 = SEFD1_X
            SEFD2 = SEFD2_X

        band_letter = ["A","B","C","D"][band]

        SNR = general_data[f"{band_letter}_SNR"].iloc[index]
        band_width = general_data[f"{band_letter}_bw"].iloc[index]*10**6
        flux.append(SNR * sqrt(SEFD1 * SEFD2) / (C * sqrt(2*int_time*band_width)) if band_width != 0 else 0)

    return flux