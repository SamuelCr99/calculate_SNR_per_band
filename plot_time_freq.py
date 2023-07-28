import pandas as pd
import matplotlib.pyplot as plt

def convert_seconds(time_str):
    return int(time_str.split(":")[0])*3600 + int(time_str.split(":")[1])*60

df = pd.read_csv("2020-12-22-datapoints.csv")

freq = df["frequency"]
time = df["time"]
print(time)

time = list(map(lambda s: int(s.split(":")[0])*3600 + int(s.split(":")[1])*60, time))

plt.scatter(time, freq, s=10)
plt.xlabel("Time [s]")
plt.ylabel("Frequency [Hz]")
plt.show()
