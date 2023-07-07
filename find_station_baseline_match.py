import pandas as pd

def find_station_baseline_match(source, baseline):
    df = pd.read_csv("data/datapoints.csv")
    station1 = baseline.split("/")[0]
    station2 = baseline.split("/")[1]

    matching_index = []

    for i, row in df.iterrows():
        if row["Source"] == source and row["Station1"] == station1 and row["Station2"] == station2:
            matching_index.append(i)
    return matching_index



if __name__ == '__main__':
    source = "1803+784"
    baseline = "GGAO12M/ISHIOKA"
    matching_stations = find_station_baseline_match(source,baseline)
    print(matching_stations)