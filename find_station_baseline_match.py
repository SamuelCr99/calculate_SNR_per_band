import pandas as pd

def find_index_of_source_baseline(source, baseline):
    df = pd.read_csv("data/datapoints.csv")
    station1 = baseline.split("/")[0]
    station2 = baseline.split("/")[1]
    return df.loc[(df.Source == source) & (df['Station1'] == station1) & (df['Station2'] == station2)].index.tolist()

def find_index_of_source(source):
    df = pd.read_csv("data/datapoints.csv")
    return df.loc[df.Source == source].index.tolist()

if __name__ == '__main__':
    source = "1803+784"
    baseline = "GGAO12M/ISHIOKA"
    matching_stations = find_index_of_source_baseline(source,baseline)
    print(matching_stations)