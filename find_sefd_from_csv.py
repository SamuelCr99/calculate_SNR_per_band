import pandas as pd

df = pd.read_csv("sefd-2023-07-24-V2.csv")

# date = []
# time = []

# for i, row in df.iterrows():
#     curr_date_time = row["date_time"]
#     date.append(curr_date_time.split(" ")[0])
#     time.append(curr_date_time.split(" ")[1])

# df["date"] = date
# df["time"] = time

# df.to_csv("qwe.csv", index = False)

df = df.loc[df["date"]=="2020-12-22"]
df.to_csv("2020-12-22-datapoints.csv", index=False)

Gs = df.loc[(df["station_code"] == "Gs") & (df["input"] == 1)]
K2 = df.loc[(df["station_code"] == "K2") & (df["input"] == 1)]
Mg = df.loc[(df["station_code"] == "Mg") & (df["input"] == 1)]
Oe = df.loc[(df["station_code"] == "Oe") & (df["input"] == 1)]
Ow = df.loc[(df["station_code"] == "Ow") & (df["input"] == 1)]

print(Gs.iloc[0]["SEFD"])
print(K2.iloc[0]["SEFD"])
print(Mg.iloc[0]["SEFD"])
print(Oe.iloc[0]["SEFD"])
print(Ow.iloc[0]["SEFD"])