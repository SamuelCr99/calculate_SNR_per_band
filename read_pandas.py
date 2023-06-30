import pandas as pd

df = pd.read_csv('dump.txt', delim_whitespace=True, skiprows=3)
print(df)